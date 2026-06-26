def normalize_department_codes(value) -> list[str]:
    """
    Приводит departmentCodes из iiko XML к списку строк.

    iiko отдаёт одно значение строкой, несколько — списком повторяющихся тегов.
    """
    if value is None or value == "NULL":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "NULL")]
    return [str(value)]
