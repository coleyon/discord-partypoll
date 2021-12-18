const { MessageEmbed, MessageActionRow, MessageButton } = require("discord.js");
const { SlashCommandBuilder } = require("@discordjs/builders");

async function makeTotalPoll(interaction) {
  console.debug("entire makeTotalPoll");
  const title = interaction.options.getString("title");
  const limit = interaction.options.getInteger("limit");

  const embeds = new MessageEmbed()
    .setColor("#1F618D")
    .setTitle(`[アンケート全体での人数制限]`)
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

async function makeEachPoll(interaction) {
  console.debug("entire makeEachPoll");
  console.debug("entire makeTotalPoll");
  const title = interaction.options.getString("title");

  const embeds = new MessageEmbed()
    .setColor("#FF5733")
    .setTitle(`[アンケート毎の人数制限]`)
    .setDescription(title);
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
    .setName("survey")
    .setDescription("アンケートをはじめる")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("total")
        .setDescription("全体にわたる回答人数制限があるアンケート")
        .addStringOption((option) =>
          option.setName("title").setDescription("アンケートのタイトル").setRequired(true)
        )
        .addIntegerOption((option) =>
          option.setName("limit").setDescription("回答人数制限").setRequired(true)
        )
        .addStringOption((option) =>
          option.setName("choice1").setDescription("アンケート1").setRequired(true)
        )
        .addStringOption((option) => option.setName("choice2").setDescription("アンケート2"))
        .addStringOption((option) => option.setName("choice3").setDescription("アンケート3"))
        .addStringOption((option) => option.setName("choice4").setDescription("アンケート4"))
        .addStringOption((option) => option.setName("choice5").setDescription("アンケート5"))
        .addStringOption((option) => option.setName("choice6").setDescription("アンケート6"))
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("each")
        .setDescription("調査項目それぞれに個別の回答人数制限があるアンケート")
        .addStringOption((option) =>
          option.setName("title").setDescription("アンケートのタイトル").setRequired(true)
        )
        .addIntegerOption((option) =>
          option.setName("limit1").setDescription("アンケートへの回答人数制限1").setRequired(true)
        )
        .addStringOption((option) =>
          option.setName("choice1").setDescription("アンケート1").setRequired(true)
        )
        .addIntegerOption((option) => option.setName("limit2").setDescription("アンケートへの回答人数制限2"))
        .addStringOption((option) => option.setName("choice2").setDescription("アンケート2"))
        .addIntegerOption((option) => option.setName("limit3").setDescription("アンケートへの回答人数制限3"))
        .addStringOption((option) => option.setName("choice3").setDescription("アンケート3"))
        .addIntegerOption((option) => option.setName("limit4").setDescription("アンケートへの回答人数制限4"))
        .addStringOption((option) => option.setName("choice4").setDescription("アンケート4"))
        .addIntegerOption((option) => option.setName("limit5").setDescription("アンケートへの回答人数制限5"))
        .addStringOption((option) => option.setName("choice5").setDescription("アンケート5"))
        .addIntegerOption((option) => option.setName("limit6").setDescription("アンケートへの回答人数制限6"))
        .addStringOption((option) => option.setName("choice6").setDescription("アンケート6"))
    ),
  async execute(interaction) {
    console.debug("entire execute");
    const subCmdType = interaction.options.getSubcommand();
    if (subCmdType === "total") {
      await makeTotalPoll(interaction);
    } else if (subCmdType === "each") {
      await makeEachPoll(interaction);
    }
  }
};
