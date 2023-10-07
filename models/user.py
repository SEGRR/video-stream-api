from pydantic import BaseModel, EmailStr, Field



class User(BaseModel):
    name:str
    email: EmailStr
    phone:str = Field(max_length=10 )
    password: str = Field(min_length=6)
    fav_genres: list[str] = []
    fav_language: list[str] = []
    watch_history : list[int] = []
    liked_movies : list[int] = []
