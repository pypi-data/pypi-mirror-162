from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from revolt.types.permissions import Overwrite

from .channel import (Channel, DMChannel, GroupDMChannel, SavedMessages,
                      TextChannel, VoiceChannel)
from .file import File
from .message import Message
from .user import Status

if TYPE_CHECKING:
    from .category import Category
    from .member import Member, MemberID
    from .server import Server, SystemMessagesConfig
    from .user import User

__all__ = (
    "BasePayload",
    "AuthenticatePayload",
    "ReadyEventPayload",
    "MessageEventPayload",
    "MessageUpdateEditedData",
    "MessageUpdateData",
    "MessageUpdateEventPayload",
    "MessageDeleteEventPayload",
    "ChannelCreateEventPayload",
    "ChannelUpdateEventPayload",
    "ChannelDeleteEventPayload",
    "ChannelStartTypingEventPayload",
    "ChannelDeleteTypingEventPayload",
    "ServerUpdateEventPayload",
    "ServerDeleteEventPayload",
    "ServerMemberUpdateEventPayload",
    "ServerMemberJoinEventPayload",
    "ServerMemberLeaveEventPayload",
    "ServerRoleUpdateEventPayload",
    "ServerRoleDeleteEventPayload",
    "UserUpdateEventPayload",
    "UserRelationshipEventPayload",
    "ServerCreateEventPayload"
)

class BasePayload(TypedDict):
    type: str

class AuthenticatePayload(BasePayload):
    token: str

class ReadyEventPayload(BasePayload):
    users: list[User]
    servers: list[Server]
    channels: list[Channel]
    members: list[Member]

class MessageEventPayload(BasePayload, Message):
    pass

MessageUpdateEditedData = TypedDict("MessageUpdateEditedData", {"$date": str})

class MessageUpdateData(TypedDict):
    content: str
    edited: MessageUpdateEditedData

class MessageUpdateEventPayload(BasePayload):
    channel: str
    data: MessageUpdateData
    id: str

class MessageDeleteEventPayload(BasePayload):
    channel: str
    id: str

class ChannelCreateEventPayload_SavedMessages(BasePayload, SavedMessages):
    pass

class ChannelCreateEventPayload_Group(BasePayload, GroupDMChannel):
    pass

class ChannelCreateEventPayload_TextChannel(BasePayload, TextChannel):
    pass

class ChannelCreateEventPayload_VoiceChannel(BasePayload, VoiceChannel):
    pass

class ChannelCreateEventPayload_DMChannel(BasePayload, DMChannel):
    pass

ChannelCreateEventPayload = Union[ChannelCreateEventPayload_Group, ChannelCreateEventPayload_Group, ChannelCreateEventPayload_TextChannel, ChannelCreateEventPayload_VoiceChannel, ChannelCreateEventPayload_DMChannel]

class ChannelUpdateEventPayloadData(TypedDict, total=False):
    name: str
    description: str
    icon: File
    nsfw: bool
    active: bool
    role_permissions: dict[str, Overwrite]
    default_permissions: Overwrite

class ChannelUpdateEventPayload(BasePayload):
    id: str
    data: ChannelUpdateEventPayloadData
    clear: Literal["Icon", "Description"]

class ChannelDeleteEventPayload(BasePayload):
    id: str

class ChannelStartTypingEventPayload(BasePayload):
    id: str
    user: str

ChannelDeleteTypingEventPayload = ChannelStartTypingEventPayload

class ServerUpdateEventPayloadData(TypedDict, total=False):
    owner: str
    name: str
    description: str
    icon: File
    banner: File
    default_permissions: int
    nsfw: bool
    system_messages: SystemMessagesConfig
    categories: list[Category]

class ServerUpdateEventPayload(BasePayload):
    id: str
    data: ServerUpdateEventPayloadData
    clear: Literal["Icon", "Banner", "Description"]

class ServerDeleteEventPayload(BasePayload):
    id: str

class ServerCreateEventPayload(BasePayload):
    id: str
    server: Server
    channels: list[Channel]

class ServerMemberUpdateEventPayloadData(TypedDict, total=False):
    nickname: str
    avatar: File
    roles: list[str]

class ServerMemberUpdateEventPayload(BasePayload):
    id: MemberID
    data: ServerMemberUpdateEventPayloadData
    clear: Literal["Nickname", "Avatar"]

class ServerMemberJoinEventPayload(BasePayload):
    id: str
    user: str

ServerMemberLeaveEventPayload = ServerMemberJoinEventPayload

class ServerRoleUpdateEventPayloadData(TypedDict, total=False):
    name: str
    colour: str
    hoist: bool
    rank: int

class ServerRoleUpdateEventPayload(BasePayload):
    id: str
    role_id: str
    data: ServerRoleUpdateEventPayloadData
    clear: Literal["Color"]

class ServerRoleDeleteEventPayload(BasePayload):
    id: str
    role_id: str

UserUpdateEventPayloadData = TypedDict("UserUpdateEventPayloadData", {
    "status": Status,
    "profile.background": File,
    "profile.content": str,
    "avatar": File,
    "online": bool

}, total=False)

class UserUpdateEventPayload(BasePayload):
    id: str
    data: UserUpdateEventPayloadData
    clear: Literal["ProfileContent", "ProfileBackground", "StatusText", "Avatar"]

class UserRelationshipEventPayload(BasePayload):
    id: str
    user: str
    status: Status
