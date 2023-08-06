import dataclasses
from datetime import datetime
from PIL.Image import Image


class CallbackHandler:
    def run(self):
        # all dictionaries are merged
        return {}


@dataclasses.dataclass
class Prompt:
    "holds database result with prompt information"
    prompt_id: int
    inserted_ts: datetime
    params: dict
    num_images: int
    callbacks: list[dict]


@dataclasses.dataclass
class Result:
    "info after generated a prompt used to update database"
    elapsed: int
    loss: float
    seed: str
    images: list[Image]
    version: str = "unknown"


@dataclasses.dataclass
class CallbackArgs:
    result: Result
    prompt: Prompt
    supabase_key: str
    database_url: str
    generation_metadata: dict
    start_time: float
