from logging import log
import os
import discord
from discord.ext import commands
from discord.utils import get
from discord import File
import re
from log import get_logger

logger = get_logger("PollCog")
RE_LIMIT = r"^\[(\d+)\].+$"
ORG_EMOJIS = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
EMOJIS = {k: v for k, v in zip(range(0, len(ORG_EMOJIS)), ORG_EMOJIS)}
RE_EMBED_LINE = r"(^.+\()(\d+)(/)([\d|-]+)(\).+\()(.*)(\)$)"
SEP = ","
EACH_POLL = "[質問ごとの人数制限]"
TOTAL_POLL = "[質問全体での人数制限]"
COLORS = {EACH_POLL: discord.Colour.magenta(), TOTAL_POLL: discord.Colour.green()}


class Ppoll(commands.Cog):
    """Party Poll"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="ppoll")
    async def poll(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(":bulb: ppoll コマンドのマニュアルです。", file=File("helpfiles/ppoll.md"))

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("{name} Extension Enabled.".format(name=self.__cog_name__))

    async def _renew_reaction(self, reaction, user, is_remove=False):
        reactioner = user.display_name.replace(SEP, "")  # remove comma from the name

        old_embed = {
            "title": reaction.message.content.split('\n')[:3],
            "description": reaction.message.content.split('\n')[3:],
        }
        desc = {n: s for n, s in enumerate(old_embed["description"])}
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
        if EACH_POLL in old_embed["title"]:
            limit = int(tmp[3]) if tmp[3].isnumeric() else -1
            limit_reaction_count = reaction.count - 1
        elif TOTAL_POLL in old_embed["title"]:
            limit = int(
                re.sub(r"^\(\d+/(\d+)\)$", r"\1", old_embed["title"][2])
            )
            limit_reaction_count = total_reaction_count

        if not is_remove and limit >= 0 and limit_reaction_count > limit:
            # over the limit when reaction added
            await reaction.message.remove_reaction(reaction.emoji, user)
            await reaction.message.channel.send(
                "{mention}\n:x:{e}は満員だったのでリアクションを取り消しました。\n{poll_url}".format(
                    mention=user.mention,
                    e=reaction.emoji,
                    poll_url=reaction.message.jump_url,
                )
            )
            logger.info(f"Appending reaction by {reactioner} has skipped, because reached the limit. msgid={reaction.message.id}")
            return

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
        # update total limitation and current total count
        old_embed["title"][2] = re.sub(r"\d+", str(total_reaction_count), old_embed["title"][2], 1)

        title_text = "\n".join(old_embed["title"])
        content_text = "\n".join(desc.values())
        await reaction.message.edit(content=f"{title_text}\n{content_text}")
        logger.info(f"Updating reaction by {reactioner} has successed. msgid={reaction.message.id}")

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
            try:
                await self._renew_reaction(*contexts)
                logger.info("Appending reaction has successed.")
            except BaseException:
                logger.error("Appending reaction has failed.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        contexts = await self._get_reaction_ctx(payload)
        if contexts:
            try:
                await self._renew_reaction(*contexts, is_remove=True)
                logger.info("Removing reaction has successed.")
            except BaseException:
                logger.error("Removing reaction has failed.")

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
            await ctx.channel.send(":bulb: ppoll コマンドのマニュアルです。", file=File("helpfiles/ppoll.md"))

    @poll.command(name="total")
    async def make_total_poll(self, ctx, title, limit, *args):
        """Total Poll"""
        if len(args) > len(EMOJIS):
            await ctx.channel.send("指定できる選択肢は{n}個までです。".format(n=len(EMOJIS)))
            logger.info(f"Total poll topic creation by {ctx.message.author.nick} has failed.")
            return
        headers = ["({cur}/{lim})".format(cur=0, lim=limit)]
        contents = list(
            {
                num: "{e} ({cur}/-) {m} ()".format(e=EMOJIS[num], cur=0, m=msg)
                for num, msg in enumerate(args)
            }.values()
        )
        title_text = "\n".join([title, TOTAL_POLL])
        content_text = "\n".join([*headers, *contents])
        message = await ctx.channel.send(f"{title_text}\n{content_text}")
        for num, _ in enumerate(args):
            await message.add_reaction(EMOJIS[num])
        logger.info(f"Total poll topic created. msgid={message.id}")

    @poll.command(name="each")
    async def make_each_poll(self, ctx, title, *args):
        """Each Poll"""
        if len(args) > len(EMOJIS):
            await ctx.channel.send("指定できる選択肢は{n}個までです。".format(n=len(EMOJIS)))
            logger.info(f"Each poll topic creation by {ctx.message.author.nick} has failed.")
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
        title_text = "\n".join([title, EACH_POLL])
        content_text = "\n".join([*headers, *contents])
        message = await ctx.channel.send(f"{title_text}\n{content_text}")
        for num, _ in enumerate(args):
            await message.add_reaction(EMOJIS[num])
        logger.info(f"Each poll topic created. msgid={message.id}")

    async def cog_command_error(self, ctx, error):
        if not ctx.author.bot:
            logger.warn(f"Cog command something wrong, error: {error}")


def setup(bot):
    bot.add_cog(Ppoll(bot))
