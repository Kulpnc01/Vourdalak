import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

class NodeType(enum.Enum):
    USERNAME = "username"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    IDENTITY = "identity"
    CREDENTIAL = "credential"
    SOCIAL_POST = "social_post"

class EdgeType(enum.Enum):
    OWNED_BY = "owned_by"
    INTERACTED_WITH = "interacted_with"
    MENTIONED = "mentioned"
    SAME_PASSWORD = "same_password"
    FRIEND_OF = "friend_of"
    FOLLOWS = "follows"
    LINKED_TO = "linked_to"

@dataclass(frozen=True)
class Node:
    type: NodeType
    value: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.type in [NodeType.EMAIL, NodeType.USERNAME]:
            object.__setattr__(self, "value", self.value.lower().strip())
        else:
            object.__setattr__(self, "value", self.value.strip())

@dataclass(frozen=True)
class Edge:
    source: Node
    target: Node
    type: EdgeType
    weight: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
