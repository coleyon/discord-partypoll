module.exports = {
  name: "total",
  description: "total poll",
  run: async (client, interaction, args) => {
    interaction.followUp({ content: client.ws.ping + "ms" });
  }
};
