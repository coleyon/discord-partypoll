use serenity::prelude::*;
use serenity::{
    framework::standard::{
        macros::{command, group},
        CommandResult,
    },
    model::channel::Message,
};

#[group]
#[prefixes("partypoll", "ppoll")]
#[description = "A group with commands providing a party poll"]
#[summary = "Clone of the Simple Poll bot extended for recruiting party members."]
#[default_command(default)]
#[commands(default)]
struct PartyPoll;

#[command]
#[description = "Puts reply with mention"]
async fn default(ctx: &Context, msg: &Message) -> CommandResult {
    // TBD implementation
    msg.reply_mention(&ctx.http, "This is partypoll command.")
        .await?;
    Ok(())
}
