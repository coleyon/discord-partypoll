const { SlashCommandBuilder } = require("@discordjs/builders");

export const data = new SlashCommandBuilder()
  .setName("each")
  .setName("each")
  .setDescription("each mode")
  .addStringOption((option) => option.setName("title").setDescription("Polling Title").setRequired(true))
  .addStringOption(
    // TBD how2impl original parser
    (option) => option.setName("limit").setDescription("Total Limit").setRequired(true)
  );
export async function execute(interaction) {
  await interaction.reply("total");
}
