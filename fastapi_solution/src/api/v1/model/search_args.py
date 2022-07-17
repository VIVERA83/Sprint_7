from dataclasses import dataclass


@dataclass
class SearchARGS:
    index: str
    id: str = None
    from_: int = None
    size: int = None
    query: dict = None
    source: dict = None
    sort: list = None
