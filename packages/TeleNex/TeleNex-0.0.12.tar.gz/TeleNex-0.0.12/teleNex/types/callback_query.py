from typing import Optional

from . import TeleObj, Field

from .user import User
from .message import Message

class CallbackQuery(TeleObj):
    _corrects = {
        'from': 'from_user'
    }

    id: str = Field()
    from_user: User = Field(User)
    message: Optional[Message] = Field(Message)
    inline_message_id: Optional[str] = Field()
    chat_instance: Optional[str] = Field()
    data: Optional[str] = Field()
    game_short_name: Optional[str] = Field()