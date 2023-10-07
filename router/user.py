from fastapi import APIRouter, HTTPException ,Path, Depends
from pydantic import EmailStr
from models.user import User
from config.db import user as db
from config.db import movies as movie_db
from passlib.context import CryptContext
from bson import ObjectId
from . import auth
router = APIRouter()

def serialize(entity):
   return {**{i:str(entity[i]) for i in entity if i == '_id'} , **{i:entity[i] for i in entity if i != '_id'}}

def serialize_all(en):
   return [serialize(i) for i in en]

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto")

@router.post("/create")
async def create_new_user(user:User):
   if db.find_one({"email":user.email}) is not None:
      raise HTTPException(status_code=201 ,detail="Email already exists")
   user.password = pwd_context.encrypt(user.password)
   db.insert_one(dict(user))
   return user


@router.get("/me" , response_model=User)
async def get_current_user(user:User = Depends(auth.get_current_user)):
   if not user:
      raise HTTPException(status_code=404 , detail="User not found")
   return user

# @router.get("/{id}")
# async def get_by_email(id:str):
#    user = db.find_one({"_id": ObjectId(id)})
#    if user:
#       return serialize(user)
#    else:
#       raise HTTPException(status_code=404 , detail="specified user not found")


@router.post("/fav_genre")
async def update_fav_genre(fav_genre:list[str] , user:User = Depends(auth.get_current_user)):
   db.update_one({"email":user['email']} , {"$addToSet":{"fav_genres":{"$each":fav_genre}}})
   return {"message": "Genre updated"}

@router.post("/watch_history")
async def update_watch_history(movie_id:int , user:User = Depends(auth.get_current_user)):
   db.update_one({"email":user['email']} , {"$addToSet":{"watch_history":movie_id}})
   return {"message": "Updated"}


@router.get("/watch_history")
async def get_watch_history(user:User = Depends(auth.get_current_user)):
   movie_history = movie_db.find({"id":{"$in": user['watch_history']}}, {"id":1, "title":1 , "popularity":1 , "poster_path":1 , "backdrop_path":1})
   return serialize_all(movie_history)



