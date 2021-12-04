const { PREFIX } = require("../utils/config");
module.exports.run = async (client) => {
    client.user.setActivity(`${PREFIX}help and ${PREFIX}play`, { type: "LISTENING" });
    console.log(`Ready.`);
};
