import os
import discord
from discord.ext import commands


bot = commands.Bot(command_prefix="/")

["\N{REGIONAL INDICATOR SYMBOL LETTER A}", "\N{REGIONAL INDICATOR SYMBOL LETTER B}"]


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
    if user.id == bot.user.id:
        return
    channel = reaction.message.channel
    await channel.send(
        "{u}さんがmessageid={id}にリアクション{r}をつけました".format(
            u=user.display_name, id=reaction.message.id, r=reaction.emoji
        )
    )


@bot.event
async def on_reaction_remove(reaction, user):
    if user.id == bot.user.id:
        return
    channel = reaction.message.channel
    await channel.send(
        "{u}さんがmessageid={id}からリアクション{r}をはずしました".format(
            u=user.display_name, id=reaction.message.id, r=reaction.emoji
        )
    )


@bot.command(name="edit")
async def edit_message(ctx):
    await ctx.message.edit(content="メッセージの内容を書き替えるテスト")


@bot.command(name="presen")
async def presentation(ctx):
    embed = discord.Embed(
        title="選択肢を表示するテスト",
        description=":regional_indicator_a: :sparkles: Choice1 (19/20)\n:regional_indicator_b: :apple: Choice2 (1/20)",
        color=discord.Colour.magenta(),
    )
    message = await ctx.channel.send("", embed=embed)
    indicators = message.embeds[0].description
    # TODO indicators から A, B, C...を抜き出す
    indicators = [
        emoji.emojize(":regional_indicator_a:"),
        emoji.emojize(":regional_indicator_b:"),
    ]
    for emj in indicators:
        await message.add_reaction("\N{THUMBS UP SIGN}")


@bot.command(name="poll")
async def make_poll(ctx):
    await ctx.channel.send("リアクション先を打つテスト")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
