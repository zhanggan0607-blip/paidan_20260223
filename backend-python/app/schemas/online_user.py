from pydantic import BaseModel


class HeartbeatRequest(BaseModel):
    device_type: str = "h5"
