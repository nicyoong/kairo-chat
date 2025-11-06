import random
from datetime import datetime


def attach_trait_getters(cls):
    """Dynamically attach all getter methods to ShapeChatBot."""

    # Identity
    def get_id(self):
        return self.character_profile.get_trait("id")

    def get_full_name(self):
        return self.character_profile.get_trait("full_name")

    def get_short_name(self):
        return self.character_profile.get_trait("short_name")

    def get_chinese_name(self):
        return self.character_profile.get_trait("chinese_name")
    
    def get_gender(self):
        return self.character_profile.get_trait("gender")

    def get_citizenship(self):
        return self.character_profile.get_trait("citizenship")

    def get_ethnicity(self):
        return self.character_profile.get_trait("ethnicity")
    
    def get_primary_language(self):
        return self.character_profile.get_trait("primary_language")

    def get_other_languages(self):
        return self.character_profile.get_trait("other_languages", [])

    def get_religion(self):
        return self.character_profile.get_trait("religion")

    def get_citizen_id_prefix(self):
        return self.character_profile.get_trait("citizen_id_prefix")
    
    # Age & Birthday
    def get_birthday(self):
        date_str = self.character_profile.get_trait("birthday")
        if not date_str:
            return None
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return random.choice([dt.strftime("%B %d, %Y"), dt.strftime("%B %d")])
        except ValueError:
            return date_str
        
    def get_age(self):
        return self.character_profile.get_trait("age")