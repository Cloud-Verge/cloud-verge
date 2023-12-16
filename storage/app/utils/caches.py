from pydantic import BaseModel


class UploadDemand(BaseModel):
    size: int
    user_token: str


class DownloadDemand(BaseModel):
    file_id: str
    user_token: str


uploads_cache: dict[str, UploadDemand] = dict()
downloads_cache: dict[str, DownloadDemand] = dict()
