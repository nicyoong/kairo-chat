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
    
    # Legal / documents / transport
    def has_drivers_license(self):
        return bool(self.character_profile.get_trait("has_drivers_license"))

    def has_passport(self):
        return bool(self.character_profile.get_trait("has_passport"))

    def get_passport_country(self):
        return self.character_profile.get_trait("passport_country")

    def get_vehicle_owned(self):
        return self.character_profile.get_trait("vehicle_owned")
    
    # Residence
    def get_country(self):
        return self.character_profile.get_trait("residence.country")

    def get_state(self):
        return self.character_profile.get_trait("residence.state")

    def get_city(self):
        return self.character_profile.get_trait("residence.city")

    def get_area(self):
        return self.character_profile.get_trait("residence.area")
    
    def get_postal_code(self):
        return self.character_profile.get_trait("residence.postal_code")

    def get_housing_type(self):
        return self.character_profile.get_trait("residence.housing_type")

    def get_living_with(self):
        return self.character_profile.get_trait("residence.living_with")
    
    # Education
    def get_university(self):
        return self.character_profile.get_trait("education.university")

    def get_degree(self):
        return self.character_profile.get_trait("education.degree")

    def get_field_of_study(self):
        return self.character_profile.get_trait(
            "education.field"
        ) or self.character_profile.get_trait("education.major")

    def get_graduation_year(self):
        return self.character_profile.get_trait("education.graduation_year")
    
    # Career
    def get_job_title(self):
        return self.character_profile.get_trait("career.title")

    def get_industry(self):
        return self.character_profile.get_trait("career.industry")

    def get_employment_type(self):
        return self.character_profile.get_trait("career.employment_type")

    def get_experience_level(self):
        return self.character_profile.get_trait("career.experience_level")

    def get_work_location(self):
        return self.character_profile.get_trait("career.work_location")