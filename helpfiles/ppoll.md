# Poll Subcommand Help

```
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
```