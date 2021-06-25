import re

def urlparse(url, schemes=None):
    schemes = schemes or ["http", "https"]
    parts = url.split("://", 1)
    assert len(parts) == 2, "scheme not found"
    scheme, location = parts[0], parts[1]
    assert scheme in schemes, "invalid scheme"
    assert re.match("^[\w\d\.-]+$", location), "invalid domain name"
    return scheme, location
