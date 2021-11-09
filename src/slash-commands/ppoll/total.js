const { SlashCommandBuilder } = require("@discordjs/builders");

export const data = new SlashCommandBuilder()
  .setName("total")
  .setDescription("total mode")
  .addStringOption((option) => option.setName("title").setDescription("Polling Title").setRequired(true))
  .addIntegerOption((option) => option.setName("limit").setDescription("Total Limit").setRequired(true))
  .addStringOption(
    // TBD how2impl original parser
    (option) => option.setName("question").setDescription("Polling Title").setRequired(true)
  );
export async function execute(interaction) {
  await interaction.reply("total");
}
