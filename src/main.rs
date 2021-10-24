mod commands;

use std::{
    collections::{HashMap, HashSet},
    env,
    fmt::Write,
    sync::Arc,
};

use commands::{channels::*, cron::*, neko::*, ppoll::*, reply::*};
use serde::{Deserialize, Serialize};
use serenity::prelude::*;
use serenity::{
    async_trait,
    client::bridge::gateway::{GatewayIntents, ShardId, ShardManager},
    collector::{EventCollectorBuilder, MessageCollectorBuilder, ReactionCollectorBuilder},
    framework::standard::{
        buckets::{LimitedFor, RevertBucket},
        help_commands,
        macros::{check, command, group, help, hook},
        Args, CommandGroup, CommandOptions, CommandResult, DispatchError, HelpOptions, Reason,
        StandardFramework,
    },
    futures::{future::BoxFuture, stream::StreamExt},
    http::Http,
    model::{
        channel::{Channel, Message},
        event::ResumedEvent,
        gateway::Ready,
        id::UserId,
        permissions::Permissions,
        prelude::*,
    },
    prelude::*,
    utils::{content_safe, ContentSafeOptions},
    FutureExt,
};
use tokio::sync::Mutex;
use tracing::{debug, info, instrument};

struct ShardManagerContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}

struct CommandCounter;

impl TypeMapKey for CommandCounter {
    type Value = HashMap<String, u64>;
}

#[group("collector")]
struct Collector;

struct Handler;
#[async_trait]
impl EventHandler for Handler {
    // Botが起動したときに走る処理
    async fn ready(&self, _: Context, ready: Ready) {
        info!("{} is connected!", ready.user.name);
    }

    async fn reaction_add(&self, _ctx: Context, _add_reaction: Reaction) {
        info!("{} added.", _add_reaction.emoji);
    }
    async fn reaction_remove(&self, _ctx: Context, _removed_reaction: Reaction) {
        info!("{} removed.", _removed_reaction.emoji);
    }

    // For instrument to work, all parameters must implement Debug.
    //
    // Handler doesn't implement Debug here, so we specify to skip that argument.
    // Context doesn't implement Debug either, so it is also skipped.
    #[instrument(skip(self, _ctx))]
    async fn resume(&self, _ctx: Context, resume: ResumedEvent) {
        // Log at the DEBUG level.
        //
        // In this example, this will not show up in the logs because DEBUG is
        // below INFO, which is the set debug level.
        debug!("Resumed; trace: {:?}", resume.trace);
    }
}

#[group]
#[description("Native (Non grouped) commands of this Bot.")]
#[summary("Basic commands")]
#[commands(about)]
struct General;

#[hook]
#[instrument]
async fn before(ctx: &Context, msg: &Message, command_name: &str) -> bool {
    // command input logger
    debug!(
        "Got command '{}' by user '{}'",
        command_name, msg.author.name
    );
    let mut data = ctx.data.write().await;
    let counter = data
        .get_mut::<CommandCounter>()
        .expect("Expected CommandCounter in TypeMap.");
    let entry = counter.entry(command_name.to_string()).or_insert(0);
    *entry += 1;
    true
}

#[hook]
#[instrument]
async fn after(_ctx: &Context, _msg: &Message, command_name: &str, command_result: CommandResult) {
    // command end logger
    debug!(
        "Finish command '{}' by user '{}': {}",
        command_name, _msg.author.name, _msg.content
    );
    match command_result {
        Ok(()) => debug!("Processed command '{}'", command_name),
        Err(why) => debug!("Command '{}' returned error {:?}", command_name, why),
    }
}

#[hook]
#[instrument]
async fn unknown_command(_ctx: &Context, _msg: &Message, unknown_command_name: &str) {
    debug!("Could not find command named '{}'", unknown_command_name);
}

#[hook]
#[instrument]
async fn normal_message(_ctx: &Context, msg: &Message) {
    debug!("Found message input not a command '{}'", msg.content);
}

#[hook]
#[instrument]
async fn delay_action(ctx: &Context, msg: &Message) {
    debug!("Found message input not a command '{}'", msg.content);
    let _ = msg.react(ctx, '⏱').await;
}

#[hook]
async fn dispatch_error(ctx: &Context, msg: &Message, error: DispatchError) {
    if let DispatchError::Ratelimited(info) = error {
        // We notify them only once.
        if info.is_first_try {
            let _ = msg
                .channel_id
                .say(
                    &ctx.http,
                    &format!("Try this again in {} seconds.", info.as_secs()),
                )
                .await;
        }
    }
}

fn _dispatch_error_no_macro<'fut>(
    ctx: &'fut mut Context,
    msg: &'fut Message,
    error: DispatchError,
) -> BoxFuture<'fut, ()> {
    async move {
        if let DispatchError::Ratelimited(info) = error {
            if info.is_first_try {
                let _ = msg
                    .channel_id
                    .say(
                        &ctx.http,
                        &format!("Try this again in {} seconds.", info.as_secs()),
                    )
                    .await;
            }
        };
    }
    .boxed()
}

#[help]
#[individual_command_tip = "If you want more information about a specific command, just pass the command as argument."]
#[command_not_found_text = "Could not find: `{}`."]
#[max_levenshtein_distance(3)]
#[indention_prefix = "+"]
#[lacking_permissions = "Hide"]
#[lacking_role = "Hide"]
#[wrong_channel = "Hide"]
async fn my_help(
    context: &Context,
    msg: &Message,
    args: Args,
    help_options: &'static HelpOptions,
    groups: &[&'static CommandGroup],
    owners: HashSet<UserId>,
) -> CommandResult {
    let _ = help_commands::with_embeds(context, msg, args, help_options, groups, owners).await;
    Ok(())
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    // get Bot token
    let bot_token = env::var("DISCORD_BOT_TOKEN").expect("Bot token not found.");

    // We will fetch your bot's owners and id
    let http = Http::new_with_token(&bot_token);
    let (owners, bot_id) = match http.get_current_application_info().await {
        Ok(info) => {
            let mut owners = HashSet::new();
            if let Some(team) = info.team {
                owners.insert(team.owner_user_id);
            } else {
                owners.insert(info.owner.id);
            }
            match http.get_current_user().await {
                Ok(bot_id) => (owners, bot_id.id),
                Err(why) => panic!("Could not access the bot id: {:?}", why),
            }
        }
        Err(why) => panic!("Could not access application info: {:?}", why),
    };

    // create commands
    let cmd_prefix = env::var("CMD_PREFIX").expect("Prefix not set.");
    let framework = StandardFramework::new()
        .configure(|c| {
            c.with_whitespace(true)
                .on_mention(Some(bot_id))
                .prefix(&cmd_prefix)
                .delimiters(vec![", ", ","])
                .owners(owners)
        })
        .before(before)
        .after(after)
        .unrecognised_command(unknown_command)
        .normal_message(normal_message)
        .on_dispatch_error(dispatch_error)
        .bucket("emoji", |b| b.delay(5))
        .await
        .bucket("complicated", |b| {
            b.limit(2)
                .time_span(30)
                .delay(5)
                .limit_for(LimitedFor::Channel)
                .await_ratelimits(1)
                .delay_action(delay_action)
        })
        .await
        .help(&MY_HELP)
        .group(&GENERAL_GROUP)
        .group(&NEKO_GROUP)
        .group(&CHANNELS_GROUP)
        .group(&PARTYPOLL_GROUP)
        .group(&CRON_GROUP)
        .group(&REPLY_GROUP);

    // create bot client
    let mut client = Client::builder(&bot_token)
        .event_handler(Handler)
        .framework(framework)
        .intents(GatewayIntents::all())
        .type_map_insert::<CommandCounter>(HashMap::default())
        .await
        .expect("Err creating client");

    {
        let mut data = client.data.write().await;
        data.insert::<ShardManagerContainer>(Arc::clone(&client.shard_manager));
    }

    // upstart the bot
    if let Err(why) = client.start().await {
        tracing::info!("Client error: {:?}", why);
    }
}

#[command]
#[bucket = "complicated"]
async fn commands(ctx: &Context, msg: &Message) -> CommandResult {
    let mut contents = "Commands used:\n".to_string();

    let data = ctx.data.read().await;
    let counter = data
        .get::<CommandCounter>()
        .expect("Expected CommandCounter in TypeMap.");

    for (k, v) in counter {
        writeln!(contents, "- {name}: {amount}", name = k, amount = v)?;
    }

    msg.channel_id.say(&ctx.http, &contents).await?;

    Ok(())
}

#[check]
#[name = "Owner"]
async fn owner_check(
    _: &Context,
    msg: &Message,
    _: &mut Args,
    _: &CommandOptions,
) -> Result<(), Reason> {
    debug!("entered owner_check, msg.author.id is {:?}.", msg.author.id);
    if msg.author.id != 7 {
        return Err(Reason::User("Lacked owner permission".to_string()));
    }

    Ok(())
}

#[command]
async fn about(ctx: &Context, msg: &Message) -> CommandResult {
    msg.channel_id
        .say(&ctx.http, "Clone of the Simple Poll bot extended for recruiting party member.\nhttps://github.com/coleyon/discord-partypoll")
        .await?;
    Ok(())
}
