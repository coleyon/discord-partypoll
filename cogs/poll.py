import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import Embed
import re


RE_LIMIT = r"^\[(\d+)\].+$"
ORG_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
EMOJIS = {k: v for k, v in zip(range(0, len(ORG_EMOJIS)), ORG_EMOJIS)}
RE_EMBED_LINE = r"(^.+\()(\d+)(/)([\d|-]+)(\).+\()(.*)(\)$)"
SEP = ","
EACH_POLL = "[質問ごとの人数制限]"
TOTAL_POLL = "[質問全体での人数制限]"
COLORS = {EACH_POLL: discord.Colour.magenta(), TOTAL_POLL: discord.Colour.green()}
HELP_TEXT = """```[Party Poll]

クイックスタート:
  /ppoll each それぞれ参加人数が違うイベント [5]お花見 [3]BBQ 人数制限なし鍋パー
  /ppoll total 10名分の予算がある3種のイベント 10 お花見 BBQ 鍋パー

コマンド(<> は実際には入力しません):
  /ppoll each <TITLE> <[EACH_LIMIT_n]QUESTION_n> - アンケートを出す（質問毎に回答数制限を指定可）
  /ppoll total <TITLE> <TOTAL_LIMIT> <QUESTION_n> - アンケートを出す（質問全体に回答数制限を指定可）

TITLE:
    Pollのタイトル

EACH_LIMIT_n:
    個々の質問に回答できる最大の人数。省略すると無制限。

TOTAL_LIMIT:
    全ての質問に回答できる最大の人数。省略できない。

QUESTION_n:
    質問文。最大10個まで指定可能。
```"""


class Poll(commands.Cog):
    """"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if not ctx.author.bot:
            await ctx.channel.send(HELP_TEXT)

    @commands.group(name="ppoll")
    async def poll(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(HELP_TEXT)

    @commands.Cog.listener()
    async def on_ready(self):
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    async def _renew_reaction(self, reaction, user, is_remove=False):
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

    async def _get_reaction_ctx(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        message = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id
        )
        if message.author.id != self.bot.user.id:
            return
        if payload.emoji.name not in ORG_EMOJIS:
            # not poll reaction
            return
        reaction = [
            reaction
            for reaction in message.reactions
            if reaction.emoji == payload.emoji.name
        ][0]
        user = await self.bot.get_channel(payload.channel_id).guild.fetch_member(
            payload.user_id
        )
        if reaction and user:
            return [reaction, user]
        else:
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        contexts = await self._get_reaction_ctx(payload)
        if contexts:
            await self._renew_reaction(*contexts)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        contexts = await self._get_reaction_ctx(payload)
        if contexts:
            await self._renew_reaction(*contexts, is_remove=True)

    def _get_limit(self, msg):
        if re.match(RE_LIMIT, msg):
            return re.sub(RE_LIMIT, r"\1", msg)
        else:
            return "-"

    def _get_total_limit(self, args):
        return sum(
            [
                int(i)
                for i in [self._get_limit(msg) for msg in args]
                if str(i).isnumeric()
            ]
        )

    @poll.command(name="help")
    async def help_text(self, ctx):
        if not ctx.author.bot:
            await ctx.channel.send(HELP_TEXT)

    @poll.command(name="total")
    async def make_total_poll(self, ctx, title, limit, *args):
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

    @poll.command(name="each")
    async def make_each_poll(self, ctx, title, *args):
        """Each Poll"""
        if len(args) > len(EMOJIS):
            await ctx.channel.send("指定できる選択肢は{n}個までです。".format(n=len(EMOJIS)))
            return
        headers = ["({cur}/{lim})".format(cur=0, lim=self._get_total_limit(args))]
        contents = list(
            {
                num: "{e} ({cur}/{lim}) {m} ()".format(
                    e=EMOJIS[num],
                    cur=0,
                    lim=self._get_limit(msg),
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


def setup(bot):
    bot.add_cog(Poll(bot))
