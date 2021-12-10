module.exports.run = async (client, messageReaction, user) => {
  console.debug("messageReactionRemove");
  const channel = messageReaction.message.channel;
  channel.sendTyping();
  // simply ignore bot and dm messages
  const message = messageReaction.message;
  if (user.system || user.bot || !message.guild) return;

  const guild = client.guilds.cache.get(messageReaction.message.guildId);
  const remover = guild.members.cache.get(user.id);
  const removerNick = remover ? remover.displayName : null;
  const removedEmoji = messageReaction.emoji;
  remover.send(`you removed ${removedEmoji} from the message \n${messageReaction.message.url}`);
};
