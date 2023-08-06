import os

git_voice_download = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

os.system(f"cd {git_voice_download} && git init  && git remote add origin "
          f"https://github.com/prakashr7d/ruth-tts-files.git && "
          f"git pull origin main && git checkout main -f  ")
