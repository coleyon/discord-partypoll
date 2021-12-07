const { SlashCommandBuilder } = require("@discordjs/builders");

/**
 * @link {https://github.com/coleyon/discord-partypoll/blob/67d296fa23ed9e297511f46c71f4b96689929495/cogs/ppoll.py#L163} interaction
 */
async function makeTotalPoll(interaction) {
  const title = interaction.options.getString("title");
  const limit = interaction.options.getInteger("limit");
  const choices = [];
  for (option of interaction.options._hoistedOptions.slice(2)) {
    if (option.value) {
      choices.push(option.value);
    }
  }
  console.log("");
}

async function makeEachPoll(interaction) {}

/**
 * /ppoll total 10名分の予算がある3種のイベント 10 お花見 BBQ 鍋パー
 */
module.exports = {
  data: new SlashCommandBuilder()
    .setName("ppoll")
    .setDescription("Make poll")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("total")
        .setDescription("total poll")
        .addStringOption((option) => option.setName("title").setDescription("title text").setRequired(true))
        .addIntegerOption((option) => option.setName("limit").setDescription("limit").setRequired(true))
        .addStringOption((option) => option.setName("choice0").setDescription("text").setRequired(true))
        .addStringOption((option) => option.setName("choice1").setDescription("text"))
        .addStringOption((option) => option.setName("choice2").setDescription("text"))
        .addStringOption((option) => option.setName("choice3").setDescription("text"))
        .addStringOption((option) => option.setName("choice4").setDescription("text"))
        .addStringOption((option) => option.setName("choice5").setDescription("text"))
        .addStringOption((option) => option.setName("choice6").setDescription("text"))
        .addStringOption((option) => option.setName("choice7").setDescription("text"))
        .addStringOption((option) => option.setName("choice8").setDescription("text"))
        .addStringOption((option) => option.setName("choice9").setDescription("text"))
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("each")
        .setDescription("each poll")
        .addStringOption((option) => option.setName("title").setDescription("title text").setRequired(true))
        .addIntegerOption((option) => option.setName("limit0").setDescription("limit").setRequired(true))
        .addStringOption((option) => option.setName("choice0").setDescription("text").setRequired(true))
        .addIntegerOption((option) => option.setName("limit1").setDescription("limit"))
        .addStringOption((option) => option.setName("choice1").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit2").setDescription("limit"))
        .addStringOption((option) => option.setName("choice2").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit3").setDescription("limit"))
        .addStringOption((option) => option.setName("choice3").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit4").setDescription("limit"))
        .addStringOption((option) => option.setName("choice4").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit5").setDescription("limit"))
        .addStringOption((option) => option.setName("choice5").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit6").setDescription("limit"))
        .addStringOption((option) => option.setName("choice6").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit7").setDescription("limit"))
        .addStringOption((option) => option.setName("choice7").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit8").setDescription("limit"))
        .addStringOption((option) => option.setName("choice8").setDescription("text"))
        .addIntegerOption((option) => option.setName("limit9").setDescription("limit"))
        .addStringOption((option) => option.setName("choice9").setDescription("text"))
    ),
  async execute(interaction) {
    const subCmdType = interaction.options.getSubcommand();
    if (subCmdType === "total") {
      await makeTotalPoll(interaction);
    } else if (subCmdType === "each") {
      await makeEachPoll(interaction);
    } else {
      return interaction.reply("No option was provided!");
    }
  }
};
