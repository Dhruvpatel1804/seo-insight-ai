from typing import Literal

from pydantic import BaseModel


class AuditResponse(BaseModel):
    audit_id: str
    status: Literal["completed"] = "completed"
    download_url: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "audit_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "download_url": "/api/v1/reports/550e8400-e29b-41d4-a716-446655440000",
                }
            ]
        }
    }
