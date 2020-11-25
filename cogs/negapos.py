'''Sentiment Analyzer (Google Language API) example code.'''

import os
import discord
from discord.ext import commands
from discord.utils import get
from oauth2client.client import GoogleCredentials
from google.cloud import language_v1
from discord.ext.commands import MessageConverter
import re
from tabulate import tabulate

tabulate.WIDE_CHARS_MODE = True


class NegaPos(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.progress = {}
        self.scores = {}
        self.magni = {}
        self.enabled = False
        self.pos = True

    @commands.Cog.listener()
    async def on_ready(self):
        print("{name} Extension Enabled.".format(name=self.__cog_name__))

    @commands.group(name="np")
    async def negapos(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    def analyze_sentiment(self, text_content):
        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(content=text_content, type_=language_v1.Document.Type.PLAIN_TEXT)
        # document = {"content": text_content, "type": language_v1.Document.Type.PLAIN_TEXT}
        response = client.analyze_sentiment(request={'document': document, 'encoding_type': language_v1.EncodingType.UTF8})
        return {"score": response.document_sentiment.score, "magni": response.document_sentiment.magnitude}

    @negapos.command(name="start")
    async def start(self, ctx):
        self.enabled = True
        await ctx.send("`/np start pos` か `/np start nega` で開始します。")

    @negapos.command(name="stop")
    async def stop(self, ctx):
        self.enabled = False
        await ctx.send("ゲームを停止しました。")
        if self.pos:
            await ctx.send(":star_struck: (`・ω・´)ｱｷﾗﾒﾝﾅﾖ!!!")
        else:
            await ctx.send(":weary: ┐(´д｀)┌ﾔﾚﾔﾚ..ﾔｯﾄｵﾜｯﾀ")

    @negapos.command(name="score")
    async def show_score(self, ctx):
        me = ctx.message.author.name
        await ctx.send(f"negapos: {self.scores[me]}\n ")
        await ctx.send(f"negapos: {self.magni[me]}\n ")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return
        if self.enabled:
            senti = self.analyze_sentiment(message.content)
            score = senti["score"]
            magni = senti["magni"]
            if message.author.name in self.scores.keys():
                self.scores[message.author.nick] += score
            else:
                self.scores[message.author.nick] = score
            if message.author.name in self.scores.keys():
                self.magni[message.author.name] += magni
            else:
                self.magni[message.author.name] = magni
            negaposmark = ":sunny:" if score > 0 else ":cloud_snow:"
            magnimark = ":chart_with_upwards_trend:" if magni > 0 else ":chart_with_downwards_trend:"
            ctx = await self.bot.get_context(message)
            scored_content = f"{negaposmark} {score}, {magnimark}{magni}"
            await ctx.send(scored_content)


def setup(bot):
    bot.add_cog(NegaPos(bot))
