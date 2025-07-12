# Roadmap

## First milestone: Validate the original idea (done: 2025-07-13)

- Support just a single endpoint: `groups`
- Support just a single Gerrit version: `3.12.0`
- All models are fully tested by querying the API of a local Gerrit

## Second milestone: Multi Gerrit version

- Support a second Gerrit version: `3.11`
- Decide the general strategy for multiple Gerrit versions on models, tests and packaging

## Third milestone: Expand the coverage

- Support a second endpoint: `accounts`
- Support a third Gerrit version: `3.10`
- State the project goals in the `README.md`

## Pre-release

- Pin runtime dependencies to the lowest version that works
- Pin dev dependencies to the latest version that works
- Review all the naming: package, import, repository, etc.
- Update `CONTRIBUTING.md` with dev instructions
- Have a proper `README.md`
- Decide how to do the changelog, must mention all Gerrit versions affected by any change
- Setup CI in GitHub
- Tests can be run with (ideally) zero manual setup in the Gerrit instance
