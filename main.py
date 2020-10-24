import discord
import os
from discord.ext import commands

bot = commands.Bot(command_prefix="/")


@bot.event
async def on_ready():
    print("-----Logged in info-----")
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print("------------------------")


@bot.command(name="ext")
@commands.has_permissions(manage_guild=True)
async def ext(ctx, method, ext_name):
    if method == "load":
        bot.load_extension("cogs.{name}".format(name=ext_name))
        await ctx.channel.send("{name} をロードしました".format(name=ext_name))
    if method == "unload":
        bot.unload_extension("cogs.{name}".format(name=ext_name))
        await ctx.channel.send("{name} をアンロードしました".format(name=ext_name))


bot.load_extension("cogs.poll")
bot.load_extension("cogs.cron")
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
