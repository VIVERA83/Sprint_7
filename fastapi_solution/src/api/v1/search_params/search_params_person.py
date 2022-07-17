from src.models.search_args import SearchARGS

from .base_search_params import BaseSearchParams


class PersonSearchParams(BaseSearchParams):
    @staticmethod
    def get_search_parameters_by_id(person_id: str) -> SearchARGS:
        source = {"includes": ["id", "title", "imdb_rating"]}
        query = {
            "bool": {
                "filter": {
                    "bool": {
                        "should": [
                            {
                                "multi_match": {
                                    "lenient": True,
                                    "fields": ["actors.id", "writers.id"],
                                    "query": person_id,
                                    "type": "phrase_prefix",
                                }
                            }
                        ]
                    }
                }
            }
        }
        return SearchARGS(index="movies", source=source, query=query)

    def get_search_parameters_by_name(
        self, title: str = None, page_size: int = None, page_number: int = None
    ) -> SearchARGS:
        """Формирует запрос по  поиску по имане персонажа api/v1/person/search ,"""
        if title:
            query = {
                "bool": {
                    "filter": {
                        "bool": {
                            "minimum_should_match": 1,
                            "should": [
                                {
                                    "multi_match": {
                                        "lenient": "true",
                                        "fields": ["full_name"],
                                        "query": title,
                                    }
                                }
                            ],
                        }
                    }
                }
            }
        else:
            query = {"match_all": {}}
        from_ = self.get_pagination(page_number, page_size)
        return SearchARGS(index="person", query=query, from_=from_, size=page_size)
