from pydantic import BaseModel

from typing import Optional

# Basemodel TOKEN
class Token(BaseModel):
    # ini yang diberikan ketika login itu success
    access_token: str
    token_type: str = "bearer"

# TOken Payload, adalah isi dari token itu
class TokenPayload(BaseModel):
    sub: Optional[str] = None #ini adalah ID
    username: Optional[str] = None
    position: Optional[str] = None 
    exp: Optional[str] = None #Expired waktu Token

class LoginRequest(BaseModel):
    username: str
    password: str