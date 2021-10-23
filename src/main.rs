mod commands;

use std::env;
use std::{collections::HashSet, fs::File, io::BufReader, usize};

use serenity::async_trait;
use serenity::framework::standard::{
    help_commands,
    macros::{group, help},
    Args, CommandGroup, CommandResult, HelpOptions,
};
use serenity::framework::StandardFramework;
use serenity::model::{channel::Message, gateway::Ready, id::UserId};
use serenity::prelude::{Client, Context, EventHandler};

use serde::{Deserialize, Serialize};
use serde_json::Result;

use commands::{channels::*, neko::*};

// Handler構造体。取得したいイベントを実装する
struct Handler;

#[async_trait]
impl EventHandler for Handler {
    // Botが起動したときに走る処理
    async fn ready(&self, _: Context, ready: Ready) {
        println!("{} is connected!", ready.user.name);
    }
}

#[help]
#[individual_command_tip = "this is help command description..."]
#[strikethrough_commands_tip_in_guild = ""]
async fn my_help(
    ctx: &Context,
    msg: &Message,
    args: Args,
    help_options: &'static HelpOptions,
    groups: &[&'static CommandGroup],
    owners: HashSet<UserId>,
) -> CommandResult {
    // _ は使用しない返り値を捨てることを明示している
    let _ = help_commands::with_embeds(ctx, msg, args, help_options, groups, owners).await;
    // 空のタプルをreturn（仕様）
    // Rustでは`;`なしの行は値としてreturnすることを表す
    // return Ok(()); と同義
    Ok(())
}

#[group]
#[description("汎用コマンド")]
#[summary("一般")]
#[commands(neko, all_channels)]
struct General;

#[derive(Serialize, Deserialize)]
struct Token {
    token: String,
}

#[tokio::main]
async fn main() {
    // コマンド系の設定
    let framework = StandardFramework::new()
        .configure(|c| c.prefix("/")) // コマンドプレフィックス
        .help(&MY_HELP) // ヘルプコマンドを追加
        .group(&GENERAL_GROUP); // general を追加するには,GENERAL_GROUP とグループ名をすべて大文字にする

    // Creates bot client
    let bot_token: String = env::var("DISCORD_BOT_TOKEN").expect("Bot token not found.");
    let mut client = Client::builder(&bot_token)
        .event_handler(Handler) // 取得するイベント
        .framework(framework) // コマンドを登録
        .await
        .expect("Err creating client"); // エラーハンドリング

    // main loop, upstarting the bot.
    if let Err(why) = client.start().await {
        println!("Client error: {:?}", why);
    }
}
