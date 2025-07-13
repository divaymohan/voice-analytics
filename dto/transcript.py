from pydantic import BaseModel

class TranscriptInput(BaseModel):
    transcript: str
    language: str = "auto"  # e.g., "en", "hi", "auto"
    