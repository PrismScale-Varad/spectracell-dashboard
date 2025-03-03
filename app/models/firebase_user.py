from pydantic import BaseModel, EmailStr
from typing import Optional

class FirebaseUser(BaseModel):
    uid: Optional[str] = None 
    email: EmailStr
    first_name: Optional[str] = None 
    last_name: Optional[str] = None 
    npi: Optional[str] = None 
    practice_name: Optional[str] = None 
    status: Optional[str] = None 
