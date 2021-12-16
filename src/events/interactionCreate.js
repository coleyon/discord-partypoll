const { MessageActionRow, MessageEmbed } = require("discord.js");

async function buttonInteraction(client, interaction) {
  if (interaction.user.bot || interaction.user.system) {
    return;
  }
  // gets common info
  const guild = client.guilds.cache.get(interaction.message.guildId);
  const reactioner = guild.members.cache.get(interaction.user.id);
  let reactionerNick = reactioner ? reactioner.displayName : null;
  reactionerNick = reactionerNick.replace(",", "，");
  const orgFields = interaction.message.embeds[0].fields;
  const currentField = orgFields.filter((f) => f.name === interaction.component.label);

  // check limit
  const embeds = new MessageEmbed(interaction.message.embeds[0]);
  const currentCount = parseInt(embeds.footer.text.split("/")[0]);
  const limitCount = parseInt(embeds.footer.text.split("/")[1]);
  if (currentCount + 1 > limitCount) {
    return await interaction.user.send(`${interaction.message.url}\nこちらの募集は定員に達していました。`);
  }

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
    console.error("something wrong field value.");
    return;
  }
  // find index of press field
  let fieldIdx = -1;
  for (var i = 0; i < embeds.fields.length; i += 1) {
    if (embeds.fields[i]["name"] === interaction.component.label) {
      fieldIdx = i;
    }
  }

  if (alreadyPressed) {
    // remove user name from field
    let reactioners = [];
    reactioners = embeds.fields[fieldIdx].value.split(",").filter((e) => e !== reactionerNick);
    if (reactioners.length) {
      embeds.fields[fieldIdx].value = reactioners.join(",");
    } else {
      embeds.fields[fieldIdx].value = "-";
    }
    // decrements answer count
    embeds.footer.text = `${currentCount - 1}/${limitCount}`;
  } else {
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

  await interaction.message.edit({ content: `timestamp: ${Date.now().toString()}`, embeds: [embeds] });
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
    // await interaction.deferReply({ ephemeral: false }).catch(() => {});
    const command = client.commands.get(interaction.commandName);
    if (!command) {
      return interaction.followUp({ content: "Command not found." });
    }

    try {
      await command.execute(interaction);
    } catch (e) {
      interaction.followUp({ content: e.message });
    }
  }
  return;
};
