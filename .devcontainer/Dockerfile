# Using here the minimal Python version we support
# TODO(aj): Maybe we should use the latest since uv can install Python versions?
# Pin to bookworm since trixie raised error when installing moby-* packages.
FROM mcr.microsoft.com/devcontainers/python:3.10-bookworm

RUN apt update && export DEBIAN_FRONTEND=noninteractive \
    && apt install --yes --no-install-recommends fish \
    && rm -rf /var/lib/apt/lists/*
