class CharacterProfile(dict):
    """Wrapper around dict that supports dot-path lookups like 'education.university'."""

    def __init__(self, data=None):
        super().__init__(data or {})

    def get_trait(self, path: str, default=None):
        keys = path.split(".")
        value = self
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value