use serenity::prelude::*;
use serenity::{
    framework::standard::{
        macros::{command, group},
        CommandResult,
    },
    model::channel::Message,
};

#[group]
#[prefixes("neko", "cat")]
#[description = "A group with commands providing a reply."]
#[summary = "Replying commands."]
#[default_command(default)]
#[commands(default)]
struct Neko;

#[command]
#[description = "Meow!!"]
async fn default(ctx: &Context, msg: &Message) -> CommandResult {
    msg.channel_id
        .say(
            &ctx.http,
            format!(
                "{} meow!, were new bot written in rustlang.",
                msg.author.mention()
            ),
        )
        .await?;
    Ok(())
}
