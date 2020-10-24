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
HELP_TEXT = """```[Cron]

クイックスタート:
    ※基準時を米国東部時間にして、コマンドを登録して、動作モードにする例
    /cron timezone EST
    /cron add Schedule-A */1 * * * * /tpoll "It is TITLE" 5 a b c
    /cron enable

    ※登録したコマンドをファイルに保管してから削除し、停止モードにする例
    /cron get
    /cron del Schedule-A
    /cron disable

コマンド(<> は実際には入力しません):
    /cron add <SCHEDULE_NAME> <SCHEDULE> <COMMAND> - スケジュールを登録する
    /cron del <SCHEDULE_NAME> - スケジュールを削除する
    /cron show - スケジュールの一覧を見る
    /cron get - スケジュールをjson形式のファイルに書き出してダウンロード可能にする
    /cron load - json形式のファイルをアップロードしてスケジュールをロードさせる
    /cron timezone - 今のタイムゾーン設定を見る
    /cron timezone <TZ> - タイムゾーンを設定する（どこの国の時間で動くか）
    /cron [help] - このヘルプを表示する
    /cron enable - 動作モードにする（スケジュールが実行されます）
    /cron disable - 停止モードにする（スケジュールが実行されません）

SCHEDULE_NAME:
    スケジュール名（任意の名前）

SCHEDULE:
    * * * * *
    | | | | |
    | | | | |
    | | | | +---- 曜日 (0-6 または mon,tue,wed,thu,fri,sat,sun)
    | | | +------ 月 (1-12)
    | | +-------- 日 (1-31)
    | +---------- 時 (0-23)
    +------------ 分 (0-59)

    SCHEDULEに指定できる値
    ----------------------------------
    *     : 全ての値で動作する（分に指定すると毎分の意）
    */a   : 毎 a で動作する（月に指定すると毎 a 月の意）
    a-b   : a から b の間で動作する（時に指定すると a ～ b 時の意）
    a-b/c : a から b にかけて毎 c に動作する（時に 9-17/2 と指定すると、9～17時にかけて2時間毎の意）
    x,y,z : x と y と z に動作する（月に 4,10 と指定すると、4月と10月の意）

    具体例
    ----------------------------------
    * * * * *        : 毎分
    */2 * * * *      : 2分毎
    59 * * * sun     : 日曜日の毎時59分
    0 14,21 * * *    : 毎日 14:00 と 21:00
    40-50 3 25 12 *  : 12/25 3:40～3:50 にかけて毎分

COMMAND:
    <SCHEDULE> で指定したタイミングに実行される Discordのコマンド。
    例: /ppoll total イベントだよ! 5 "花見" "クリスマス"

    拡張
    ----------------------------------
    コマンド実行時から見てn日後となる日付を、コマンドの内容に差し込む機能です。
    例えば、毎週月曜～火曜に開催されるイベントの募集を出すコマンドを、
    前の週の金曜日に定時実行させたい場合などに使えます。
    この例で言えば、COMMAND部を以下のように指定できます。
    /ppoll total "定例イベント {{3.days}}～{{4.days}}" 5 "参加" "不参加"

    このコマンドが実行されたタイミングが10/1だとしたら、
    以下のコマンドが実際には動きます。
    /ppoll total "定例イベント 10/4～10/5" 5 "参加" "不参加"
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
        await self._load_userdata()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name=""), status=None
        )
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    @commands.group()
    async def cron(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(HELP_TEXT)

    @tasks.loop(minutes=1.0, reconnect=True)
    async def tick(self):
        current = self._now()
        for k, v in self.userdata.items():
            if croniter.match(v["schedule"], current):
                cmd = v["command"]
                ch = self.bot.get_channel(v["channel_id"])
                await ch.send(f"{cmd}")
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name="Cron"), status=None
        )

    def IC(self, n):
        offset = re.sub(r"\{\{(\d+)\.days\}\}", r"\1", n)
        d = self._now() + relativedelta(days=int(offset))
        return d.strftime("%m/%d")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            if message.content.startswith("/"):
                ctx = await self.bot.get_context(message)
                replaced_message = re.sub(  # (∩´∀｀)∩
                    r"\{\{(\d+)\.days\}\}",
                    lambda x: self.IC(x.group()),
                    message.content,
                )
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
            activity=Activity(type=ActivityType.unknown, name=""), status=None
        )
        await ctx.channel.send(":yum: 自動実行を無効にしました。")

    @cron.command(name="timezone")
    async def set_timezone(self, ctx, tz=None):
        if tz:
            if tz in pytz.all_timezones:
                self.timezone = tz
                await ctx.send(f"タイムゾーン {self.timezone} にセットしました。")
            else:
                await ctx.send(
                    f":no_entry_sign: 指定したタイムゾーン {tz} はありません。\n"
                    f":bulb: 指定できるタイムゾーンは https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568 です。"
                )
        else:
            await ctx.send(f":bulb: 今のタイムゾーンは {self.timezone} です。")

    @cron.command(name="enable")
    async def enable_cron(self, ctx):
        await self._load_userdata()
        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name="Cron"), status=None
        )
        self.tick.start()
        await ctx.channel.send(":yum: 自動実行を有効にしました。")

    @cron.command(name="show")
    async def show_schedule(self, ctx):
        headers = ["名前", "分", "時", "日", "月", "曜日", "コマンド"]
        table = []
        for k, v in self.userdata.items():
            crontab = v["schedule"].split(" ")
            table.append([k, *crontab, v["command"]])
        formatted_description = tabulate(table, headers, tablefmt="simple")
        await ctx.channel.send(
            f":bulb: {len(self.userdata)} 件のスケジュールが登録されています\n```{formatted_description}```"
        )

    @cron.command(name="del")
    async def delete_schedule(self, ctx, name):
        self.userdata.pop(name)
        await self._save_userdata()
        await ctx.send(f":yum: スケジュール `{name}` を除去しました。")

    @cron.command(name="add")
    async def add_schedule(self, ctx, name, m, h, dom, mon, dow, *cmd):
        crontab = " ".join([m, h, dom, mon, dow])
        if not croniter.is_valid(crontab):
            await ctx.send(f":no_entry_sign: スケジュール `{crontab}` が不正です。")
        else:
            escaped_cmds = " ".join((f'"{i}"' if " " in i else i for i in cmd))
            self.userdata[name] = {
                "command": escaped_cmds,
                "server_id": ctx.guild.id,
                "channel_id": ctx.channel.id,
                "author": ctx.message.author.id,
                "schedule": crontab,
            }
            await self._save_userdata()
        next_run = self._strftime(croniter(crontab, self._now()).get_next(dt))
        await ctx.send(
            f":yum: スケジュール `{name}` を追加しました。\n"
            f"次回実行予定は {next_run} です。\n"
            f"実行されるコマンドは `{escaped_cmds}` です。"
        )

    @cron.command(name="load")
    async def upload_userdata(self, ctx):
        try:
            await ctx.message.attachments[0].save(fp=USERDATA_PATH)
            await self._load_userdata()
            await ctx.send(":yum: スケジュールをアップロードしました。")
        except BaseException:
            await ctx.send(":no_entry_sign: スケジュールをアップロードできませんでした。")

    @cron.command(name="get")
    async def get_userdata(self, ctx):
        await ctx.send(":bulb: 現在のスケジュールデータです。", file=File(USERDATA_PATH))

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

    def cog_unload(self):
        self.tick.cancel()
        self.bot.change_presence(
            activity=Activity(type=ActivityType.unknown, name=""), status=None
        )


def setup(bot):
    bot.add_cog(Cron(bot))
