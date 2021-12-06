module.exports.run = async (client) => {
  console.log(`Ready At: ${client.readyAt}`);
  console.log(`Bot User: ${client.user.username} (${client.user.id})`);
  // client.user.setActivity("Wating...", { type: "Playing" });
  console.log(`Ready.`);
  client.user.setPresence({ activities: [{ name: "Wating...", type: "Playing" }], status: "online" });
};
