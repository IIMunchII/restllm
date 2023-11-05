import uuid
from datetime import datetime
from enum import Enum
from typing import Any

import redis.asyncio as redis
from pydantic import UUID4, BaseModel, Field


class EventType(str, Enum):
    TASK = "task"
    OBJECT = "object"


class CRUDAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class TaskAction(Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    COMPLETE = "complete"


class EventStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class Event(BaseModel):
    action: CRUDAction | TaskAction
    status: EventStatus
    object: Any


class EventWithMeta(BaseModel):
    uuid: str | UUID4 = Field(default_factory=uuid.uuid4)
    owner: int | str
    type: EventType
    event: Event
    created_at: datetime = Field(default_factory=datetime.now)

    async def publish(self, redis_client: redis.Redis) -> int:
        return await redis_client.publish(
            self.get_channel(),
            self.model_dump_json(),
        )

    def get_channel(self) -> str:
        return f"{self.type.value}:{self.owner}"
