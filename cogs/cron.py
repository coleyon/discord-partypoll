import json
import os
import re
import shlex
from collections import namedtuple
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import aiofiles
import pytz
from croniter import croniter, CroniterBadCronError
from discord import Activity, ActivityType, File
from discord.ext import commands, tasks
from tabulate import tabulate
from discord.ext.commands import TextChannelConverter, ChannelNotFound
from log import get_logger

logger = get_logger("CronCog")
USERDATA_PATH = os.getenv("USERDATA_PATH", default="userdata.json")
Schedule = namedtuple(
    "Schedule", ("guild_id", "channel_id", "register_id", "cron", "command")
)
CMD_MAX_VISIBLE = 15
tabulate.WIDE_CHARS_MODE = True


class Cron(commands.Cog):
    """cron based task"""

    def __init__(self, bot):
        self.bot = bot
        self.timezone = os.getenv("TIMEZONE", default="Asia/Tokyo")

    def _now(self):
        return pytz.timezone(self.timezone).localize(dt.now())

    def _strftime(self, date):
        return date.strftime("%Y/%m/%d %H:%M")

    @commands.Cog.listener()
    async def on_ready(self):
        await self._load_userdata()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name=""), status=None
        )
        logger.info("{name} Extension Enabled.".format(name=self.__cog_name__))

    @commands.group()
    async def cron(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(":bulb: cron コマンドのマニュアルです。", file=File("helpfiles/cron.md"))

    @tasks.loop(minutes=1.0, reconnect=True)
    async def tick(self):
        current = self._now()
        for k, v in self.userdata.items():
            if croniter.match(v["schedule"], current):
                cmd = v["command"]
                ch = self.bot.get_channel(v["channel_id"])
                await ch.send(f"{cmd}")
                logger.debug(f"Runned `{cmd}`.")
        presence_type = ActivityType.listening
        await self.bot.change_presence(
            activity=Activity(type=presence_type, name="Cron"), status=None
        )
        logger.debug("tick")

    def IC(self, n):
        offset = re.sub(r"\{\{(\d+)\.days\}\}", r"\1", n)
        d = self._now() + relativedelta(days=int(offset))
        return d.strftime("%m/%d")

    def _dig(self, msg: list):
        '''get a command or sub-command instance and query from the message'''
        try:
            options = msg.copy()
            options[0] = options[0][1:]
            cmd = self.bot.all_commands[options.pop(0)]
            while True:
                cmd = cmd.all_commands[options.pop(0)]
                if isinstance(cmd, commands.core.Command):
                    break
            return [cmd, options]
        except BaseException as e:
            logger.error(f"Sub command digging failed, {e}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            if message.content.startswith(self.bot.command_prefix):
                ctx = await self.bot.get_context(message)
                replaced_message = re.sub(
                    r"\{\{(\d+)\.days\}\}",
                    lambda x: self.IC(x.group()),
                    message.content,
                )
                m = shlex.split(replaced_message)
                cmd = self._dig(m)
                if cmd:
                    await ctx.invoke(cmd[0], *cmd[1])

    @tick.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()

    @cron.command(name="disable")
    async def disable_cron(self, ctx):
        self.tick.cancel()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name=""), status=None
        )
        await ctx.channel.send(":white_check_mark: 自動実行を無効にしました。")
        logger.info("Cron disabled manually.")

    @cron.command(name="timezone")
    async def set_timezone(self, ctx, tz=None):
        if tz:
            if tz in pytz.all_timezones:
                self.timezone = tz
                await ctx.send(f"タイムゾーン {self.timezone} にセットしました。")
            else:
                await ctx.send(
                    f":x: 指定したタイムゾーン {tz} はありません。\n"
                    f":bulb: 指定できるタイムゾーンは https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 です。"
                )
        else:
            await ctx.send(f":bulb: 今のタイムゾーンは {self.timezone} です。")
            logger.info(f"Current timezone setting changed to {self.timezone}")

    @cron.command(name="enable")
    async def enable_cron(self, ctx):
        await self._load_userdata()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name="Cron"), status=None
        )
        self.tick.start()
        await ctx.channel.send(":white_check_mark: 自動実行を有効にしました。")
        logger.info("Cron enabled manually.")

    @cron.command(name="show")
    async def show_schedule(self, ctx, schedule_name=None):
        try:
            if schedule_name:
                # detail mode
                detail = self.userdata[schedule_name]["command"]
                await ctx.channel.send(f":bulb: スケジュール `{schedule_name}` によって実行されるコマンドは...\n`{detail}`\nです。")
            else:
                # summary mode
                headers = ["名前", "分", "時", "日", "月", "曜日", "コマンド"]
                table = []
                for k, v in self.userdata.items():
                    crontab = v["schedule"].split(" ")
                    shoten_cmd = "{c}...".format(c=v["command"][:CMD_MAX_VISIBLE]) if len(v["command"]) > CMD_MAX_VISIBLE else v["command"]
                    table.append([k, *crontab, shoten_cmd])
                formatted_description = tabulate(table, headers, tablefmt="simple")
                await ctx.channel.send(
                    f":bulb: {len(self.userdata)} 件のスケジュールが登録されています\n```{formatted_description}```"
                )
        except BaseException as e:
            logger.error(f"Showing schedule command failed, {e}.")

    @cron.command(name="del")
    async def delete_schedule(self, ctx, name):
        try:
            self.userdata.pop(name)
            await self._save_userdata()
            await ctx.send(f":white_check_mark: スケジュール `{name}` を除去しました。")
        except BaseException as e:
            logger.error(f"Deleting schedule command failed, {e}.")

    @cron.command(name="check")
    async def check_schedule(self, ctx):
        try:
            current = self._now()
            table = []
            for k, v in self.userdata.items():
                if ctx.guild.id != v["server_id"]:
                    continue
                try:
                    run_at = self._strftime(croniter(v["schedule"], current).get_next(dt))
                except CroniterBadCronError:
                    run_at = "無し"
                run_on = self.bot.get_channel(v["channel_id"])
                if not run_on:
                    run_on = "無し"
                author = await ctx.guild.fetch_member(v["author"])
                author_name = "不明"
                if author:
                    author_name = author.nick
                table.append([run_at, run_on, k, author_name])

            formatted_table = tabulate(table, ["次回実行日時", "実行先チャンネル", "スケジュール名", "登録した人"], tablefmt="simple")
            await ctx.send(f":bulb: 直近の実行タイミングは次の通りです。\n```{formatted_table}```")
        except BaseException as e:
            logger.error(f"Checking schedule command failed, {e}.")

    @cron.group(name="set")
    async def set_subcmd(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @set_subcmd.command(name="channel")
    async def set_channel(self, ctx, schedule_name, channel: TextChannelConverter = None):
        channel_id = None
        channel_name = None
        if channel:
            try:
                channel_id = channel.id
                channel_name = channel.name
            except ChannelNotFound:
                await ctx.send(":x: チャンネルが見つけられません。")
                return
        else:
            channel_id = ctx.channel.id
            channel_name = ctx.channel.name
        if schedule_name in self.userdata.keys():
            self.userdata[schedule_name]["channel_id"] = channel_id
            await self._save_userdata()
            await ctx.send(f":white_check_mark: `{schedule_name}` の実行先チャンネルを `{channel_name}` に変更しました。")
            logger.debug(f"{schedule_name} schedule running dest channel changed to {channel_name}.")
        else:
            await ctx.send(f":x: スケジュール `{schedule_name}` がありません。")
            logger.debug("Schedule running dest channel changing has failed.")

    @set_subcmd.command(name="schedule")
    async def set_schedule(self, ctx, schedule_name, m, h, dom, mon, dow):
        if schedule_name not in self.userdata.keys():
            await ctx.send(f":x: スケジュール `{schedule_name}` がありません。")
            return
        schedule = " ".join([m, h, dom, mon, dow])
        if croniter.is_valid(schedule):
            self.userdata[schedule_name]["schedule"] = schedule
            await self._save_userdata()
            await ctx.send(f":white_check_mark: `{schedule_name}` のスケジュールを `{schedule}` に変更しました。")
        else:
            await ctx.send(f":x: `{schedule}` は正しくありません。")

    @cron.command(name="add")
    async def add_schedule(self, ctx, name, m, h, dom, mon, dow, *cmd):
        crontab = " ".join([m, h, dom, mon, dow])
        escaped_cmds = None
        if not croniter.is_valid(crontab):
            await ctx.send(f":x: スケジュール `{crontab}` が不正です。")
        else:
            if not self._dig(list(cmd)):
                await ctx.send(":x: 他Botのコマンドまたは正しくないコマンドは定時実行ができないので登録しませんでした。")
                logger.debug("Specified command could not scheduled.")
                return
            escaped_cmds = " ".join((f'"{i}"' if " " in i else i for i in cmd))
            self.userdata[name] = {
                "command": escaped_cmds,
                "server_id": ctx.guild.id,
                "channel_id": ctx.channel.id,
                "author": ctx.message.author.id,
                "schedule": crontab,
            }
            await self._save_userdata()
            logger.debug("Specified command scheduled successfully.")
        next_run = self._strftime(croniter(crontab, self._now()).get_next(dt))
        await ctx.send(
            f":white_check_mark: スケジュール `{name}` を追加しました。\n"
            f"次回実行予定は {next_run} です。\n"
            f"実行されるコマンドは `{escaped_cmds}` です。"
        )

    @cron.command(name="load")
    async def upload_userdata(self, ctx):
        try:
            await ctx.message.attachments[0].save(fp=USERDATA_PATH)
            await self._load_userdata()
            await ctx.send(":white_check_mark: スケジュールをアップロードしました。")
            logger.debug(f"Uploaded file saved to {USERDATA_PATH}.")
        except BaseException as e:
            await ctx.send(":x: スケジュールをアップロードできませんでした。")
            logger.debug(f"Could not uploaded file saved to {USERDATA_PATH}, reason: {e}.")

    @cron.command(name="get")
    async def get_userdata(self, ctx):
        await ctx.send(":bulb: 現在のスケジュールデータです。", file=File(USERDATA_PATH))

    async def _save_userdata(self):
        async with aiofiles.open(USERDATA_PATH, mode="w", encoding="utf-8") as afp:
            await afp.write(json.dumps(self.userdata, sort_keys=True, indent=4))
        logger.debug(f"User Data {USERDATA_PATH} saved.")

    async def _load_userdata(self):
        if os.path.exists(USERDATA_PATH) and os.path.isfile(USERDATA_PATH):
            async with aiofiles.open(USERDATA_PATH, mode="r", encoding="utf-8") as afp:
                self.userdata = json.loads(await afp.read())
            logger.debug(f"User Data {USERDATA_PATH} loaded.")
        else:
            async with aiofiles.open(USERDATA_PATH, mode="w", encoding="utf-8") as afp:
                self.userdata = {}
                json.dump(self.userdata, afp)
            logger.debug(f"User Data {USERDATA_PATH} generated.")

    def cog_unload(self):
        self.tick.cancel()
        presence_type = ActivityType.unknown
        self.bot.change_presence(
            activity=Activity(type=presence_type, name=""), status=None
        )
        logger.debug(f"Presense Changed to {presence_type}.")


def setup(bot):
    bot.add_cog(Cron(bot))
