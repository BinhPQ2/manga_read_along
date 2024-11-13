import os
import sys
sys.path.append(os.path.abspath('/kaggle/working/manga_read_along'))

import shutil
import subprocess
import torch
from transformers import AutoModel
from TTS.api import TTS
from unittest.mock import patch
from src.config import (
    ROOT_PATH, RAW_IMAGE_PATH, CHARACTER_PATH, VOICE_BANK, OUTPUT_PATH,
    RAW_IMAGE_RENAME_PATH, COLORIZED_PATH, JSON_PATH, TRANSCRIPT_PATH,
    TRANSCRIPT_FILE, AUDIO_PATH, FINAL_OUTPUT_PATH
)

def pipeline(is_colorization: bool, is_panel_view: bool):
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(RAW_IMAGE_RENAME_PATH, exist_ok=True)
    os.makedirs(COLORIZED_PATH, exist_ok=True)
    os.makedirs(JSON_PATH, exist_ok=True)
    os.makedirs(TRANSCRIPT_PATH, exist_ok=True)
    os.makedirs(AUDIO_PATH, exist_ok=True)
    os.makedirs(FINAL_OUTPUT_PATH, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on {device}", flush=True)
    print("Initializing submodules...", flush=True)
    for submodule in ["manga_read_along", "manga_read_along/manga-colorization-v2-custom"]:
        submodule_path = os.path.join(ROOT_PATH, submodule)
        result = subprocess.run(["git", "submodule", "init"], cwd=submodule_path)
        if result.returncode != 0:
            print(f"Error initializing submodule {submodule}: {result.stderr}")
        result = subprocess.run(["git", "submodule", "update", "--remote"], cwd=submodule_path)
        if result.returncode != 0:
            print(f"Error updating submodule {submodule}: {result.stderr}")

    print("Running magiv2.py...", flush=True)
    result = subprocess.run([
        "python", os.path.join(ROOT_PATH, "manga_read_along/magi_functional/magiv2.py"),
        "--image", RAW_IMAGE_PATH,
        "--rename_image", RAW_IMAGE_RENAME_PATH,
        "--character", CHARACTER_PATH,
        "--json", JSON_PATH,
        "--transcript", TRANSCRIPT_PATH
    ])
    if result.returncode != 0:
        print(f"Error in magiv2.py: {result.stderr}", flush=True)

    if is_colorization:
        print("Running inference_v2.py...", flush=True)
        result = subprocess.run([
            "python", os.path.join(ROOT_PATH, "manga_read_along/manga-colorization-v2-custom/inference_v2.py"),
            "-p", RAW_IMAGE_RENAME_PATH,
            "-des_path", os.path.join(ROOT_PATH, "manga_read_along/manga-colorization-v2-custom/denoising/models/net_rgb.pth"),
            "-gen", os.path.join(ROOT_PATH, "manga_read_along/manga-colorization-v2-custom/networks/generator.zip"),
            "-s", COLORIZED_PATH,
            "-ds", "0",
            "--gpu"
        ])
        if result.returncode != 0:
            print(f"Error in inference_v2.py: {result.stderr}", flush=True)

    print("Running text_to_speech.py...", flush=True)
    result = subprocess.run([
        "python", os.path.join(ROOT_PATH, "manga_read_along/magi_functional/text_to_speech.py"),
        "-i", RAW_IMAGE_RENAME_PATH,
        "-v", VOICE_BANK,
        "-t", TRANSCRIPT_FILE,
        "-o", AUDIO_PATH,
        "-m", "male_character"
    ])
    if result.returncode != 0:
        print(f"Error in text_to_speech.py: {result.stderr}", flush=True)

    print("Running main.py...", flush=True)
    result = subprocess.run([
        "python", os.path.join(ROOT_PATH, "manga_read_along/magi_functional/main.py"),
        "-i", COLORIZED_PATH if is_colorization else RAW_IMAGE_RENAME_PATH,
        "-j", JSON_PATH,
        "-a", AUDIO_PATH,
        "-s", FINAL_OUTPUT_PATH,
        "-panel", str(is_panel_view)
    ])
    if result.returncode != 0:
        print(f"Error in main.py: {result.stderr}", flush=True)

    generated_video_path = os.path.join(FINAL_OUTPUT_PATH, "video_Padding_True_audio.mp4")
    reencoded_video_path = os.path.splitext(generated_video_path)[0] + "_reencoded.mp4"
    if os.path.exists(generated_video_path):
        print("Re-encoding final video...", flush=True)
        try:
            result = subprocess.run([
                "ffmpeg", "-i", generated_video_path, "-c:v", "libx264", "-c:a", "aac",
                "-strict", "experimental", reencoded_video_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Re-encoding completed successfully.", flush=True)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error during video re-encoding: {e}", flush=True)
            print(e.stderr.decode())
            return False
    else:
        print("Generated video not found for re-encoding.", flush=True)
        return False

    print("Pipeline completed successfully!", flush=True)
    return True

if __name__ == "__main__":
    pipeline(is_colorization=True, is_panel_view=True)