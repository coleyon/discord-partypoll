module.exports.run = async (client, messageReaction, user) => {
  console.debug("messageReactionAdd");
  const channel = messageReaction.message.channel;
  channel.sendTyping();
  // simply ignore bot and dm messages
  const message = messageReaction.message;
  if (user.system || user.bot || !message.guild) return;

  const guild = client.guilds.cache.get(messageReaction.message.guildId);
  const reactioner = guild.members.cache.get(user.id);
  const reactionerNick = reactioner ? reactioner.displayName : null;
  const reactionEmoji = messageReaction.emoji;
  reactioner.send(`You added ${reactionEmoji} to the message\n${messageReaction.message.url}`);
};
