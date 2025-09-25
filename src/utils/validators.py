def is_valid_url(url: str) -> bool:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc]) and len(url) > 0


def validate_bookmark_data(data: dict) -> bool:
    required_fields = ['url', 'title']
    return all(field in data for field in required_fields) and is_valid_url(data['url'])