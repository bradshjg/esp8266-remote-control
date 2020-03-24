FROM debian

RUN apt-get update && apt-get install -y \
    mosquitto-clients \
  && rm -rf /var/lib/apt/lists/*
