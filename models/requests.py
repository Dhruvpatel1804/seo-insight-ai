from pydantic import BaseModel, HttpUrl


class AuditRequest(BaseModel):
    url: HttpUrl

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"url": "https://www.milestoneinternet.com/"}
            ]
        }
    }
