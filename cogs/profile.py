import json
import os
from discord.ext import commands
from discord import Member, User
import aiofiles
from tabulate import tabulate
from discord import File
from log import get_logger

logger = get_logger("ProfileCog")
PROFDATA_PATH = os.getenv("PROFILEDATA_PATH", default="profiledata.json")
EMOJIS = {"ok": "\N{SQUARED OK}", "ng": "\N{SQUARED NG}"}
tabulate.WIDE_CHARS_MODE = True


class Profile(commands.Cog):
    """Profile

    ProfdataFormat:
        {
            GUILD_ID: {
                USER_ID: {
                    "key1": "value1",
                    "key2": "value2",
                },
            },
        }
    """

    def __init__(self, bot):
        self.bot = bot
        self.profdata = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self._load_profiledata()
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    @commands.group(name="profile")
    async def profile(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(":bulb: profile コマンドのマニュアルです。", file=File("helpfiles/profile.md"))

    @profile.command(name="addto")
    async def add_profile_to(self, ctx, user: Member, key: str, value: str):
        if str(ctx.guild.id) not in self.profdata.keys():
            self.profdata[str(ctx.guild.id)] = {}
        elif str(user.id) not in self.profdata[str(ctx.guild.id)].keys():
            self.profdata[str(ctx.guild.id)][str(user.id)] = {}
        self.profdata[str(ctx.guild.id)][str(user.id)][key] = value
        await self._save_profiledata()
        await ctx.message.send(EMOJIS['ok'])

    @profile.command(name="add")
    async def add_profile(self, ctx, key: str, value: str):
        if str(ctx.guild.id) not in self.profdata.keys():
            self.profdata[str(ctx.guild.id)] = {}
        elif str(ctx.message.author.id) not in self.profdata[str(ctx.guild.id)].keys():
            self.profdata[str(ctx.guild.id)][str(ctx.message.author.id)] = {}
        self.profdata[str(ctx.guild.id)][str(ctx.message.author.id)][key] = value
        await self._save_profiledata()
        await ctx.message.send(EMOJIS['ok'])

    @profile.command(name="show")
    async def show_profile(self, ctx, user: Member):
        header = ["KEY", "VALUE"]
        try:
            author_profiles = self.profdata[str(ctx.guild.id)][str(user.id)]
            [[k, v] for k, v in author_profiles.items()]
            formatted_description = tabulate([[k, v] for k, v in author_profiles.items()], header, tablefmt="simple")
            await ctx.message.add_reaction(EMOJIS['ok'])
            await ctx.send(f"{user.nick}さんのプロフィール\n\n{formatted_description}")
        except BaseException:
            await ctx.message.add_reaction(EMOJIS['ng'])

    @profile.command(name="del")
    async def del_profile(self, ctx, key: str):
        try:
            del self.profdata[str(ctx.guild.id)][str(ctx.message.author.id)][key]
            await self._save_profiledata()
            await ctx.message.add_reaction(EMOJIS['ok'])
        except KeyError:
            await ctx.message.add_reaction(EMOJIS['ng'])

    @profile.command(name="delfrom")
    async def del_profile_from(self, ctx, user: Member, key: str):
        try:
            del self.profdata[str(ctx.guild.id)][str(user.id)][key]
            await self._save_profiledata()
            await ctx.message.add_reaction(EMOJIS['ok'])
        except KeyError:
            await ctx.message.add_reaction(EMOJIS['ng'])

    @profile.command(name="reset")
    async def reset_profile(self, ctx):
        try:
            del self.profdata[str(ctx.guild.id)][str(ctx.message.author.id)]
            await self._save_profiledata()
            await ctx.message.add_reaction(EMOJIS['ok'])
        except KeyError:
            await ctx.message.add_reaction(EMOJIS['ng'])

    async def _save_profiledata(self):
        async with aiofiles.open(PROFDATA_PATH, mode="w", encoding="utf-8") as afp:
            await afp.write(json.dumps(self.profdata, sort_keys=True, indent=4))
        logger.debug(f"User Data {PROFDATA_PATH} saved.")

    async def _load_profiledata(self):
        if os.path.exists(PROFDATA_PATH) and os.path.isfile(PROFDATA_PATH):
            async with aiofiles.open(PROFDATA_PATH, mode="r", encoding="utf-8") as afp:
                self.profdata = json.loads(await afp.read())
            logger.debug(f"Profile Data {PROFDATA_PATH} loaded.")
        else:
            async with aiofiles.open(PROFDATA_PATH, mode="w", encoding="utf-8") as afp:
                self.profdata = {}
                json.dump(self.profdata, afp)
            logger.debug(f"Profile Data {PROFDATA_PATH} generated.")


def setup(bot):
    bot.add_cog(Profile(bot))
