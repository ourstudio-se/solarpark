from typing import Any, Optional

from pydantic import BaseModel


class Attachment(BaseModel):
    file_content: Any
    file_name: str
    file_type: str


class Email(BaseModel):
    from_email: str
    to_email: str
    subject: str
    html_content: str
    attachments: Optional[list[Attachment]] = None
