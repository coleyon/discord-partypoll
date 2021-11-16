const fs = require("fs");
const { REST } = require("@discordjs/rest");
const { Routes } = require("discord-api-types/v9");
const { clientId, guildId, token, is_global } = require("configs/config.json");

const commands = [];
const commandFiles = fs.readdirSync("./src/slash-commands").filter((file) => file.endsWith(".js"));

for (const file of commandFiles) {
  const command = require(`./commands/${file}`);
  commands.push(command.data.toJSON());
}

const rest = new REST({ version: "9" }).setToken(token);

(async () => {
  try {
    console.log("Started refreshing application (/) commands.");

    if (!is_global) {
      await rest.put(Routes.applicationGuildCommands(clientId, guildId), {
        body: commands
      });
    } else {
      await rest.put(Routes.applicationGuildCommands(clientId), {
        body: commands
      });
    }

    console.log("Successfully reloaded application (/) commands.");
  } catch (error) {
    console.error(error);
  }
})();
