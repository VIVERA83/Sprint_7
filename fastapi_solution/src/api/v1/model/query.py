from fastapi import Query

QuerySort = Query(
    default=None,
    description="Сортировка фильмов по рейтингу, "
    "по умолчанию фильмы отсортированы по максимальному рейтингу",
)
QueryGenre = Query(
    default=None,
    description="Фильтрация по жанру, по умолчанию фильтрация отключена",
)
QueryPageSize = Query(
    default=None,
    alias="page[size]",
    title="Какие то страницы",
    description="Кол-во записей которое будет возвращены в ответе, по умолчанию 100",
    gt=0,
    example=100,
)
QueryPageNumber = Query(
    default=None,
    alias="page[number]",
    title="Какие то страницы",
    description="Вернет записи начина с указанной страницы, то есть page_size*page_number",
    gt=0,
    example=1,
)

QueryCaption = Query(
    default=None, description="Поиск по названию фильма", example="Star Wars"
)

QueryPerson = Query(
    default=None,
    description="Фильтрация по персоне, по умолчанию фильтрация отключена",
    example="George Lucas",
)
