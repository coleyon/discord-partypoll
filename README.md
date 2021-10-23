# Summary

Work in progress, trying change converting this app using rust + [serenity](https://docs.rs/serenity/0.10.9/serenity/index.html) ...

# Quickstart

Creates `.env` file project root.

```env
DISCORD_BOT_TOKEN=your_bot_token_here
CMD_PREFIX=/
LOGLEVEL=INFO
```

```bash
$ docker-compose build
$ docker-composee up -d
```

# Local Debugging

**Cargo run:**

```bash
$ cargo install
$ cargo build
$ cargo run
```

**VSCode:**

* [LLDB Debugging](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb)
* [Formatter, Linter](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust)


# Base Code references

https://zenn.dev/t4t5u0/articles/cd731e0293cf224cb4dc

