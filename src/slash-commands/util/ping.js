import { SlashCommandBuilder } from "@discordjs/builders";

export const data = new SlashCommandBuilder().setName("ping").setDescription("Replies with Pong!");
export async function execute(interaction) {
  await interaction.reply("Pong!");
}

module.exports = {
  name: "ping",
  description: "chekling ping of bot",
  run: async (client, interaction, args) => {
    interaction.followUp({ content: client.ws.ping + "ms" });
  }
};
