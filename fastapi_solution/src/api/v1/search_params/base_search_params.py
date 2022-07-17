from typing import Optional


class BaseSearchParams:
    @staticmethod
    def get_pagination(
        page_number: Optional[int], page_size: Optional[int]
    ) -> Optional[int]:
        """Высчитывается offset параметр для запроса в БД (Elastic)"""
        limit = (page_number or 1) - 1
        offset = (page_size or 10) * limit  # 10 - размер страницы по умолчанию
        return offset if offset else None
