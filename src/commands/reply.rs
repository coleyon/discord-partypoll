use serenity::prelude::*;
use serenity::{
    framework::standard::{
        macros::{command, group},
        CommandResult,
    },
    model::channel::Message,
};

#[group]
#[prefixes("reply", "rp")]
#[description = "A group with commands providing a reply."]
#[summary = "Replying commands."]
#[default_command(default)]
#[commands(default, without_mention)]
struct Reply;

#[command]
#[description = "Puts reply with mention"]
async fn default(ctx: &Context, msg: &Message) -> CommandResult {
    msg.reply_mention(&ctx.http, "reply with mention test")
        .await?;
    Ok(())
}

#[command]
#[description = "Puts reply"]
async fn without_mention(ctx: &Context, msg: &Message) -> CommandResult {
    msg.reply(&ctx.http, "simple reply test").await?;
    Ok(())
}
