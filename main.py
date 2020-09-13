import os
import discord
from discord.ext import commands
from discord.utils import get
import re

bot = commands.Bot(command_prefix="/")

RE_LIMIT = r"^\[(\d+)\].+$"
RE_EMOJI = r"^(:.+:)"
ORG_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
EMOJIS = {k: v for k, v in zip(range(0, len(ORG_EMOJIS)), ORG_EMOJIS)}


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
    message = reaction.message
    channel = reaction.message.channel
    target_count = [r for r in message.reactions if r.emoji == reaction.emoji][
        0
    ].count - 1
    await channel.send(
        "{u}さんがmessageid={id}からリアクション{r}をはずし、リアクション者数は{c}になりました。".format(
            u=user.display_name, id=message.id, r=reaction.emoji, c=target_count
        )
    )
    # TODO message.edit(embed=message.embeds[0].description + "内容に変更を加えるテスト")
    await message.edit(content="メッセージの内容を書き替えるテスト")


def _get_limit(msg):
    if re.match(RE_LIMIT, msg):
        return re.sub(RE_LIMIT, r"\1", msg)
    else:
        return "-"


@bot.command(name="poll")
async def make_poll(ctx, title, *args):
    if len(args) > len(EMOJIS):
        await ctx.channel.send("指定できる選択肢は{n}個までです。".format(n=len(EMOJIS)))
        return
    contents = {
        num: "{e} (0/{lim}) {m}".format(e=EMOJIS[num], lim=_get_limit(msg), m=msg)
        for num, msg in enumerate(args)
    }
    embed = discord.Embed(
        title=title,
        description="\n".join(contents.values()),
        color=discord.Colour.magenta(),
    )
    message = await ctx.channel.send("", embed=embed)
    indicators = message.embeds[0].description
    # TODO indicators から A, B, C...を抜き出す
    indicators = [EMOJIS[0], EMOJIS[1]]
    for indicator in indicators:
        await message.add_reaction(indicator)


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
