const { MessageActionRow } = require("discord.js");

async function buttonInteraction(client, interaction) {
  const customId = interaction.customID;
  const channel = interaction.channel;
  const reactioner = interaction.user;
  const component = interaction.component;

  await interaction.component.setStyle("DANGER");
  await interaction.editReply({
    components: [new MessageActionRow().addComponents(interaction.component)]
  });
  // await interaction.Update({
  //   components: [new MessageActionRow().addComponents(interaction.component)]
  // });

  console.debug("button pushed.");
}

module.exports.run = async (client, interaction) => {
  console.debug("interactionCreate");
  if (interaction.isButton()) {
    await interaction.deferUpdate();
    await buttonInteraction(client, interaction);
  }
  if (interaction.isCommand()) {
    await interaction.deferReply();
    // await interaction.deferReply({ ephemeral: false }).catch(() => {});
    const command = client.commands.get(interaction.commandName);
    if (!command) {
      return interaction.followUp({ content: "an Erorr" });
    }

    try {
      interaction.channel.sendTyping();
      await command.execute(interaction);
    } catch (e) {
      interaction.followUp({ content: e.message });
    }
  }
  return;
};
