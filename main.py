import discord
import os
from discord.ext import commands
import subprocess
from log import get_logger

bot = commands.Bot(command_prefix="/")
app_name = os.getenv('DISCORD_BOT_NAME', default='PartyPoll')
logger = get_logger(app_name)


@bot.event
async def on_ready():
    logger.info("-----Logged in info-----")
    try:
        current_src_version = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).strip().decode('utf-8')
        logger.info(f"{app_name} {current_src_version}")
    except BaseException:
        logger.info("Code Version: Unknown")
    logger.info(f"Bot User Name: {bot.user.name}")
    logger.info(f"Bot User ID: {bot.user.id}")
    logger.info(f"Discord.py Version: {discord.__version__}")
    logger.info("------------------------")


@bot.command(name="ext")
@commands.has_permissions(manage_guild=True)
async def ext(ctx, method, ext_name: str):
    if method == "load":
        bot.load_extension(f"cogs.{ext_name}")
        await ctx.channel.send(f"{ext_name} をロードしました")
        logger.info(f"Cog {ext_name} loaded.")
    if method == "unload":
        bot.unload_extension(f"cogs.{ext_name}")
        await ctx.channel.send(f"{ext_name} をアンロードしました")
        logger.info(f"Cog {ext_name} unloaded.")


bot.load_extension("cogs.ppoll")
bot.load_extension("cogs.cron")
# bot.load_extension("cogs.profile")
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
