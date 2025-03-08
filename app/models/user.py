from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
