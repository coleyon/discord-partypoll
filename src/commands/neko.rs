use serenity::framework::standard::{macros::command, CommandResult};
use serenity::model::prelude::*;
use serenity::prelude::*;

#[command]
#[description = "Meow!!"]
async fn neko(ctx: &Context, msg: &Message) -> CommandResult {
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
