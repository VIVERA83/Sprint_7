from src.models.search_args import SearchARGS

from .base_search_params import BaseSearchParams


class FilmSearchParams(BaseSearchParams):
    def get_search_parameters_by_top(
        self,
        sort: str,
        genre_id: str = None,
        page_size: int = None,
        page_number: int = None,
    ) -> SearchARGS:

        if sort:
            order = "desc" if sort.startswith("-") else "asc"
            sort = sort.removeprefix("-")
            sort = [{sort: {"order": order}}]

        if genre_id:
            query = {
                "bool": {
                    "filter": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "lenient": True,
                                        "fields": ["genre.id"],
                                        "query": genre_id,
                                        "type": "phrase_prefix",
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        else:
            query = {"match_all": {}}
        from_ = self.get_pagination(page_number, page_size)

        return SearchARGS(
            index="movies", from_=from_, size=page_size, query=query, sort=sort
        )

    def get_search_parameters_by_title(
        self, title: str = None, page_size: int = None, page_number: int = None
    ) -> SearchARGS:
        source = {"includes": ["id", "title", "imdb_rating"]}

        if title:
            query = {
                "bool": {
                    "filter": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "lenient": True,
                                        "fields": ["title"],
                                        "query": title,
                                        "type": "phrase_prefix",
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        else:
            query = {"match_all": {}}
        from_ = self.get_pagination(page_number, page_size)
        return SearchARGS(
            index="movies",
            from_=from_,
            size=page_size,
            source=source,
            query=query,
        )
