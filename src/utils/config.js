let config;
try {
  config = require("../../configs/config.json");
} catch (error) {
  config = null;
}

exports.TOKEN = config ? config.TOKEN : process.env.TOKEN;
exports.PREFIX = (config ? config.PREFIX : process.env.PREFIX) || "/";
