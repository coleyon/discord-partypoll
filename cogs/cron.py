import asyncio
import json
import os
import re
import shlex
from collections import namedtuple
from datetime import datetime as dt
from datetime import timedelta as td
from time import sleep
from dateutil.relativedelta import relativedelta
import aiofiles
import pytz
from croniter import croniter
from discord import Activity, ActivityType, Colour, Embed, File, Status
from discord.ext import commands, tasks
from hashids import Hashids
from tabulate import tabulate

USERDATA_PATH = os.getenv("USERDATA_PATH", default="userdata.json")
Schedule = namedtuple(
    "Schedule", ("guild_id", "channel_id", "register_id", "cron", "command")
)
tabulate.WIDE_CHARS_MODE = True
HELP_TEXT = """```[Cron like Scheduler]

Synopsis:
    /cron add <SCHEDULE_NAME> <SCHEDULE> <COMMAND> - add a schedule.
    /cron del <SCHEDULE_NAME> - remove specified schedule
    /cron show - show list of registered schedules.
    /cron get - download a schedule file formatted with json.
    /cron load - upload a schedule file formatted with json.

SCHEDULE_NAME:
    Name of the schedule.

SCHEDULE:
    * * * * *
    | | | | |
    | | | | |
    | | | | +---- Day of the Week   (range: 0-6 or mon,tue,wed,thu,fri,sat,sun)
    | | | +------ Month of the Year (range: 1-12)
    | | +-------- Day of the Month  (range: 1-31)
    | +---------- Hour              (range: 0-23)
    +------------ Minute            (range: 0-59)  # every n day in month.
    Expression Field Description
    ----------------------------------
    *        any    Fire on every value
    */a      any    Fire every a values, starting from the minimum
    a-b      any    Fire on any value within the a-b range (a must be smaller than b)
    a-b/c    any    Fire every c values within the a-b range
    x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions

    Examples:
        */1 * * * *      : runs at every minutes.
        59 * * * sun     : runs at 59 minutes every hour
        0 14,21 * * *    : runs at 14:00 and 21:00 every day.
        40-50 3 25 12 *  : runs from 3:40 to 3:50 on December 25th.

COMMAND:
    The Commands executed on the specified schedule.
    i.e.: /tpoll title 5 "first question" "second question"

InplaceDate:
    For example, you want to notify members 
    about a date three days after the command execution date.
    Let's assume that the command execution date is December 21st
    and the event date is December 24th.

    /tpoll "Event on 12/24(Mon)" 5 "I'm Join!" "Damn.."

    In such a case, specify the COMMAND part as follows.

    /tpoll "Event on {{days.3}}" 5 "I'm Join!" "Damn.."
```"""


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
        self.default_channel = None
        await self._load_userdata()
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    @commands.group()
    async def cron(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(HELP_TEXT)

    @tasks.loop(minutes=1.0, reconnect=True)
    async def tick(self):
        current = self._now()
        # await self._load_userdata()
        for k, v in self.userdata.items():
            if croniter.match(v[0], current):
                await self.default_channel.send(f"{v[1]}")

    # def IC(self, n):
    #     d = self._now() + relativedelta()
    #     return d.strftime("%m/%d")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            if message.content.startswith("/"):
                ctx = await self.bot.get_context(message)
                # replaced_message = re.sub(
                #     r"\{\{days\.\d+\}\}", lambda x: self.IC(x.group()), message.content
                # )
                m = shlex.split(replaced_message)
                cmd = m[0][1:]
                query = m[1:]
                await ctx.invoke(self.bot.get_command(cmd), *query)

    @tick.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()

    @cron.command(name="disable")
    async def disable_cron(self, ctx):
        self.tick.cancel()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name=":sleeping:")
        )
        await self.default_channel.send(":first_quarter_moon_with_face: 自動実行を無効にしました。")

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
        else:
            await ctx.send(f"今のタイムゾーンは {self.timezone} です。")

    @cron.command(name="enable")
    async def enable_cron(self, ctx):
        self.default_channel = ctx.channel
        await self._load_userdata()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name="Enable Cron")
        )
        self.tick.start()
        await self.default_channel.send(":sun_with_face: 自動実行を有効にしました。")

    @cron.command(name="show")
    async def show_schedule(self, ctx):
        headers = ["名前", "分", "時", "日", "月", "曜日", "コマンド"]
        table = []
        for k, v in self.userdata.items():
            crontab = v[0].split(" ")
            table.append([k, *crontab, v[1]])
        formatted_description = tabulate(table, headers, tablefmt="simple")
        await ctx.channel.send(
            f"{len(self.userdata)} 件のスケジュールが登録されています\n```{formatted_description}```"
        )

    @cron.command(name="del")
    async def delete_schedule(self, ctx, name):
        self.userdata.pop(name)
        await self._save_userdata()
        await ctx.send(f"スケジュール `{name}` を除去しました。")

    @cron.command(name="add")
    async def add_schedule(self, ctx, name, m, h, dom, mon, dow, *cmd):
        crontab = " ".join([m, h, dom, mon, dow])
        if not croniter.is_valid(crontab):
            await ctx.send(f"スケジュール `{crontab}` が不正です。")
        else:
            escaped_cmds = " ".join((f'"{i}"' if " " in i else i for i in cmd))
            new_record = {name: [crontab, escaped_cmds]}
            self.userdata = {**self.userdata, **new_record}
            await self._save_userdata()
        next_run = self._strftime(croniter(crontab, self._now()).get_next(dt))
        await ctx.send(
            f"スケジュール `{name}` を追加しました。\n"
            f"次回実行予定は {next_run} です。\n"
            f"実行されるコマンドは `{escaped_cmds}` です。"
        )

    @cron.command(name="upload")
    async def upload_userdata(self, ctx):
        try:
            await ctx.message.attachments[0].save(fp=USERDATA_PATH)
            await self._load_userdata()
            await ctx.send(":yum: スケジュールをアップロードしました。")
        except BaseException:
            await ctx.send(":hot_face: スケジュールをアップロードできませんでした。")

    @cron.command(name="get")
    async def get_userdata(self, ctx):
        await ctx.send("現在のスケジュールデータです。", file=File(USERDATA_PATH))

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
