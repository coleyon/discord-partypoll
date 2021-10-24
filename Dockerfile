#======== BASE image for build time saving.
FROM rust:1.56 as base

ARG APP_NAME=${APP_NAME:-partypoll}

# Create empty project
RUN USER=root cargo new --bin ${APP_NAME}
WORKDIR /${APP_NAME}

# Build dependencies for caching
# COPY ["./Cargo.lock", "./Cargo.lock"]
COPY ["./Cargo.toml", "./Cargo.toml"]
RUN cargo build --release
RUN rm -fr ./src

# Build original source tree
RUN rm ./target/release/deps/${APP_NAME}*
COPY ["./src", "./src"]
RUN cargo build --release

#======== APP image
FROM rust:1.56

# copy cached directory
ARG APP_NAME=${APP_NAME:-partypoll}

WORKDIR /${APP_NAME}
COPY --from=base ["/${APP_NAME}/target/release/${APP_NAME}", "."]

ENV DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN:-set_your_token}
ENV CMD_PREFIX=${CMD_PREFIX:-/}
ENV LOGLEVEL=${LOGLEVEL:-INFO}
ENV APP_NAME=${APP_NAME:-partypoll}
ENV RUST_LOG=${RUST_LOG:-INFO}

CMD ["sh", "-c", "./${APP_NAME}"]