import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import Embed
import re
from defs import HELP_TEXT

bot = commands.Bot(command_prefix="/")

RE_LIMIT = r"^\[(\d+)\].+$"
ORG_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
EMOJIS = {k: v for k, v in zip(range(0, len(ORG_EMOJIS)), ORG_EMOJIS)}
RE_EMBED_LINE = r"(^.+\()(\d+)(/)([\d|-]+)(\).+\()(.*)(\)$)"
COLOR = discord.Colour.magenta()
SEP = ","


@bot.event
async def on_ready():
    print("-----Logged in info-----")
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print("------------------------")


async def _renew_reaction(reaction, user, is_remove=False):
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
            "{mention} さんへ\n{e}は満員だったのでリアクションを取り消しました。ごめんなさい:sob:\n{poll_url}".format(
                mention=user.mention,
                e=reaction.emoji,
                poll_url=reaction.message.jump_url,
            )
        )
        return

    reactioner = user.display_name.replace(SEP, "")  # remove comma from the name
    # update numbers of current members
    tmp[1] = str(reaction.count - 1)
    # update names of current members
    members = set(tmp[5].split(",")) if tmp[5] else set()
    if is_remove:
        members.discard(reactioner)
    else:
        members.add(reactioner)
    tmp[5] = ",".join(members)
    # update the line
    new_line = "".join(tmp)
    desc[key] = new_line
    new_embed = Embed(
        title=old_embed.title, description="\n".join(desc.values()), color=COLOR
    )
    await reaction.message.edit(embed=new_embed)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    if message.author.id != bot.user.id:
        return
    reaction = [
        reaction
        for reaction in message.reactions
        if reaction.emoji == payload.emoji.name
    ][0]
    user = [
        user
        for user in bot.get_channel(payload.channel_id).members
        if user.id == payload.user_id
    ][0]
    await _renew_reaction(reaction, user)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot.user.id:
        return
    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    if message.author.id != bot.user.id:
        return
    reaction = [
        reaction
        for reaction in message.reactions
        if reaction.emoji == payload.emoji.name
    ][0]
    user = [
        user
        for user in bot.get_channel(payload.channel_id).members
        if user.id == payload.user_id
    ][0]
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
        num: "{e} ({cur}/{lim}) {m} ()".format(
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
