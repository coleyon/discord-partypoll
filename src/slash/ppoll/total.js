const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("total")
    .setDescription("total poll")
    .addStringOption((option) => option.setName("total").setDescription("total text")),
  async execute(interaction) {
    const value = interaction.options.getString("total");
    if (value) return interaction.reply(`The options value is: \`${value}\``);
    return interaction.reply("No option was provided!");
  }
};
