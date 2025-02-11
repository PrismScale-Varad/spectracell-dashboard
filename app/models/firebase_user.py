from pydantic import BaseModel, EmailStr
from typing import Optional

class FirebaseUser(BaseModel):
    uid: Optional[str] = None
    email: EmailStr
    first_name: str
    last_name: str
    npi: str
    practice_name: str
    status: str
