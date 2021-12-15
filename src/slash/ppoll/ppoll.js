const { MessageEmbed, MessageActionRow, MessageButton } = require("discord.js");
const { SlashCommandBuilder } = require("@discordjs/builders");

/**
 * @link https://github.com/coleyon/discord-partypoll/blob/67d296fa23ed9e297511f46c71f4b96689929495/cogs/ppoll.py#L163
 */
async function makeTotalPoll(interaction) {
  console.debug("entire makeTotalPoll");
  const title = interaction.options.getString("title");
  const limit = interaction.options.getInteger("limit");

  const embeds = new MessageEmbed()
    .setColor("#FF5733")
    .setTitle(`[質問全体での人数制限]`)
    .setDescription(title)
    .setFooter(`0/${limit}`);
  const buttons = new MessageActionRow();
  for (option of interaction.options._hoistedOptions.slice(2)) {
    if (option.value) {
      buttons.addComponents(
        new MessageButton()
          .setCustomId(`${interaction.id}_${option.name}`)
          .setLabel(option.value)
          .setStyle("SUCCESS")
      );
      embeds.addField(option.value, "-", true);
    }
  }

  await interaction.channel.send({ embeds: [embeds], components: [buttons] });
  console.log("OK");
}

/**
 * @link https://github.com/coleyon/discord-partypoll/blob/67d296fa23ed9e297511f46c71f4b96689929495/cogs/ppoll.py#L182
 */
async function makeEachPoll(interaction) {
  console.debug("entire makeEachPoll");
  console.debug("entire makeTotalPoll");
  const title = interaction.options.getString("title");

  const embeds = new MessageEmbed().setColor("#FF5733").setTitle(`[質問毎の人数制限]`).setDescription(title);
  const buttons = new MessageActionRow();
  const split = (array, n) =>
    array.reduce((a, c, i) => (i % n == 0 ? [...a, [c]] : [...a.slice(0, -1), [...a[a.length - 1], c]]), []);

  for (optionSet of split(interaction.options._hoistedOptions.slice(1), 2)) {
    const limit = optionSet[0];
    const choice = optionSet[1];
    if (limit.value && choice.value) {
      buttons.addComponents(
        new MessageButton()
          .setCustomId(`${interaction.id}_${choice.name}`)
          .setLabel(choice.value)
          .setStyle("SUCCESS")
      );
      embeds.addField(`${choice.value}, 0/${limit.value}`, "-", true);
    }
  }

  await interaction.channel.send({ embeds: [embeds], components: [buttons] });
  console.log("OK");
}

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
    console.debug("entire execute");
    const subCmdType = interaction.options.getSubcommand();
    if (subCmdType === "total") {
      await makeTotalPoll(interaction);
      return await interaction.editReply("Total limited polling.");
    } else if (subCmdType === "each") {
      await makeEachPoll(interaction);
      return await interaction.editReply("Each limited polling.");
    }
    return await interaction.editReply("入力が不足しています.");
  }
};
