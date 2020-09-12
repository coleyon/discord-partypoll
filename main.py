import os
import discord
from discord.ext import commands


bot = commands.Bot(command_prefix="/")


@bot.event
async def on_ready():
    print("-----Logged in info-----")
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print("------------------------")


@bot.command(name="echo")
async def echo(ctx):
    if ctx.author.bot:
        return
    await ctx.channel.send(ctx.message.content)


@bot.event
async def on_reaction_add(reaction, user):
    # author = reaction.message.author
    channel = reaction.message.channel
    await channel.send(
        "{u}さんがmessageid={id}にリアクション{r}をつけました".format(
            u=user.display_name, id=reaction.message.id, r=reaction.emoji
        )
    )


@bot.event
async def on_reaction_remove(reaction, user):
    channel = reaction.message.channel
    await channel.send(
        "{u}さんがmessageid={id}からリアクション{r}をはずしました".format(
            u=user.display_name, id=reaction.message.id, r=reaction.emoji
        )
    )


@bot.command(name="edit")
async def edit_message(ctx):
    await ctx.message.edit(content="メッセージの内容を書き替えるテスト")


@bot.command(name="poll")
async def make_poll(ctx):
    await ctx.channel.send("リアクション先を打つテスト")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
