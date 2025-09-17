from pydantic import BaseModel, HttpUrl
from typing import Optional

class TemplateCreate(BaseModel):
    name: str
    content: str
    button_text: Optional[str] = None
    button_url: Optional[HttpUrl] = None

class SendMessageRequest(BaseModel):
    chat_id: str # Can be a numeric ID or a @username
    template_name: str
