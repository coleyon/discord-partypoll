const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("cron")
    .setDescription("poll like command"),
  async execute(interaction) {
    await interaction.reply("not impl");
  },
};
