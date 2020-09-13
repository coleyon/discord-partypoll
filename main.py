import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import Embed
import re

bot = commands.Bot(command_prefix="/")

RE_LIMIT = r"^\[(\d+)\].+$"
ORG_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
EMOJIS = {k: v for k, v in zip(range(0, len(ORG_EMOJIS)), ORG_EMOJIS)}
RE_EMBED_LINE = r"(^.+\()(\d+)(/)([\d|-]+)(\).+$)"
COLOR = discord.Colour.magenta()

HELP_TEXT = """[Extended Poll]
■質問に回答する人向け
https://kaze-lab.com/discord-simplepoll/
こちらで解説されている `Simple Poll` Botと用法がほぼ同じですが、
質問へ回答した時に人数上限に達した場合に、
回答が自動的に取り消されつつ、その旨をBotが教えてくれる点が異なります。
つまり、上限を超える回答をしないように回答者側が気を使わなくて良いです。

■質問を作る人向け
回答に人数制限をつけることができる Simple Poll のクローンです。
質問は最大10コまで指定できます。

コマンド構文:
　　`/epoll "タイトル" "[1]回答者数の上限が1の質問" "上限が無い質問" ...`
　　`/epoll-help`
コマンド例:
　　`/epoll イベントだよ！ "[10]:white_flower: お花見" "[3] :peach: 桃狩り" ":snowflake: 雪まつり"`
　　`/epoll title [1]1 2 3 4 5 6 7 8 9 10`

日本語やスペースを含む質問はダブルクォーテーション `"` で囲む必要があります。
半角英数のみでスペースを含まない質問（例えば`[1]Question-A`）はクォーテーションで囲まなくても大丈夫です。
"""


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


async def _renew_reaction(reaction, user, is_remove=False):
    if user.id == bot.user.id:
        return
    old_embed = reaction.message.embeds[0]
    desc = {n: s for n, s in enumerate(old_embed.description.split("\n"))}
    key = [s[0] for s in desc.items() if reaction.emoji in s[1]][0]

    # update current member count
    tmp = list(re.match(RE_EMBED_LINE, desc[key]).groups())
    limit = int(tmp[3]) if tmp[3].isnumeric() else -1
    if not is_remove and limit >= 0 and reaction.count - 1 > limit:
        # over the limit when reaction added
        await reaction.message.remove_reaction(reaction.emoji, user)
        await reaction.message.channel.send(
            "{mention} さんへ\n{e} はもう満員だったので、今のリアクションを取り消しました。ごめんなさい:sob:\n{poll_url}".format(
                mention=user.mention,
                e=reaction.emoji,
                poll_url=reaction.message.jump_url,
            )
        )
        return

    tmp[1] = str(reaction.count - 1)
    new_line = "".join(tmp)
    desc[key] = new_line
    # update current
    new_embed = Embed(
        title=old_embed.title, description="\n".join(desc.values()), color=COLOR
    )
    await reaction.message.edit(embed=new_embed)


@bot.event
async def on_reaction_add(reaction, user):
    await _renew_reaction(reaction, user)


@bot.event
async def on_reaction_remove(reaction, user):
    await _renew_reaction(reaction, user, is_remove=True)


def _get_limit(msg):
    if re.match(RE_LIMIT, msg):
        return re.sub(RE_LIMIT, r"\1", msg)
    else:
        return "-"


@bot.command(name="epoll")
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
        title=title, description="\n".join(contents.values()), color=COLOR
    )
    message = await ctx.channel.send("", embed=embed)
    for num, _ in enumerate(args):
        await message.add_reaction(EMOJIS[num])


@bot.command(name="epoll-help")
async def help_text(ctx):
    if not ctx.author.bot:
        await ctx.channel.send(HELP_TEXT)


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
