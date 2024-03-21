from typing import Optional
from pydantic import BaseModel


class UploadDemand(BaseModel):
    file_id: str
    user_auth: str


class DownloadDemand(BaseModel):
    file_id: str
    user_auth: Optional[str]


uploads_cache: dict[str, UploadDemand] = dict()
downloads_cache: dict[str, DownloadDemand] = dict()
