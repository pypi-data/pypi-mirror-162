from meili_sdk.models.base import BaseModel
import typing as t

__all__ = ("DockingRoutineMessage",)

class DockingRoutineMessage(BaseModel):
    type: str
    point: t.List
