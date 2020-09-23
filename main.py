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
SEP = ","
EACH_POLL = "[質問ごとの人数制限]"
TOTAL_POLL = "[質問全体での人数制限]"
COLORS = {EACH_POLL: discord.Colour.magenta(), TOTAL_POLL: discord.Colour.green()}


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
    if reaction.emoji not in ORG_EMOJIS:
        # not poll reaction
        return
    key = [s[0] for s in desc.items() if reaction.emoji in s[1]][0]

    # update current member count
    tmp = list(re.match(RE_EMBED_LINE, desc[key]).groups())
    total_reaction_count = sum([r.count for r in reaction.message.reactions]) - len(
        reaction.message.reactions
    )
    limit_reaction_count = 0
    limit = -1
    if EACH_POLL in old_embed.title:
        limit = int(tmp[3]) if tmp[3].isnumeric() else -1
        limit_reaction_count = reaction.count - 1
    elif TOTAL_POLL in old_embed.title:
        limit = int(
            re.sub(r"^\(\d+/(\d+)\)$", r"\1", old_embed.description.split("\n")[0])
        )
        limit_reaction_count = total_reaction_count

    if not is_remove and limit >= 0 and limit_reaction_count > limit:
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
    single_reaction_count = reaction.count - 1
    # update numbers of current members
    tmp[1] = str(single_reaction_count)
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
    desc[0] = re.sub(r"\d+", str(total_reaction_count), desc[0], 1)
    new_embed = Embed(
        title=old_embed.title,
        description="\n".join(desc.values()),
        color=old_embed.color,
    )
    await reaction.message.edit(embed=new_embed)


async def _get_reaction_ctx(payload):
    if payload.user_id == bot.user.id:
        return
    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    if message.author.id != bot.user.id:
        return
    if payload.emoji.name not in ORG_EMOJIS:
        # not poll reaction
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
    if reaction and user:
        return [reaction, user]
    else:
        return


@bot.event
async def on_raw_reaction_add(payload):
    contexts = await _get_reaction_ctx(payload)
    if contexts:
        await _renew_reaction(*contexts)


@bot.event
async def on_raw_reaction_remove(payload):
    contexts = await _get_reaction_ctx(payload)
    if contexts:
        await _renew_reaction(*contexts, is_remove=True)


def _get_limit(msg):
    if re.match(RE_LIMIT, msg):
        return re.sub(RE_LIMIT, r"\1", msg)
    else:
        return "-"


def _get_total_limit(args):
    return sum(
        [int(i) for i in [_get_limit(msg) for msg in args] if str(i).isnumeric()]
    )


@bot.command(name="epoll")
async def make_each_poll(ctx, title, *args):
    """Each Poll"""
    if len(args) > len(EMOJIS):
        await ctx.channel.send("指定できる選択肢は{n}個までです。".format(n=len(EMOJIS)))
        return
    headers = ["({cur}/{lim})".format(cur=0, lim=_get_total_limit(args))]
    contents = list(
        {
            num: "{e} ({cur}/{lim}) {m} ()".format(
                e=EMOJIS[num],
                cur=0,
                lim=_get_limit(msg),
                m=re.sub(r"^\[\d+\]", "", msg),
            )
            for num, msg in enumerate(args)
        }.values()
    )
    embed = discord.Embed(
        title="\n".join([title, EACH_POLL]),
        description="\n".join([*headers, *contents]),
        color=COLORS[EACH_POLL],
    )
    message = await ctx.channel.send("", embed=embed)
    for num, _ in enumerate(args):
        await message.add_reaction(EMOJIS[num])


@bot.command(name="tpoll")
async def make_total_poll(ctx, title, limit, *args):
    """Total Poll"""
    if len(args) > len(EMOJIS):
        await ctx.channel.send("指定できる選択肢は{n}個までです。".format(n=len(EMOJIS)))
        return
    headers = ["({cur}/{lim})".format(cur=0, lim=limit)]
    contents = list(
        {
            num: "{e} ({cur}/-) {m} ()".format(e=EMOJIS[num], cur=0, m=msg)
            for num, msg in enumerate(args)
        }.values()
    )
    embed = discord.Embed(
        title="\n".join([title, TOTAL_POLL]),
        description="\n".join([*headers, *contents]),
        color=COLORS[TOTAL_POLL],
    )
    message = await ctx.channel.send("", embed=embed)
    for num, _ in enumerate(args):
        await message.add_reaction(EMOJIS[num])


@bot.command(name="epoll-help")
async def help_text(ctx):
    if not ctx.author.bot:
        await ctx.channel.send(HELP_TEXT)


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
