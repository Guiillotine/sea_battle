
from pydantic import BaseModel, field_validator
import hashlib
from datetime import datetime
from typing import Optional

def hash_password(password):
    value_bytes = password.encode("utf-8")  # Строка нужна в байтовом виде
    hash_object = hashlib.sha256(value_bytes, usedforsecurity=True)
    return hash_object.hexdigest() # хэш - к строке

### ИГРОК
class Player_base(BaseModel):
    login: str
    password: str

class Player_create(Player_base):
    @field_validator("password")
    def hash_password(cls, value):
        return hash_password(value)

class Player(Player_base):
    id: int
    sid: str
    class Config:
        from_attributes = True

class Player_login_request(Player_base):
    # Для авторизации нужны те же поля, что в Player_base: логин, пароль
    pass

class Player_login_response(BaseModel):
    # При успешной авторизации вернуть: sid, логин
    sid: str
    login: str


### ИГРА
class Game_base(BaseModel):
    board: list[list[list[int]]]
    start_date: datetime
    end_date: Optional[datetime] = None
    id_player1: int
    id_player2: int
    id_winner: Optional[int] = None
    id_status: int

class Game_create(Game_base):
    pass

class Game(Game_base):
    id: int
    sid: str
    class Config:
        from_attributes = True


### СТАТУС ИГРЫ
class Status(BaseModel):
    id: int
    status_name: str
    class Config:
        from_attributes = True