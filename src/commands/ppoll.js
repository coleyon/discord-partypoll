const { SlashCommandBuilder } = require("@discordjs/builders");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("ppoll")
    .setDescription("Replies with Pong!")
    // ppoll each <TITLE> <[LIMIT_1]QUESTION_1> [[LIMIT_n]QUESTION_n ...]
    .addSubcommand((subcommand) =>
      subcommand
        .setName("each")
        .setDescription("each mode")
        .addStringOption((option) =>
          option
            .setName("title")
            .setDescription("Polling Title")
            .setRequired(true)
        )
        .addStringOption(
          // TBD how2impl original parser
          (option) =>
            option
              .setName("limit")
              .setDescription("Total Limit")
              .setRequired(true)
        )
    )
    // ppoll total <TITLE> <TOTAL_LIMIT> [QUESTION_n ...]
    .addSubcommand((subcommand) =>
      subcommand
        .setName("total")
        .setDescription("total mode")
        .addStringOption((option) =>
          option
            .setName("title")
            .setDescription("Polling Title")
            .setRequired(true)
        )
        .addIntegerOption((option) =>
          option
            .setName("limit")
            .setDescription("Total Limit")
            .setRequired(true)
        )
        .addStringOption(
          // TBD how2impl original parser
          (option) =>
            option
              .setName("question")
              .setDescription("Polling Title")
              .setRequired(true)
        )
    ),
  async execute(interaction) {
    await interaction.reply("ppoll");
  },
};
