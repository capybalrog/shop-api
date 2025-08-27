from django.utils.html import format_html

def get_image_preview(obj, field_name='image'):
    """Функция для вывода превью картинки в админке."""
    image_field = getattr(obj, field_name, None)
    if image_field and hasattr(image_field, 'url'):
        return format_html(
            '<img src="{}" style="max-height: 50px;"/>',
            image_field.url
        )
    return '-'
