import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import Embed
import re
import string

bot = commands.Bot(command_prefix="/")

RE_LIMIT = r"^\[(\d+)\].+$"
RE_CURRENT_LIMIT = r"^.+\((\d+)/(\d+)\).+$"
RE_EMOJI = r"^(:.+:)"
# RE_EMOJI_UNICODE = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
ORG_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
EMOJIS = {k: v for k, v in zip(range(0, len(ORG_EMOJIS)), ORG_EMOJIS)}
RE_EMBED_LINE = r"(^.+\()(\d+)(/)([\d|-]+)(\).+$)"


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
    old_embed = reaction.message.embeds[0]
    desc = {n: s for n, s in enumerate(old_embed.description.split("\n"))}
    key = [s[0] for s in desc.items() if reaction.emoji in s[1]][0]

    # update current member count
    tmp = list(re.match(RE_EMBED_LINE, desc[key]).groups())
    tmp[1] = str(reaction.count - 1)
    new_line = "".join(tmp)
    desc[key] = new_line
    # update current
    new_embed = Embed(title=old_embed.title, description="\n".join(desc.values()))
    await reaction.message.edit(embed=new_embed)


@bot.event
async def on_reaction_remove(reaction, user):
    # if user.id == bot.user.id:
    #     return
    # message = reaction.message
    # channel = reaction.message.channel
    # target_count = [r for r in message.reactions if r.emoji == reaction.emoji][
    #     0
    # ].count - 1
    # await channel.send(
    #     "{u}さんがmessageid={id}からリアクション{r}をはずし、リアクション者数は{c}になりました。".format(
    #         u=user.display_name, id=message.id, r=reaction.emoji, c=target_count
    #     )
    # )
    # # TODO message.edit(embed=message.embeds[0].description + "内容に変更を加えるテスト")
    # await message.edit(content="メッセージの内容を書き替えるテスト")
    if user.id == bot.user.id:
        return
    old_embed = reaction.message.embeds[0]
    desc = {n: s for n, s in enumerate(old_embed.description.split("\n"))}
    key = [s[0] for s in desc.items() if reaction.emoji in s[1]][0]

    # update current member count
    tmp = list(re.match(RE_EMBED_LINE, desc[key]).groups())
    tmp[1] = str(reaction.count - 1)
    new_line = "".join(tmp)
    desc[key] = new_line
    # update current
    new_embed = Embed(title=old_embed.title, description="\n".join(desc.values()))
    await reaction.message.edit(embed=new_embed)


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
        num: "{e} ({cur}/{lim}) {m}".format(
            e=EMOJIS[num], cur=0, lim=_get_limit(msg), m=re.sub(r"^\[\d+\]", "", msg)
        )
        for num, msg in enumerate(args)
    }
    embed = discord.Embed(
        title=title,
        description="\n".join(contents.values()),
        color=discord.Colour.magenta(),
    )
    message = await ctx.channel.send("", embed=embed)
    for num, _ in enumerate(args):
        await message.add_reaction(EMOJIS[num])


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
