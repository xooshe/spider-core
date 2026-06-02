from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PaginationData:
    page: Optional[int] = None
    take: int = None
    total_pages: int = None
    total_items: int = None


@dataclass
class PaginationRO:
    items: Optional[Any] = None
    pageInfo: PaginationData = None
