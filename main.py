import os
from html import unescape
import discord
from discord.ext import commands
from oauth2client.client import GoogleCredentials
from google.cloud import translate_v2 as translate


bot = commands.Bot(command_prefix="/")
GoogleCredentials.get_application_default()
TRANSLATION_SOFT_LIMIT = 2000
MANUAL = """Translate and respond to messages your posted message on the discord channel.
```
syntax:
  /tran <src> <dest> <message>
    The parameters src and dest can be ISO_639-1 codes.
    https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
  /man ["desc"]
    Show manual or description of this tool.
```
"""
ABOUT_THIS_TOOL = """
```
privacy(en):
  This tool sends the messages you post to the Google Translate 
  service only for the purpose of translating the messages you post.
  If you do not want the messages you post to be 
  sent or processed by Google Translate, please do not use this tool.
  This tool will not use or process any information for any 
  purpose other than the translation you instructed it.
privacy(ja):
  このツールは、あなたが投稿したメッセージを翻訳するためだけに、
  あなたが投稿したメッセージをGoogle翻訳サービスへ送信して翻訳します。
  もしあなたが、あなたの投稿するメッセージがGoogle翻訳サービスへ
  送信されたり処理される事を望まない場合は、このツールを利用しないでください。
  このツールは、あなたがこのツールに対して指示した翻訳以外の目的では、
  いかなる情報収集も処理も行いません。
```
"""


@bot.event
async def on_ready():
    print("-----Logged in info-----")
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print("------------------------")


def _get_attrbution():
    return discord.File(
        "google-translate-attribution.png", filename="google-translate-attribution.png"
    )


@bot.command(name="man")
async def manual(ctx, opt=""):
    """manual command

    Example:
        `/man` - show how to use this tool.
        `/man [desc]` - show about this tool.
    """
    if opt == "desc":
        await ctx.channel.send(ABOUT_THIS_TOOL)
    else:
        await ctx.channel.send(MANUAL)


@bot.command(name="tran")
async def translate_message(ctx):
    # """Translate the posted message into target language.

    # Example:
    #     `/tran en ja Hello World, I'm Shingen Takeda.`
    # """
    # if ctx.author.bot:
    #     return

    # # ctx.message.content
    # text = " ".join(ctx.message.content.split(" ")[3:])
    # if len(text) > TRANSLATION_SOFT_LIMIT:
    #     text = text[:TRANSLATION_SOFT_LIMIT] + "…"

    # result = translate.Client().translate(
    #     text, source_language=src, target_language=target
    # )
    # msg = "`{author}` さんのメッセージを翻訳しました!!\n<{org_url}>\n```\n{translated}\n```".format(
    #     org_url=ctx.message.jump_url,
    #     author=ctx.author.display_name,
    #     translated=result["translatedText"],
    # )
    # await ctx.channel.send(unescape(msg), file=_get_attrbution())
    await ctx.channel.send("")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
