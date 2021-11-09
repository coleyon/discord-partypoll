const { SlashCommandBuilder } = require("@discordjs/builders");

export const data = new SlashCommandBuilder().setName("cron").setDescription("poll like command");
export async function execute(interaction) {
  await interaction.reply("not impl");
}
