from pydantic import BaseModel, HttpUrl

class Body(BaseModel):
    url : HttpUrl
