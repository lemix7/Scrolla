from pydantic import BaseModel

class Post(BaseModel):
    title:str
    caption:str