const { MessageActionRow, MessageEmbed } = require("discord.js");

async function totalButtonInteraction(client, interaction) {
  // gets common info
  const guild = client.guilds.cache.get(interaction.message.guildId);
  const reactioner = guild.members.cache.get(interaction.user.id);
  let reactionerNick = reactioner ? reactioner.displayName : reactioner.name;
  reactionerNick = reactionerNick.replaceAll(",", "，");
  const embeds = new MessageEmbed(interaction.message.embeds[0]);
  const currentCount = parseInt(embeds.footer.text.split("/")[0]);
  const limitCount = parseInt(embeds.footer.text.split("/")[1]);
  // check is answered by the user
  let alreadyPressed = false;
  for (field of embeds.fields) {
    if (field.value === "-") {
      continue;
    }
    if (field.value.includes(reactionerNick)) {
      alreadyPressed = true;
      break;
    }
  }
  if (currentCount < 1 && alreadyPressed) {
    console.error(":x: something wrong field value.");
    return;
  }
  // find index of pressed field
  let fieldIdx = -1;
  for (var i = 0; i < embeds.fields.length; i += 1) {
    if (embeds.fields[i]["name"] === interaction.component.label) {
      fieldIdx = i;
    }
  }

  if (alreadyPressed) {
    // remove user name from field
    const orgReactions = embeds.fields[fieldIdx].value.split(",");
    if (!orgReactions.includes(reactionerNick)) {
      return await interaction.user.send(`:x:${interaction.message.url}\n同時に複数の回答はできません。`);
    }
    let reactioners = [];
    reactioners = embeds.fields[fieldIdx].value.split(",").filter((e) => e !== reactionerNick);
    if (reactioners.length) {
      embeds.fields[fieldIdx].value = reactioners.join(",");
    } else {
      embeds.fields[fieldIdx].value = "-";
    }
    // decrements answer count
    const diff = orgReactions.length - reactioners.length;
    embeds.footer.text = `${currentCount - diff}/${limitCount}`;
  } else {
    // check limit
    if (currentCount + 1 > limitCount) {
      return await interaction.user.send(`:x:${interaction.message.url}\n は回答人数制限オーバーでした。`);
    }
    // add user name to field
    let reactioners = [];
    if (embeds.fields[fieldIdx].value === "-") {
      reactioners.push(reactionerNick);
    } else {
      reactioners = embeds.fields[fieldIdx].value.split(",");
      reactioners.push(reactionerNick);
    }
    embeds.fields[fieldIdx].value = reactioners.join(",");
    // increments answer count
    embeds.footer.text = `${currentCount + 1}/${limitCount}`;
  }
  await interaction.message.edit({ embeds: [embeds] });
}

async function eachButtonInteraction(client, interaction) {
  // gets common info
  const guild = client.guilds.cache.get(interaction.message.guildId);
  const reactioner = guild.members.cache.get(interaction.user.id);
  let reactionerNick = reactioner ? reactioner.displayName : reactioner.name;
  reactionerNick = reactionerNick.replaceAll(",", "，");
  const embeds = new MessageEmbed(interaction.message.embeds[0]);
  // find index of pressed field
  let fieldIdx = -1;
  for (var i = 0; i < embeds.fields.length; i += 1) {
    if (embeds.fields[i]["name"].split(",")[0] === interaction.component.label) {
      fieldIdx = i;
    }
  }
  const fieldLimitArea = embeds.fields[fieldIdx].name.split(",")[1].trim();
  const currentCount = parseInt(fieldLimitArea.split("/")[0]);
  const limitCount = parseInt(fieldLimitArea.split("/")[1]);
  // check is answered by the user
  let alreadyPressed = false;
  if (embeds.fields[fieldIdx].value === "-") {
    alreadyPressed = false;
  } else {
    alreadyPressed = embeds.fields[fieldIdx].value.includes(reactionerNick);
  }
  if (currentCount < 1 && alreadyPressed) {
    console.error(":x: something wrong field value.");
    return;
  }
  const fieldTitle = embeds.fields[fieldIdx].name.split(",")[0];

  if (alreadyPressed) {
    // remove user name from field
    const orgReactions = embeds.fields[fieldIdx].value.split(",");
    let reactioners = [];
    reactioners = embeds.fields[fieldIdx].value.split(",").filter((e) => e !== reactionerNick);
    if (reactioners.length) {
      embeds.fields[fieldIdx].value = reactioners.join(",");
    } else {
      embeds.fields[fieldIdx].value = "-";
    }
    // decrements answer count
    const diff = orgReactions.length - reactioners.length;
    embeds.fields[fieldIdx].name = `${fieldTitle}, ${currentCount - diff}/${limitCount}`;
  } else {
    // check limit
    if (currentCount + 1 > limitCount) {
      const fieldTitle = embeds.fields[fieldIdx].name.split(",")[0];
      return await interaction.user.send(
        `:x:${interaction.message.url}\nアンケート \`${fieldTitle}\` は回答人数制限オーバーでした。`
      );
    }
    // add user name to field
    let reactioners = [];
    if (embeds.fields[fieldIdx].value === "-") {
      reactioners.push(reactionerNick);
    } else {
      reactioners = embeds.fields[fieldIdx].value.split(",");
      reactioners.push(reactionerNick);
    }
    embeds.fields[fieldIdx].value = reactioners.join(",");
    // increments answer count
    embeds.fields[fieldIdx].name = `${fieldTitle}, ${currentCount + 1}/${limitCount}`;
  }
  await interaction.message.edit({ embeds: [embeds] });
}

async function buttonInteraction(client, interaction) {
  if (interaction.user.bot || interaction.user.system) {
    return;
  }
  const embedTitle = interaction.message.embeds[0].title;
  if ("[アンケート全体での人数制限]" === embedTitle) {
    await totalButtonInteraction(client, interaction);
  }
  if ("[アンケート毎の人数制限]" === embedTitle) {
    await eachButtonInteraction(client, interaction);
  }
  console.debug("button pushed.");
}

module.exports.run = async (client, interaction) => {
  console.debug("interactionCreate");
  if (interaction.isButton()) {
    await interaction.deferUpdate();
    await buttonInteraction(client, interaction);
  }
  if (interaction.isCommand()) {
    await interaction.deferReply();
    const command = client.commands.get(interaction.commandName);
    if (!command) {
      return await interaction.editReply({ content: ":x: Command not found.", ephemeral: true });
    }

    try {
      await command.execute(interaction);
      await interaction.editReply({ content: "ok.", ephemeral: true });
    } catch (e) {
      await interaction.editReply({ content: e.message, ephemeral: true });
    }
  }
};
