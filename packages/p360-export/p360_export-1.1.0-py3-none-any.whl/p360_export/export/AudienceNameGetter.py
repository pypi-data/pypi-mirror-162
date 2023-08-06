class AudienceNameGetter:
    def get(self, config: dict) -> str:
        persona = config["personas"][0]
        return f"{persona['persona_name']}-{persona['persona_id']}"
