from fastapi import APIRouter, HTTPException ,Path , Depends , status
from pydantic import EmailStr, BaseModel
from models.user import User
from config.db import user as db
from datetime import datetime , timedelta
from passlib.context import CryptContext
from jose import JWTError , jwt
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from bson import ObjectId
router = APIRouter()

SECRET_KEY = "yeshammastanimadhoshkiyejayedekho"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    user_id: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto")

oaut2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password , hashed_password):
    return pwd_context.verify(plain_password , hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(user_email , password):
    user = db.find_one({"email": user_email})
    if not user:
        return False
    if verify_password(password, user['password']):
        return user


@router.post("/token" , response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username , form_data.password)
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token(
        data = {"sub": str(user['_id'])},
        expire_time= access_token_expire
    )
    return {"access_token": access_token , "token_type": "Bearer"}


def create_access_token(data:dict , expire_time:timedelta | None = None):
    to_encode = data.copy()
    if expire_time:
        expire = datetime.utcnow() + expire_time
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode , SECRET_KEY , algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token:str = Depends(oaut2_scheme)):
    credential_error = HTTPException(status_code=401 , detail="Could not validate credentials")
    try:
        print(token)
        payload = jwt.decode(token , SECRET_KEY , algorithms=ALGORITHM)
        user_id = payload.get('sub')
        if user_id is None:
            raise credential_error
        token_data = TokenData(user_id=user_id)
    except JWTError:
        print("JWT ERROR")
        raise credential_error
    user = db.find_one({"_id" : ObjectId(token_data.user_id)})
    if user is None:
        raise credential_error
    return user

async def authenticate_request(token:str = Depends(oaut2_scheme)):
    credential_error = HTTPException(status_code=401 , detail="Could not validate credentials")
    try:
        print(token)
        payload = jwt.decode(token , SECRET_KEY , algorithms=ALGORITHM)
        user_id = payload.get('sub')
        if user_id is None:
            raise credential_error
        token_data = TokenData(user_id=user_id)
    except JWTError:
        print("JWT ERROR")
        raise credential_error
    user = db.find_one({"_id" : ObjectId(token_data.user_id)})
    if user is None:
        raise credential_error
    return True




@router.get("/me" , response_model=User)
async def get_current_user(user:User = Depends(get_current_user)):
   if not user:
      raise HTTPException(status_code=404 , detail="User not found")
   return user