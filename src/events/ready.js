const { PREFIX } = require("../utils/config");
module.exports.run = async (client) => {
  console.log(`Ready At: ${client.readyAt}`);
  console.log(`Bot User: ${client.user.username} (${client.user.id})`);
  client.user.setActivity(`${PREFIX}help and ${PREFIX}play`, { type: "LISTENING" });
  console.log(`Ready.`);
};
