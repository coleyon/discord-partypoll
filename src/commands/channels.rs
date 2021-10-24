use serenity::prelude::*;
use serenity::{
    framework::standard::{
        macros::{command, group},
        CommandResult,
    },
    model::channel::Message,
};

#[group]
#[prefixes("ch", "channel", "channels")]
#[description = "A group with commands providing a reply."]
#[summary = "Replying commands."]
#[default_command(all_channel)]
#[commands(all_channel)]
struct Channels;

#[command]
#[description = "Gets channel list."]
async fn all_channel(ctx: &Context, msg: &Message) -> CommandResult {
    let guild_id = *msg.guild_id.unwrap().as_u64();
    let channels = ctx.http.get_channels(guild_id).await.unwrap();

    for chan in channels {
        msg.channel_id
            .say(&ctx.http, format!("{}", chan.name))
            .await?;
    }
    Ok(())
}
