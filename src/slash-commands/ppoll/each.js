module.exports = {
  name: "each",
  description: "each poll",
  run: async (client, interaction, args) => {
    interaction.followUp({ content: client.ws.ping + "ms" });
  }
};
