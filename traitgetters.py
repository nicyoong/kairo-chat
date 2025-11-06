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