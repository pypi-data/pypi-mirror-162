# Imports used through the rest of the notebook.
import hashlib
import os
import pickle
from datetime import datetime
from typing import Text

import torchaudio

from ruth_tts_transformer.parser import TextToSpeech
from ruth_tts_transformer.utils.audio import load_voice


class TTS:
    def __init__(self):
        self.gen = None
        self.voice = None
        self.preset = "ultra_fast"
        self.tts = TextToSpeech(autoregressive_batch_size=16)
        self.voice_samples_gabby_reading, self.conditioning_latent_reading = \
            load_voice("gabby_reading")
        self.voice_samples_gabby_convo, self.conditioning_latent_convo = \
            load_voice("gabby_convo")

    def generate(self, text, voice: Text = "gabby_reading"):
        if voice == "gabby_reading":
            self.gen, _ = self.tts.tts(text,
                                       conditioning_latents=self.conditioning_latent_reading,
                                       use_deterministic_seed=0,
                                       return_deterministic_state=True,
                                       num_autoregressive_samples=16,
                                       diffusion_iterations=30)
        else:
            self.gen, _ = self.tts.tts(text,
                                       conditioning_latents=self.conditioning_latent_convo,
                                       use_deterministic_seed=0,
                                       return_deterministic_state=True,
                                       num_autoregressive_samples=16,
                                       diffusion_iterations=30)

    def parse(self):
        file_name = hashlib.sha1(str(datetime.now()).encode("UTF-8"))
        torchaudio.save(file_name.hexdigest() + '.wav', self.gen.squeeze(0).cpu(), 24000)
        return file_name.hexdigest()
