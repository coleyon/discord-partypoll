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
client.slash = new discord.Collection();

// creating interaction events
["events", "slash", "commands"].forEach((handler) => {
  require(`./handlers/${handler}`)(client);
});

client.login(TOKEN);
