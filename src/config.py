# config.py

import os

ROOT_PATH = "/kaggle/working/"

RAW_IMAGE_PATH = os.path.join(ROOT_PATH, "manga_read_along/input/raw")
CHARACTER_PATH = os.path.join(ROOT_PATH, "manga_read_along/input/character")
VOICE_BANK = os.path.join(ROOT_PATH, "manga_read_along/input/voice_bank")

OUTPUT_PATH = os.path.join(ROOT_PATH, "output")
RAW_IMAGE_RENAME_PATH = os.path.join(OUTPUT_PATH, "renamed")
COLORIZED_PATH = os.path.join(OUTPUT_PATH, "colorized")
JSON_PATH = os.path.join(OUTPUT_PATH, "json")
TRANSCRIPT_PATH = os.path.join(OUTPUT_PATH, "transcript")
TRANSCRIPT_FILE = os.path.join(TRANSCRIPT_PATH, "transcript.txt")
AUDIO_PATH = os.path.join(OUTPUT_PATH, "audio")
FINAL_OUTPUT_PATH = os.path.join(OUTPUT_PATH, "output_final")
GENERATED_VIDEO_PATH = os.path.join(FINAL_OUTPUT_PATH, "video_Padding_True.mp4")
REENCODED_VIDEO_PATH = os.path.splitext(GENERATED_VIDEO_PATH)[0] + "_reencoded.mp4"