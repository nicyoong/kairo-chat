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
    
    # Family (you’ll fill this later; getters still safe)
    def get_family(self):
        return self.character_profile.get_trait("family", {})
    
    # Relationship & pets
    def get_relationship_status(self):
        return self.character_profile.get_trait("relationship_status")

    def get_pets(self):
        return self.character_profile.get_trait("pets")
    
    # Digital presence
    def get_primary_messaging_app(self):
        return self.character_profile.get_trait("digital_presence.main_messaging_app")

    def get_secondary_app(self):
        return self.character_profile.get_trait("digital_presence.secondary_app")

    def has_tiktok(self):
        return bool(self.character_profile.get_trait("digital_presence.has_tiktok"))

    def uses_online_banking(self):
        return bool(self.character_profile.get_trait("digital_presence.uses_online_banking"))

    def get_cloud_storage(self):
        return self.character_profile.get_trait("digital_presence.cloud_storage", [])
    
    # ===== PHYSICAL TRAITS =====
    def get_height(self):
        return self.character_profile.get_trait("physical.height_cm")

    def get_blood_type(self):
        return self.character_profile.get_trait("physical.blood_type")

    def get_allergies(self):
        return self.character_profile.get_trait("physical.allergies")
    
    # Interests and hobbies
    def get_random_hobby(self):
        hobbies = self.character_profile.get_trait("interests_and_hobbies.hobbies", [])
        return random.choice(hobbies) if hobbies else None

    def get_random_favorite_music_genre(self):
        genres = self.character_profile.get_trait("interests_and_hobbies.favorite_music_genres", [])
        return random.choice(genres) if genres else None

    def get_random_favorite_movie(self):
        movies = self.character_profile.get_trait("interests_and_hobbies.favorite_movies", [])
        return random.choice(movies) if movies else None
    
    def get_random_favorite_food(self):
        foods = self.character_profile.get_trait("interests_and_hobbies.favorite_foods", [])
        return random.choice(foods) if foods else None

    def get_random_favorite_drink(self):
        drinks = self.character_profile.get_trait("interests_and_hobbies.favorite_drinks", [])
        return random.choice(drinks) if drinks else None

    def get_random_preferred_hangout_spot(self):
        spots = self.character_profile.get_trait(
            "interests_and_hobbies.preferred_hangout_spots", []
        )
        return random.choice(spots) if spots else None
    
    def get_travel_preference(self):
        return self.character_profile.get_trait("interests_and_hobbies.travel_preference")

    def get_personality_fun(self):
        return self.character_profile.get_trait("personality_fun")

    def get_personality_serious(self):
        return self.character_profile.get_trait("personality_serious")
    
    # attach all trait getters to class
    cls.get_id = get_id
    cls.get_full_name = get_full_name
    cls.get_short_name = get_short_name
    cls.get_chinese_name = get_chinese_name
    cls.get_gender = get_gender
    cls.get_citizenship = get_citizenship
    cls.get_ethnicity = get_ethnicity
    cls.get_primary_language = get_primary_language
    cls.get_other_languages = get_other_languages
    cls.get_religion = get_religion
    cls.get_citizen_id_prefix = get_citizen_id_prefix

    cls.get_birthday = get_birthday
    cls.get_age = get_age

    cls.has_drivers_license = has_drivers_license
    cls.has_passport = has_passport
    cls.get_passport_country = get_passport_country
    cls.get_vehicle_owned = get_vehicle_owned