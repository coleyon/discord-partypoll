const { MessageActionRow, MessageEmbed } = require("discord.js");

async function buttonInteraction(client, interaction) {
  // const customId = interaction.customID;
  // const channel = interaction.channel;
  // const reactioner = interaction.user;
  // const component = interaction.component;
  // const orgComponents = interaction.message.components[0];
  // const currentComponent = orgComponents.components.filter((c) => c.customId === interaction.customId);
  // const orgFields = interaction.message.embeds[0].fields;
  // const currentField = orgFields.filter((f) => f.name === interaction.component.label);

  await interaction.message.edit(Date.now().toString());

  // client.channels.cache
  //   .get(interaction.channelId)
  //   .fetchMessage(interaction.message.id)
  //   .then((msg) => msg.edit("Done!"));

  // // TODO ボタンの状態とFieldの内容を
  // await interaction.component.setStyle("DANGER");
  // await interaction.embeds.setFields(orgFields);
  // await interaction.editReply({
  //   components: [new MessageActionRow().addComponents(interaction.component)],
  //   embeds: [embeds]
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
      return interaction.followUp({ content: "Command not found." });
    }

    try {
      await command.execute(interaction);
    } catch (e) {
      interaction.followUp({ content: e.message });
    }
  }
  return;
};
