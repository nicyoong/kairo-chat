from datetime import datetime


def _init_trait_router(self):
    init_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{init_time}] Trait router initializing...")
    """
    Create a dictionary mapping question patterns to (getter_function, response_templates).
    Each entry defines: how to detect the question, what getter to use, and how to respond.
    """
    self.trait_router = [
        {
            "patterns": [
                "what's your name",
                "what is your name",
                "tell me your full name",
                "can you tell me your name",
                "what should i call you",
            ],
            "getter": self.get_full_name,
            "responses": [
                "Oh, I'm {}!",
                "My name's {}, nice to meet you!",
            ],
        },
        {
            "patterns": [
                "how old are you",
                "what's your age",
                "what is your age",
                "can you tell me your age",
            ],
            "getter": self.get_age,
            "responses": [
                "I'm {} this year.",
                "{} years old.",
            ],
        },