HELP_TEXT = """Party Poll

回答に人数制限をつけることができる Simple Poll のクローンです。
1件のPollにつき質問は最大10コまで指定できます。
人数制限をどの範囲にかけるかによって、次の2つのコマンドを使い分けて下さい。

[質問ごとに人数制限をしたい場合]
　コマンド構文:
　　質問1の回答上限を2に制限した質問: `/epoll "タイトル" "[2]質問1" "質問2"`
　コマンド例:
　　`/epoll "イベントだよ！" "[1] お花見" "[0] 桃狩り" "雪まつり"`

[質問全体に人数制限をしたい場合]
　コマンド構文:
　　全体の回答上限を2に制限した質問: `/tpoll "タイトル" 2 "質問1" "質問2"`
　コマンド例:
　　`/tpoll "イベントだよ！" 1 "お花見" "桃狩り" "雪まつり"`

[共通]
　　スペースを含む質問（例えば`[1] Question A`）はダブルクォーテーション `"` で囲む必要があります。
　　スペースを含まない質問（例えば`[1]Question-A`）はクォーテーションで囲まなくても大丈夫です。
　　人数制限を超えた回答があった場合は、回答が自動的に取り消されその旨をBotが教えてくれます。
"""

HELP_TEXT_TINY = """Party Poll

SYNOPSIS:
  `/epoll <TITLE> <[[LIMIT_OF_THE_QUESTION]]QUESTION>...<[[LIMIT_OF_THE_QUESTION]]QUESTION>`
  `/tpoll <TITLE> <LIMIT_OF_QUESTIONS> <QUESTION>...[QUESTION]`

OPTIONS:
  TITLE:
    Title text of the poll.

  LIMIT_OF_THE_QUESTION:
    Limit Number of reaction count of the question. (0-n)

  LIMIT_OF_QUESTIONS:
    Limit number of all reactions count of all question. (0-n)

  QUESTION:
    Each Question text of the poll.
"""
