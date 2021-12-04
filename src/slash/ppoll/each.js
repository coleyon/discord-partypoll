const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("each")
    .setDescription("each poll")
    .addStringOption((option) => option.setName("each").setDescription("each text")),
  async execute(interaction) {
    const value = interaction.options.getString("each");
    if (value) return interaction.reply(`The options value is: \`${value}\``);
    return interaction.reply("No option was provided!");
  }
};
