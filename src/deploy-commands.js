const { readdirSync } = require("fs");
const { REST } = require("@discordjs/rest");
const { Routes } = require("discord-api-types/v9");
const { TOKEN, IS_GLOBAL, CLIENT_ID, GUILD_ID } = require("../configs/config.json");

const commands = [];
readdirSync("src/slash").forEach((dir) => {
  const cmdFiles = readdirSync(`src/slash/${dir}/`).filter((file) => file.endsWith(".js"));
  for (const file of cmdFiles) {
    const command = require(`../src/slash/${dir}/${file}`);
    commands.push(command.data.toJSON());
  }
});

const rest = new REST({ version: "9" }).setToken(TOKEN);

(async () => {
  try {
    console.log("Started refreshing application (/) commands.");

    if (IS_GLOBAL === true) {
      await rest.put(Routes.applicationGuildCommands(CLIENT_ID), {
        body: commands
      });
    } else {
      await rest.put(Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID), {
        body: commands
      });
    }
    console.log("Successfully reloaded application (/) commands.");
  } catch (error) {
    console.error(error);
  }
})();
