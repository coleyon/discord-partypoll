const { readdirSync } = require("fs");
const ascii = require("ascii-table");

//THIS ONE FROM V12

// Create a new Ascii table
let table = new ascii("Slash commands");
module.exports = (client) => {
  readdirSync("src/slash").forEach((dir) => {
    const commands = readdirSync(`src/slash/${dir}/`).filter((file) => file.endsWith(".js"));

    for (let file of commands) {
      let pull = require(`../slash/${dir}/${file}`);

      if (pull.data.name) {
        client.commands.set(pull.data.name, pull);
        table.addRow(file, "✅");
      } else {
        table.addRow(file, `❌  -> missing a help.name, or help.name is not a string.`);
        continue;
      }
    }
  });
  console.log(table.toString());
};
