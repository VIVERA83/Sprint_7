from src.models.search_args import SearchARGS


class GenreSearchParams:
    @staticmethod
    def get_search_parameters_by_genres(page_size: int = None) -> SearchARGS:
        page_size = page_size or 100
        query = {"match_all": {}}
        return SearchARGS(index="genre", query=query, size=page_size)
