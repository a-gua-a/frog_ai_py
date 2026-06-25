import os

class Voice:
    def __init__(self):
        self.voice_id = os.getenv("VOICE_ID")

    def setVoiceId(self,voice_id):
        self.voice_id = voice_id

voice = Voice()