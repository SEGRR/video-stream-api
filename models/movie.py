from pydantic import BaseModel


class Movie(BaseModel):
    movie_id:int
    title:str




