const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("cron")
    .setDescription("cron cmd")
    .addStringOption((option) => option.setName("crontab").setDescription("crontab text")),
  async execute(interaction) {
    const value = interaction.options.getString("crontab");
    if (value) {
      return interaction.reply(`The options value is: \`${value}\``);
    } else {
      return interaction.reply("No option was provided!");
    }
  }
};
