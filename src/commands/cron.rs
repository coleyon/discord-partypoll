use serenity::prelude::*;
use serenity::{
    framework::standard::{
        macros::{command, group},
        CommandResult,
    },
    model::channel::Message,
};

#[group]
#[prefixes("cron")]
#[description = "A group with commands providing a cron."]
#[summary = "Cron like command execution scheduler."]
#[default_command(default)]
#[commands(default)]
struct Cron;

#[command]
#[description = "Puts reply with mention"]
async fn default(ctx: &Context, msg: &Message) -> CommandResult {
    // TBD implementation
    msg.reply_mention(&ctx.http, "this is cron command.")
        .await?;
    Ok(())
}
