const discord = require("discord.js");
const { Intents } = require("discord.js");
const { TOKEN } = require("./utils/config");

const client = new discord.Client({
  messageCacheLifetime: 60,
  fetchAllMembers: false,
  messageCacheMaxSize: 10,
  restTimeOffset: 0,
  restWsBridgetimeout: 100,
  allowedMentions: {
    parse: ["roles", "users", "everyone"],
    repliedUser: true
  },
  partials: ["MESSAGE", "CHANNEL", "REACTION"],
  intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES, Intents.FLAGS.GUILD_MESSAGE_REACTIONS]
});

client.commands = new discord.Collection();
client.aliases = new discord.Collection();
// client.slash = new discord.Collection();

// creating interaction events
["events", "slash"].forEach((handler) => {
  require(`./handlers/${handler}`)(client);
});

// client.on("interactionCreate", async (interaction) => {
//   if (!interaction.isCommand()) {
//     return;
//   }
//   const command = client.commands.get(interaction.commandName);
//   if (!command) {
//     return;
//   }
//   try {
//     await command.execute(interaction);
//   } catch (error) {
//     console.error(error);
//     return interaction.reply({
//       content: "There was an error while executing this command!",
//       ephemeral: true
//     });
//   }
// });

client.login(TOKEN);
