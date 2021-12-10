const discord = require("discord.js");
const { Intents } = require("discord.js");
const { TOKEN } = require("./utils/config");

const client = new discord.Client({
  messageCacheLifetime: 60,
  fetchAllMembers: true,
  messageCacheMaxSize: 10,
  restTimeOffset: 0,
  restWsBridgetimeout: 100,
  allowedMentions: {
    parse: ["roles", "users", "everyone"],
    repliedUser: true
  },
  // https://discordjs.guide/popular-topics/partials.html#enabling-partials
  partials: ["MESSAGE", "CHANNEL", "REACTION"],
  // https://discordjs.guide/popular-topics/intents.html#privileged-intents
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.GUILD_MESSAGES,
    Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
    Intents.FLAGS.DIRECT_MESSAGES,
    Intents.FLAGS.DIRECT_MESSAGE_REACTIONS,
    Intents.FLAGS.GUILD_MEMBERS
  ]
});

client.commands = new discord.Collection();
client.aliases = new discord.Collection();
// client.slash = new discord.Collection();

// creating interaction events
["events", "slash"].forEach((handler) => {
  require(`./handlers/${handler}`)(client);
});

client.login(TOKEN);
