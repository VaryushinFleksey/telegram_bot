# Список погонял
NICKNAMES = [
    "чел",
    "дружбан",
    "крушон",
]

def add_nickname(nickname):
    """Добавляет новое погоняло в список"""
    global NICKNAMES
    
    # Проверяем, нет ли уже такого погоняла
    if nickname in NICKNAMES:
        return False
    
    # Добавляем новое погоняло в список
    NICKNAMES.append(nickname)
    
    # Формируем новое содержимое файла
    new_content = "# Список погонял\nNICKNAMES = [\n"
    
    # Добавляем все погоняла
    for nick in NICKNAMES:
        new_content += f'    "{nick}",\n'
    
    # Закрываем список и добавляем функцию
    new_content += "]\n\n"
    new_content += '''def add_nickname(nickname):
    """Добавляет новое погоняло в список"""
    global NICKNAMES
    
    # Проверяем, нет ли уже такого погоняла
    if nickname in NICKNAMES:
        return False
    
    # Добавляем новое погоняло в список
    NICKNAMES.append(nickname)
    
    # Формируем новое содержимое файла
    new_content = "# Список погонял\\nNICKNAMES = [\\n"
    
    # Добавляем все погоняла
    for nick in NICKNAMES:
        new_content += f'    "{nick}",\\n'
    
    # Закрываем список и добавляем функцию
    new_content += "]\\n\\n"
    
    # Записываем обновленный файл
    with open(__file__, "w", encoding="utf-8") as file:
        file.write(new_content)
    
    return True'''
    
    # Записываем обновленный файл
    with open(__file__, "w", encoding="utf-8") as file:
        file.write(new_content)
    
    return True