from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class Header:
    alg: str = "H256"


@dataclass
class Payload:
    user_id: uuid4 = uuid4()
    iat: int = datetime.now().timestamp()
    exp: int = 900
    role: str = "anonymous"
    nonce: bool = False
    super_user: bool = False


@dataclass
class JWT:
    header: Header
    payload: Payload
    jwt: str

    @property
    def signature(self) -> str:
        return self.jwt.split(".")[2]
