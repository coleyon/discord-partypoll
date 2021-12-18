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
    choice.value = choice.value.replaceAll(",", "，");
    if (Number.isInteger(limit.value) && choice.value) {
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
        .addStringOption((option) => option.setName("title").setDescription("タイトル").setRequired(true))
        .addIntegerOption((option) => option.setName("limit").setDescription("回答制限").setRequired(true))
        .addStringOption((option) => option.setName("choice1").setDescription("回答1").setRequired(true))
        .addStringOption((option) => option.setName("choice2").setDescription("回答2"))
        .addStringOption((option) => option.setName("choice3").setDescription("回答3"))
        .addStringOption((option) => option.setName("choice4").setDescription("回答4"))
        .addStringOption((option) => option.setName("choice5").setDescription("回答5"))
        .addStringOption((option) => option.setName("choice6").setDescription("回答6"))
        .addStringOption((option) => option.setName("choice7").setDescription("回答7"))
        .addStringOption((option) => option.setName("choice8").setDescription("回答8"))
        .addStringOption((option) => option.setName("choice9").setDescription("回答9"))
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("each")
        .setDescription("each poll")
        .addStringOption((option) => option.setName("title").setDescription("タイトル").setRequired(true))
        .addIntegerOption((option) => option.setName("limit1").setDescription("制限1").setRequired(true))
        .addStringOption((option) => option.setName("choice1").setDescription("回答1").setRequired(true))
        .addIntegerOption((option) => option.setName("limit2").setDescription("制限2"))
        .addStringOption((option) => option.setName("choice2").setDescription("回答2"))
        .addIntegerOption((option) => option.setName("limit3").setDescription("制限3"))
        .addStringOption((option) => option.setName("choice3").setDescription("回答3"))
        .addIntegerOption((option) => option.setName("limit4").setDescription("制限4"))
        .addStringOption((option) => option.setName("choice4").setDescription("回答4"))
        .addIntegerOption((option) => option.setName("limit5").setDescription("制限5"))
        .addStringOption((option) => option.setName("choice5").setDescription("回答5"))
        .addIntegerOption((option) => option.setName("limit6").setDescription("制限6"))
        .addStringOption((option) => option.setName("choice6").setDescription("回答6"))
        .addIntegerOption((option) => option.setName("limit7").setDescription("制限7"))
        .addStringOption((option) => option.setName("choice7").setDescription("回答7"))
        .addIntegerOption((option) => option.setName("limit8").setDescription("制限8"))
        .addStringOption((option) => option.setName("choice8").setDescription("回答8"))
        .addIntegerOption((option) => option.setName("limit9").setDescription("制限9"))
        .addStringOption((option) => option.setName("choice9").setDescription("回答9"))
    ),
  async execute(interaction) {
    console.debug("entire execute");
    const subCmdType = interaction.options.getSubcommand();
    if (subCmdType === "total") {
      await makeTotalPoll(interaction);
      // return await interaction.editReply("Total limited polling.");
    } else if (subCmdType === "each") {
      await makeEachPoll(interaction);
      // return await interaction.editReply("Each limited polling.");
    }
    // return await interaction.editReply("入力が不足しています.");
  }
};
