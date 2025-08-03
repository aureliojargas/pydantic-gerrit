# Using here the minimal Python version we support
# TODO(aj): Maybe we should use the latest since uv can install Python versions?
FROM mcr.microsoft.com/devcontainers/python:3.10

RUN apt update && export DEBIAN_FRONTEND=noninteractive \
    && apt install --yes --no-install-recommends \
    fish \
    && rm -rf /var/lib/apt/lists/*
