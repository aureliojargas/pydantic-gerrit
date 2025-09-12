Asking CoPilot to generate TypedDicts for all models in groups.py using Python 3.10+ syntax (PEP 604)


```python
from typing import TypedDict, Literal
from datetime import datetime

class GroupAuditEventInfoDict(TypedDict, total=False):
    member: "AccountInfoDict | GroupInfoDict"
    type: Literal['ADD_USER', 'REMOVE_USER', 'ADD_GROUP', 'REMOVE_GROUP']
    user: "AccountInfoDict"
    date: datetime

class GroupInfoDict(TypedDict, total=False):
    id: str
    name: str | None
    url: str | None
    options: "GroupOptionsInfoDict"
    description: str | None
    group_id: int | None
    owner: str | None
    owner_id: str | None
    created_on: datetime | None
    more_groups: bool | None
    members: list["AccountInfoDict"] | None
    includes: list["GroupInfoDict"] | None

class GroupInputDict(TypedDict, total=False):
    name: str | None
    uuid: str | None
    description: str | None
    visible_to_all: bool | None
    owner_id: str | None
    members: list[str] | None

class GroupOptionsInfoDict(TypedDict, total=False):
    visible_to_all: bool | None

class GroupOptionsInputDict(TypedDict, total=False):
    visible_to_all: bool | None

class GroupsInputDict(TypedDict, total=False):
    one_group: str | None
    groups: list[str] | None

class MembersInputDict(TypedDict, total=False):
    one_member: str | None
    members: list[str] | None
```
