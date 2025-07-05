from pydantic import BaseModel, ConfigDict


class BaseModelGerrit(BaseModel):
    model_config = ConfigDict(
        extra='forbid',  # our models are strict, no extra fields allowed
        serialize_by_alias=True,  # keep the leading underscores in field names when dumping the model
    )
