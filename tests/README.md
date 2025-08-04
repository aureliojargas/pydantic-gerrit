# Tests

## Setup

- `docker compose up`
- Initial setup to be done only once:
  - Access the Gerrit URL on port 8080
  - Go to `settings/#HTTPCredentials` and generate a new password
  - Add the password to `~/.netrc`, as `machine localhost login admin password ...`
- Setup Python venv
  - Setup venv: `uv sync`
  - Activate venv: `source .venv/bin/activate.fish`
- `pytest`

## TODO

- Should I have full JSON files in the expected data and compare a full model dump?
  - the diff would be nice to detect changes in the API
  - variable data such as timestamps and ids will never match :/

- Must be super readable and user-friendly (contributions), avoid magic

- Use a Python Gerrit client library instead of directly querying the API?

- Must test the full results, with all optional fields activated AND with value
