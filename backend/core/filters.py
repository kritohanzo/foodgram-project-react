from admin_auto_filters.filters import AutocompleteFilter


class NameFilter(AutocompleteFilter):
    """
    Фильтр для админки,
    позволяющий искать записи на основе поля 'name'.
    """
    title = 'Название'
    field_name = 'name'


class AuthorFilter(AutocompleteFilter):
    """
    Фильтр для админки,
    позволяющий искать записи на основе поля 'author'.
    """
    title = 'Автор'
    field_name = 'author'


class TagsFilter(AutocompleteFilter):
    """
    Фильтр для админки,
    позволяющий искать записи на основе поля 'tags'.
    """
    title = 'Теги'
    field_name = 'tags'
