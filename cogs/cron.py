from discord.ext import commands, tasks
from datetime import datetime as dt
from datetime import timedelta as td
from hashids import Hashids
import json
import os
import uuid
from time import sleep


class Cron(commands.Cog):
    """cron based task"""

    def __init__(self, bot):
        self.bot = bot
        self.mainloop.start()
        self.hashids = Hashids(
            min_length=4, salt=os.getenv("HASHIDS_SALT", default="123")
        )
        self.schedules = dict()

    @commands.group()
    async def cron(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("TODO: ヘルプテキストを表示")

    @cron.command()
    async def add(self, ctx, name, m, h, dom, mon, dow, cmd):
        value = ", ".join([m, h, dom, mon, dow, cmd])
        uid = self.hashids.encode(name)
        x = {uid: value}
        self.schedules = {**self.schedules, **x}
        await ctx.send(f"{name} をスケジュールしました。次回実行は yyyy-mm-dd hh:mm です。")

    @cron.command()
    async def delete(self, ctx, name):
        await ctx.send(f"{name} をスケジュールから除去しました。")

    @cron.command()
    async def dump(self, ctx):
        sch = json.dumps(
            self.schedules,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
            separators=(",", ": "),
        )
        await ctx.send(f"登録されたスケジュールは以下です。{sch}")

    @cron.command()
    async def load(self, ctx):
        await ctx.send(f"スケジュールを添付ファイルからロードしました。")

    @cron.command()
    async def setnotif(self, ctx):
        self.default_channel = ctx.channel
        await ctx.send(f"{ctx.channel.name} を通知先チャネルにセットしました。")

    @commands.Cog.listener()
    async def on_ready(self):
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    @tasks.loop(minutes=1.0, reconnect=True)
    async def mainloop(self):
        self.default_channel.send("run!")

    @mainloop.before_loop
    async def check_next_schedule():
        self.default_channel.send("standby 2secs...")
        sleep(2.0)

    def cog_unload(self):
        self.mainloop.cancel()


def setup(bot):
    bot.add_cog(Cron(bot))
