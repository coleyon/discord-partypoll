module.exports.run = async (client) => {
  console.debug("destroy");
  client.user.setPresence({ activities: [{ name: "Closing...", type: "Playing" }], status: "dnd" });
  console.log("closing...");
};
