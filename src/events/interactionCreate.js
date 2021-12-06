module.exports.run = async (client, interaction) => {
  console.debug("interactionCreate");
  if (!interaction.isCommand()) {
    return;
  }
  // await interaction.deferReply({ ephemeral: false }).catch(() => {});
  const command = client.commands.get(interaction.commandName);
  if (!command) {
    return interaction.followUp({ content: "an Erorr" });
  }

  try {
    await command.execute(interaction);
  } catch (e) {
    interaction.followUp({ content: e.message });
  }
};
