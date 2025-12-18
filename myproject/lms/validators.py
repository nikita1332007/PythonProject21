from rest_framework.exceptions import ValidationError

def validate_youtube_link(value):
    """
    Проверяет, что ссылка принадлежит youtube.com или youtu.be
    """
    allowed_domains = ['youtube.com', 'youtu.be']
    if not any(domain in value for domain in allowed_domains):
        raise ValidationError('Ссылка должна быть с доменов youtube.com или youtu.be')
    return value