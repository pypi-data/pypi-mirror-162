import typing as t
from datetime import datetime

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel
from meili_sdk.version import VERSION

__all__ = (
    "VDA5050VehiclePosition",
    "VDA5050NodePosition",
    "VDA5050VehicleBatteryState",
    "VDA5050NodeState",
    "VDA5050StateMessage",
)


CURRENT_HEADER_ID = 0


class VDA5050VehiclePosition(BaseModel):
    x: float
    y: float
    positionInitialized: bool
    theta: float

    def __init__(self, **kwargs):
        kwargs.setdefault("positionInitialized", True)
        super().__init__(**kwargs)

    def validate_theta(self):
        if self.theta < 0 or self.theta > 360:
            raise ValidationError("Theta must be between 0 and 360 degrees")


class VDA5050NodePosition(BaseModel):
    x: float
    y: float
    theta: float

    def validate_theta(self):
        if self.theta < 0 or self.theta > 360:
            raise ValidationError("Theta must be between 0 and 360 degrees")


class VDA5050VehicleBatteryState(BaseModel):
    batteryCharge: float
    batteryVoltage: float
    batteryHealth: int
    charging: bool
    reach: t.Optional[float] = None

    def __init__(self, **kwargs):
        kwargs.setdefault("charging", False)
        super().__init__(**kwargs)


class VDA5050NodeState(BaseModel):
    nodeId: str
    sequence: str
    nodePosition: VDA5050NodePosition
    released: bool

    def __init__(self, **kwargs):
        kwargs.setdefault("released", False)
        node_position = kwargs.pop("nodePosition")
        if not isinstance(node_position, VDA5050NodePosition):
            node_position = VDA5050NodePosition(**node_position)
        kwargs["nodePosition"] = node_position
        super().__init__(**kwargs)


class VDA5050StateMessage(BaseModel):
    """
    Message to be sent to FMS MQTT Broker

    When initializing the message, headerId and timestamp will be automatically generated
    """

    headerId: int
    timestamp: datetime
    version: str
    manufacturer: str
    serialNumber: str
    orderId: t.Optional[str] = None
    lastNodeId: t.Optional[str] = None
    driving: bool
    paused: bool
    newBaseRequested: bool
    nodeStates: t.Optional[t.List[VDA5050NodeState]] = None
    agvPosition: t.Optional[VDA5050VehiclePosition] = None
    batteryState: t.Optional[VDA5050VehicleBatteryState] = None
    operatingMode: str

    def __init__(self, **kwargs):
        global CURRENT_HEADER_ID
        CURRENT_HEADER_ID += 1

        kwargs.setdefault("headerId", CURRENT_HEADER_ID)
        kwargs.setdefault("timestamp", datetime.now())
        kwargs.setdefault("driving", False)
        kwargs.setdefault("paused", False)
        kwargs.setdefault("newBaseRequested", False)
        kwargs.setdefault("version", VERSION)
        kwargs.setdefault("operatingMode", "AUTOMATIC")

        node_states = kwargs.pop("nodeStates", None)
        node_state_objects = []

        if node_states:
            for node_state in node_states:
                if isinstance(node_state, VDA5050NodeState):
                    node_state_objects.append(node_state)
                else:
                    node_state_objects.append(VDA5050NodeState(**node_state))
            kwargs["nodeStates"] = node_state_objects

        if "agvPosition" in kwargs:
            agv_position = kwargs["agvPosition"]
            if not isinstance(agv_position, VDA5050VehiclePosition):
                kwargs["agvPosition"] = VDA5050VehiclePosition(**agv_position)

        if "batteryState" in kwargs:
            battery_state = kwargs["batteryState"]
            if not isinstance(battery_state, VDA5050VehicleBatteryState):
                kwargs["batteryState"] = VDA5050VehicleBatteryState(**battery_state)

        super().__init__(**kwargs)
