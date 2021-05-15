# Summary

The discord bot contains few extentions.
* `ppoll` extension: poll tool like to the [Simple Poll](https://discord.bots.gg/bots/324631108731928587).
* `cron` extension: automated command runner with cron like schedule format.


# Manual

* `/help`
  ```
  Synopsis:
    /ext load <COG>
    /ext unload <COG>

  COG:
    "ppoll" - Simple Poll like polling extension
    "cron" - Cron like scheduling extension
  ```
* [`/help poll`](https://github.com/coleyon/discord-partypoll/wiki/poll)
  ```
  Synopsis:
    /ppoll each <TITLE> <[[LIMIT_OF_THE_QUESTION]]QUESTION_1> [<[[LIMIT_OF_THE_QUESTION]]QUESTION_1>]
    /ppoll total <TITLE> <LIMIT_OF_QUESTIONS> <QUESTION_1> [<QUESTION_10>]
  ```
* [`/help cron`](https://github.com/coleyon/discord-partypoll/wiki/cron)
  ```
  Synopsis:
    /cron add <SCHEDULE_NAME> <SCHEDULE> <COMMAND> - add a schedule.
    /cron del <SCHEDULE_NAME> - remove specified schedule
    /cron show [SCHEDULE_NAME] - show list of registered schedules.
    /cron check - show next run and target channel.
    /cron get - download a schedule file formatted with json.
    /cron load - upload a schedule file formatted with json.
    /cron timezone - show curent running timezone setting
    /cron timezone <TZ> - set running timezone
    /cron [help] - show this help
    /cron enable - enable running cron schedules
    /cron disable - disable running cron schedules
    /cron set schedule <SCHEDULE_NAME> <SCHEDULE> - sets a crontab to the schedule
    /cron set channel <SCHEDULE_NAME> - sets a channel to run the command

  format of the SCHEDULE:
      * * * * *
      | | | | |
      | | | | |
      | | | | +---- Day of the Week   (range: 0-6 or mon,tue,wed,thu,fri,sat,sun)
      | | | +------ Month of the Year (range: 1-12)
      | | +-------- Day of the Month  (range: 1-31)
      | +---------- Hour              (range: 0-23)
      +------------ Minute            (range: 0-59)  # every n day in month.
      Expression Field Description
      ----------------------------------
      *        any    Fire on every value
      */a      any    Fire every a values, starting from the minimum
      a-b      any    Fire on any value within the a-b range (a must be smaller than b)
      a-b/c    any    Fire every c values within the a-b range
      x,y,z    any    Fire on any matching expression; can combine any number of any of the above expressions
      Examples:
          */1 * * * *      : runs at every minutes, every day.
          59 * * * sun     : runs at 59 minutes every hour on sunday
          0 14,21 * * *    : runs at 14:00 and 21:00 every day.
          40-50 3 25 12 *  : runs from 3:40 to 3:50 on December 25th.
  ```

# Quickstart

**Poll** commands

```
/ext load poll
/ppoll total "It is TITLE" 5 "Dance Party" "Summer Sonic Fest"
/ppoll each "It is TITLE" "[4]Jazz Quartet Live" "Summer Sonic Fest"
```

**Cron** commands

```
Examples:
  /ext load cron
  /cron timezone EST
  /cron add Schedule-A */1 * * * * /ppoll total "It is TITLE" 5 "Dance Party" "Summer Sonic Fest"
  /cron enable
```

# Upstart

* make requirements.txt `$ pipenv lock -r`
* [Create your own discord bot and get the token](https://qiita.com/PinappleHunter/items/af4ccdbb04727437477f#bot%E7%94%A8%E3%81%AE%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%82%92%E6%89%8B%E3%81%AB%E5%85%A5%E3%82%8C%E3%82%8B)
* Set the token to `DISCORD_BOT_TOKEN` in `docker-compose.yml`
* Run `$ docker-compose up -d` on your docker server
* [Invite your bot to your discord server](https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot)
required permissions
  * SCOPES: bot
  * BOT TEXT PERMISSIONS: `Send Messages`, `Manage Messages`, `Embed Links`, `Add Reactions`
