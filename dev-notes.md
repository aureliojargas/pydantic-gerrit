# Dev notes

## TODO - schemas

- Complete all entities generation
- Fix generated Python code to import from other generated models instead of creating those empty types/classes
- Define testing strategy
  - Have JSON input/responses saved in the repo?
    - Then the models can be validated against them
    - No need for a Gerrit instance to run the tests
      - This is important so the tests run fast and reliably
    - Gerrit instance would be useful to generate the JSON files
    - Different sets of files per Gerrit version

- Docs:
  - How to regenerate the models: `cd schemas/v3_12 && python ../../scripts/generate.py --version 3_12`


## TODO

- Maybe try converting `polygerrit-ui/app/types/common.ts` directly to Pydantic?
  - `polygerrit-ui/app/api/rest-api.ts`
  - `polygerrit-ui/app/constants/constants.ts`
  - `polygerrit-ui/app/types/types.ts`
  - First commit adding it in Jul 2020: bfbd275a1bd17c038b5905a34f4863a446f3914e
  - How far it goes back?
    - Was it a good support back then?
    - Can I rely on it to generating everything?
    - Or should I stick to what it supports?
  - Study it more.
  - Is it official and well maintained?
  - Everything in a single file is an advantage?
  - Does it change too much?
  - My differential:
    - Support multiple versions (well, that one already does, via stable branches)
    - Python
    - Automatic testing
      - does this one also have it?
      - Investigate
    - detached from Gerrit, anyone can install
  - It has some niceties such as enum and base classes

    ```ts
    export type GroupAuditEventInfo =
    | GroupAuditAccountEventInfo
    | GroupAuditGroupEventInfo;

    export enum GroupAuditEventType {
    ADD_USER = 'ADD_USER',
    REMOVE_USER = 'REMOVE_USER',
    ADD_GROUP = 'ADD_GROUP',
    REMOVE_GROUP = 'REMOVE_GROUP',
    }

    export interface GroupAuditEventInfoBase {
    user: AccountInfo;
    date: Timestamp;
    }

    export interface GroupAuditAccountEventInfo extends GroupAuditEventInfoBase {
    type: GroupAuditEventType.ADD_USER | GroupAuditEventType.REMOVE_USER;
    member: AccountInfo;
    }

    export interface GroupAuditGroupEventInfo extends GroupAuditEventInfoBase {
    type: GroupAuditEventType.ADD_GROUP | GroupAuditEventType.REMOVE_GROUP;
    member: GroupInfo;
    }
    ```

- Tests cover all models from `groups` (run `make uncovered`)
- Document the decisions: Python version, Gerrit versions, no patch-level versions in the models, no EOL'ed versions, etc.
- How to automate the API usage without manually generating an HTTP password first?

## Models

- Use `extra='forbid'` in all models? Makes sense, since we're targeting specific API versions.

- Should I add extra models making non-optional the fields affected by extra query options? For example, activating `members` and `includes` fields in `GroupInfo`, we could have extra models such as `GroupInfoPlusMembers` and `GroupInfoPlusIncludes`, and the combination of both: `GroupInfoPlusMembersAndIncludes`. This combination can explode the number of models if many extra fields are activated.
  - The models that use `GroupInfo` as an attribute type may also be affected by `o=MEMBERS`, for example?

## Input models

Testing input models is convoluted because:

> <https://gerrit-review.googlesource.com/Documentation/rest-api.html#input>
>
> Unknown JSON parameters will simply be ignored by Gerrit without causing an exception.

So if I really want to make sure the input models only contains valid fields, I would have to always assert that the informed value was set in the just-created element. I don't want to go down that route. At least not now.

Some fields in the input models have leading underscores. Pydantic considers them private.
We're using `alias=` in the model to fix the validation to accept the underscores, and `serialize_by_alias=True` in the base model to fix the serialization. See: <https://github.com/pydantic/pydantic/issues/8700>

## Today I Learned (TIL)

Optional fields may appear only if the data is actually set.

- For example, when showing an account, the `display_name` field will only appear if the user has set a display name.
- Even for boolean fields: "not set if false"
  - but sometimes `false` appears in the output:
      http -b :8080/access/?project=All-Projects
        "config_visible": false,
- not set if range is empty (from 0 to 0) or not set
- not set for the All-Projects project

Input parameters will change the output, adding more data to the response.

Some endpoints require a query string, otherwise will return empty.

Some outputs require special permissions:

> <http://localhost:8080/Documentation/rest-api-plugins.html#list-plugins>
>
> To be allowed to see the installed plugins, a user must be a member of a group that is granted the 'View Plugins' capability or the 'Administrate Server' capability.

Some outputs require special compile options:

> <http://localhost:8080/Documentation/rest-api-documentation.html>
>
> Please note that this feature is only usable with documentation built-in. You’ll need to bazel build withdocs or bazel build release to test this feature.

## Gerrit versions

We provide data models for all the supported Gerrit versions:
<https://www.gerritcodereview.com/support.html#supported-versions>

Changelog: <https://www.gerritcodereview.com/releases-readme.html>

Maven releases: <https://central.sonatype.com/artifact/com.google.gerrit/gerrit-war/versions>

## Versions

Latest: 3.12.0 (July 2025)
Local: 3.10.5

3.9 and older are EOL: <https://www.gerritcodereview.com/support.html#supported-versions>

Discover the current version:

```console
$ http -b :8080/config/server/version
)]}'
"3.12.0"
$
```

## How to discover API changes

```bash
git diff origin/stable-3.11..origin/stable-3.12 -- Documentation/rest-api*
```

See also changes in the original Java data files.

## Gerrit repository

<https://gerrit.googlesource.com/gerrit/+/refs/heads/stable-3.12/>

```text
Documentation/rest-api-access.txt
Documentation/rest-api-accounts.txt
Documentation/rest-api-changes.txt
Documentation/rest-api-config.txt
Documentation/rest-api-documentation.txt
Documentation/rest-api-groups.txt
Documentation/rest-api-plugins.txt
Documentation/rest-api-projects.txt
Documentation/rest-api.txt

java/com/google/gerrit/server/restapi
java/com/google/gerrit/extensions/api/
java/com/google/gerrit/extensions/common/

polygerrit-ui/app/api/rest-api.ts
```

## Auth

Set an HTTP password in the UI for the `admin` user: <http://localhost:8080/settings/#HTTPCredentials>

Add it to `.netrc`:

```netrc
machine localhost login admin password ...
```

How to automate that?

## Calling API from the console

Install:

```bash
uv tool install httpie
```

Run without credentials (no `/a` prefix):

```console
$ http -b :8080/projects
)]}'
{
    "All-Projects": {
        "id": "All-Projects",
        "state": "ACTIVE",
        "web_links": [
            {
                "name": "browse",
                "url": "/plugins/gitiles/All-Projects"
            }
        ]
    },
    "All-Users": {
        "id": "All-Users",
        "state": "ACTIVE",
        "web_links": [
            {
                "name": "browse",
                "url": "/plugins/gitiles/All-Users"
            }
        ]
    }
}
```

Run with credentials (use the `/a` prefix):

```bash
http -b :8080/a/groups
```

With query parameters

```bash
http -b :8080/a/accounts suggest== q==a
```

To query some Gerrit installs, you must `--follow` redirects:

```bash
http --follow gerrit.example.com/a/groups
```

## Querying the changes endpoint

By default there's no changes to query, I must create a repo and submit a change.

```bash
git clone "<http://localhost:8080/test>" &&
(cd "test" &&
    mkdir -p `git rev-parse --git-dir`/hooks/ &&
    curl -Lo `git rev-parse --git-dir`/hooks/commit-msg <http://localhost:8080/tools/hooks/commit-msg> &&
    chmod +x `git rev-parse --git-dir`/hooks/commit-msg)

cd test/
echo foo > README.md
git add README.md
gcm First commit
git remote add gerrit <http://localhost:8080/test>
git review
```

## Python package

Have a single package, with the Gerrit versions as submodules:

```python
from pydantic_gerrit.v3_12.groups import GroupInfo
```

Users can also detect the actual Gerrit server version at runtime and load the correct submodule.

Should I divide the package by major endpoints (like Gerrit docs) or join all endpoints in a single module?

Use calver.org instead of semver? Semver because I may decide to change the package structure any time, and that's a breaking change.

Package name:

```python
import pydantic
import pydantic_settings
import pydantic_gerrit  # pydantic is "Data validation using Python type hints", just stating Gerrit should be enough
```

## Multiple Gerrit versions

Use symlinks in the model files to avoid repetition? This can get messy when changing a symlink source: it will reflect in multiple versions, maybe without noticing.

Tests? How to do it? Feature sniffing or completely separate per version?

No need to support patch-level versions. They are bugfixes and there's no functionality change:

- <https://www.gerritcodereview.com/3.11.html#bugfix-releases>
- <https://www.gerritcodereview.com/3.10.html#bugfix-releases>
- <https://www.gerritcodereview.com/3.9.html#bugfix-releases>

Will we support only the active (not EOL'ed) versions? If so, what happens when a version we support gets EOL'ed? Do we remove it from the package? Or just stop testing and updating it?

One idea is having a `latest` "version", where all the most current models will reside. Versioned packages will import from `latest` when there's no changes. Otherwise they must contain their own implementation for the differing models. For the user, one (questionable) advantage is being able to always import from `pydantic_gerrit.latest.*`, as long as they always use the most recent Gerrit version.

```python
from pydantic_gerrit.latest.groups import GroupInfo, GroupOptionsInfo
from pydantic_gerrit.latest.accounts import AccountInfo, AvatarInfo
```

Or maybe not having the `latest` namespace and allowing for direct endpoints access from the root package: `pydantic_gerrit.groups`.

```python
from pydantic_gerrit.groups import GroupInfo, GroupOptionsInfo
from pydantic_gerrit.accounts import AccountInfo, AvatarInfo
```

But this is all weird. The typing is always tied to a specific Gerrit version. The user must know which Gerrit version they are targeting.

```python
from pydantic_gerrit.v3_12.groups import GroupInfo, GroupOptionsInfo
from pydantic_gerrit.v3_12.accounts import AccountInfo, AvatarInfo
```

Maybe remove the underscore from the version? There won't be too many different numbers at any given time...

```python
from pydantic_gerrit.v312.groups import GroupInfo, GroupOptionsInfo
from pydantic_gerrit.v312.accounts import AccountInfo, AvatarInfo
```

If I only have versioned packages, how to organize the actual code? If a model is exactly the same in all Gerrit versions, under which specific version its implementation should reside? The older or the newer? Or in a private internal namespace? If it's in the older (the most intuitive), then it's a trouble when I need to remove a version (e.g., because it was EOL'ed). Well it's a one-time trouble.

Should I use `__all__` to make all models available?

## Additional ideas

- Publish schemas from the models, in the repository or <https://www.schemastore.org/>

- Document (or even publish) that one can convert Pydantic models to TypedDict: <https://github.com/unclecode/pydantype>.
  - Useful for those not using Pydantic models in their code, but still want to type the JSON results.

## References

- [Rest API docs](https://gerrit-review.googlesource.com/Documentation/rest-api.html): This the most up-to-date docs.

- [Summary of Gerrit releases](https://www.gerritcodereview.com/releases-readme.html)

- [Gerrit ticket to implement Swagger (OpenAPI)](https://issues.gerritcodereview.com/issues/40011133): Opened in 2019, not too many comments, but brings one important bit of information: "The Gerrit REST-API documentation is currently hand-written.". That means the documentation may be wrong, or not in sync with the code. That's why actual testing in a Gerrit instance is required.

- [Tool to generate pydantic models](https://docs.pydantic.dev/latest/integrations/datamodel_code_generator/) many input sources, but none that I can use.

## Interesting Pydantic projects

- <https://pypi.org/project/api-client-pydantic/>
- <https://pypi.org/project/pydantic-faker/>

## My upstream contribs

- [Remove unused `width` attribute from AvatarInfo](https://gerrit-review.googlesource.com/c/gerrit/+/488441)
- [REST API docs: Move 'Delete Group' after 'Create Group'](https://gerrit-review.googlesource.com/c/gerrit/+/488463)
- [Fix typos in documentation](https://gerrit-review.googlesource.com/c/gerrit/+/489442?usp=dashboard)
