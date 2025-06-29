def generate_pagination(total_pages: int, visible_pages: int, current_page: int) -> list:
    if visible_pages >= total_pages:
        return list(range(1, total_pages + 1))
    l_offset = visible_pages // 2
    r_offset = visible_pages - l_offset - 1
    if current_page < l_offset:
        return list(range(1, visible_pages)) + [total_pages]
    if current_page > total_pages - r_offset:
        return [1] + list(range(total_pages - visible_pages + 2, total_pages + 1))
    return [1] + list(range(current_page - l_offset + 1, current_page + r_offset)) + [total_pages]
