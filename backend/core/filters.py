from admin_auto_filters.filters import AutocompleteFilter


class AuthorFilter(AutocompleteFilter):
    """
    Фильтр для админки,
    позволяющий искать записи на основе поля 'author'.
    """

    title = "Автор"
    field_name = "author"


class TagsFilter(AutocompleteFilter):
    """
    Фильтр для админки,
    позволяющий искать записи на основе поля 'tags'.
    """

    title = "Тег"
    field_name = "tags"


class IngredientsFilter(AutocompleteFilter):
    """
    Фильтр для админки,
    позволяющий искать записи на основе поля 'ingredients'.
    """

    title = "Ингредиент"
    field_name = "ingredients"
