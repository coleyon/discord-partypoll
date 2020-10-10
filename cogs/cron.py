from discord.ext import commands, tasks
from datetime import datetime as dt
from datetime import timedelta as td
from hashids import Hashids
from discord import Embed, Activity, ActivityType, Status, Colour, File
from collections import namedtuple
import aiofiles
import aiohttp
from croniter import croniter
import json
from tabulate import tabulate
import os
import pytz
from time import sleep

USERDATA_PATH = os.getenv("USERDATA_PATH", default="userdata.json")
Schedule = namedtuple(
    "Schedule", ("guild_id", "channel_id", "register_id", "cron", "command")
)
tabulate.WIDE_CHARS_MODE = True


class Cron(commands.Cog):
    """cron based task"""

    def __init__(self, bot):
        self.bot = bot
        self.timezone = os.getenv("TIMEZONE", default="Asia/Tokyo")

    def _now(self):
        return dt.now(pytz.utc).astimezone(pytz.timezone(self.timezone))

    @commands.Cog.listener()
    async def on_ready(self):
        self.default_channel = None
        await self._load_userdata()
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    @commands.group()
    async def cron(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("TODO: ヘルプテキストを表示")

    @tasks.loop(minutes=1.0, reconnect=True)
    async def tick(self):
        x = str(dt.now())
        print(x)
        self.default_channel.send(x)

    @tick.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

    @cron.command(name="disable")
    async def disable_cron(self, ctx):
        self.tick.cancel()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name="Pause Cron")
        )

    @cron.command(name="timezone")
    async def set_timezone(self, ctx, tz=None):
        if tz:
            if tz in pytz.all_timezones:
                self.timezone = tz
                await ctx.send(f"タイムゾーン {self.timezone} にセットしました。")
            else:
                await ctx.send(
                    f"指定したタイムゾーン {tz} はありません。\n"
                    f"指定できるタイムゾーンは https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 です。"
                )

    @cron.command(name="enable")
    async def enable_cron(self, ctx):
        self.default_channel = ctx.channel
        await ctx.invoke(self.bot.get_command("cron").all_commands["load"])
        self.tick.start()
        await self.bot.change_presence(
            activity=Activity(
                type=ActivityType.unknown, name=f"Cron: {len(self.userdata)}"
            )
        )

    @cron.command(name="show")
    async def show_schedule(self, ctx):
        headers = ["名前", "分", "時", "日", "月", "曜日", "コマンド"]
        await self._load_userdata()
        table = []
        for k, v in self.userdata.items():
            crontab = v[0].split(" ")
            table.append([k, *crontab, v[1]])
        formatted_description = tabulate(table, headers, tablefmt="simple")
        embed = Embed(
            title=f"{len(self.userdata)} 件のスケジュールが登録されています", color=Colour.gold()
        )
        await ctx.channel.send(f"```{formatted_description}```", embed=embed)

    @cron.command(name="del")
    async def delete_schedule(self, ctx, name):
        await ctx.send(f"スケジュール `{self.userdata.pop(name)}` を除去しました。")
        await self._save_userdata()

    @cron.command(name="add")
    async def add_schedule(self, ctx, name, m, h, dom, mon, dow, *cmd):
        crontab = " ".join([m, h, dom, mon, dow])
        if not croniter.is_valid(crontab):
            await ctx.send(f"スケジュール `{crontab}` の指定がおかしいです。")
            return
        cmd = " ".join(cmd)
        x = {name: [crontab, cmd]}
        self.userdata = {**self.userdata, **x}
        await self._save_userdata()
        itr = croniter(crontab, self._now())
        await ctx.send(
            f"スケジュール `{name}` を追加しました。\n"
            f"次回実行予定は {itr.get_next()} です。\n"
            f"実行されるコマンドは `{cmd}` です。"
        )

    @cron.command(name="upload")
    async def upload_userdata(self, ctx):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as resp:
                    if resp.status == 200 and resp.reason == "OK":
                        self.userdata = json.loads(await resp.text(), encoding="utf-8")
                    else:
                        raise
            await self._save_userdata()
            await ctx.send(":yum: スケジュールが正しくアップロードできました。")
        except BaseException:
            await ctx.send(":hot_face: スケジュールが正しくアップロードできませんでした。")
        await ctx.invoke(self.bot.get_command("cron").all_commands["show"])

    @cron.command(name="get")
    async def get_userdata(self, ctx):
        await self._save_userdata()
        with open(USERDATA_PATH, mode="r", encoding="utf-8") as fp:
            await ctx.send("現在のスケジュールデータです。", file=File(fp, "userdata.json"))

    async def _save_userdata(self):
        async with aiofiles.open(USERDATA_PATH, mode="w", encoding="utf-8") as afp:
            await afp.write(json.dumps(self.userdata, sort_keys=True, indent=4))

    async def _load_userdata(self):
        if os.path.exists(USERDATA_PATH) and os.path.isfile(USERDATA_PATH):
            async with aiofiles.open(USERDATA_PATH, mode="r", encoding="utf-8") as afp:
                self.userdata = json.loads(await afp.read())
        else:
            async with aiofiles.open(USERDATA_PATH, mode="w", encoding="utf-8") as afp:
                self.userdata = {}
                json.dump(self.userdata, afp)

    @cron.command(name="load")
    async def load_schedules(self, ctx):
        await self._load_userdata()
        await ctx.send(f"{len(self.userdata)} 件のスケジュールをロードしました。")

    def cog_unload(self):
        self.tick.cancel()
        self.bot.change_presence(activity=None, status=None)


def setup(bot):
    bot.add_cog(Cron(bot))
