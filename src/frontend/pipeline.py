import os
import subprocess
import torch
from transformers import AutoModel
from TTS.api import TTS
from unittest.mock import patch

# Set the root path relative to this script’s directory
# root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "/kaggle/working/"))

# Define paths based on your directory structure
raw_image_path = os.path.join(root_path, "input/raw")
character_path = os.path.join(root_path, "input/character")
raw_image_rename_path = os.path.join(root_path, "output/renamed")
colorized_path = os.path.join(root_path, "output/colorized")
json_path = os.path.join(root_path, "output/json")
transcript_path = os.path.join(root_path, "output/transcript")
audio_path = os.path.join(root_path, "output/audio")
final_output_path = os.path.join(root_path, "output/output_final")
voice_bank = os.path.join(root_path, "/kaggle/input/ravdess-emotional-speech-audio/")
transcript_file = os.path.join(transcript_path, "transcript.txt")

# Ensure all output directories exist
os.makedirs(raw_image_rename_path, exist_ok=True)
os.makedirs(colorized_path, exist_ok=True)
os.makedirs(json_path, exist_ok=True)
os.makedirs(transcript_path, exist_ok=True)
os.makedirs(audio_path, exist_ok=True)
os.makedirs(final_output_path, exist_ok=True)

# Check for GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on {device}")

# Initialize submodules in `manga_read_along` and `manga-colorization-v2-custom`
print("Initializing submodules...")
for submodule in ["manga_read_along", "manga-colorization-v2-custom"]:
    submodule_path = os.path.join(root_path, submodule)
    result = subprocess.run(["git", "submodule", "init"], cwd=submodule_path)
    if result.returncode != 0:
        print(f"Error initializing submodule {submodule}: {result.stderr}")
    result = subprocess.run(["git", "submodule", "update", "--remote"], cwd=submodule_path)
    if result.returncode != 0:
        print(f"Error updating submodule {submodule}: {result.stderr}")

print("Installing dependencies...")
result = subprocess.run(["pip", "install", "-r", os.path.join(root_path, "magi_functional/requirements_kaggle.txt")])
if result.returncode != 0:
    print(f"Error installing dependencies: {result.stderr}")

# Load MAGI model
print("Loading MAGI model...")
magiv2 = AutoModel.from_pretrained("ragavsachdeva/magiv2", trust_remote_code=True).to(device).eval()

# Download colorization model weights if they don’t already exist
colorization_model_path = os.path.join(root_path, "manga-colorization-v2-custom/networks/generator.zip")
denoising_model_path = os.path.join(root_path, "manga-colorization-v2-custom/denoising/models/net_rgb.pth")
if not os.path.exists(colorization_model_path):
    print("Downloading colorization model weights...")
    subprocess.run([
        "gdown", "1qmxUEKADkEM4iYLp1fpPLLKnfZ6tcF-t",
        "-O", colorization_model_path
    ])
if not os.path.exists(denoising_model_path):
    os.makedirs(os.path.dirname(denoising_model_path), exist_ok=True)
    subprocess.run([
        "gdown", "161oyQcYpdkVdw8gKz_MA8RD-Wtg9XDp3",
        "-O", denoising_model_path
    ])

# Step 1: Run magiv2.py
print("Running magiv2.py...")
result = subprocess.run([
    "python", os.path.join(root_path, "magi_functional/magiv2.py"),
    "--image", raw_image_path,
    "--rename_image", raw_image_rename_path,
    "--character", character_path,
    "--json", json_path,
    "--transcript", transcript_path
])
if result.returncode != 0:
    print(f"Error in magiv2.py: {result.stderr}")

# Step 2: Run inference_v2.py for colorization
print("Running inference_v2.py...")
result = subprocess.run([
    "python", os.path.join(root_path, "manga-colorization-v2-custom/inference_v2.py"),
    "-p", raw_image_rename_path,
    "-des_path", denoising_model_path,
    "-gen", colorization_model_path,
    "-s", colorized_path,
    "-ds", "0",
    "--gpu"
])
if result.returncode != 0:
    print(f"Error in inference_v2.py: {result.stderr}")

# Step 3: Text-to-speech
print("Setting up text-to-speech...")
with patch('builtins.input', return_value='y'):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

print("Running text_to_speech.py...")
result = subprocess.run([
    "python", os.path.join(root_path, "magi_functional/text_to_speech.py"),
    "-i", raw_image_rename_path,
    "-v", voice_bank,
    "-t", transcript_file,
    "-o", audio_path,
    "-m", "male_character"
])
if result.returncode != 0:
    print(f"Error in text_to_speech.py: {result.stderr}")

# Step 4: Combine in main_final.py
print("Running main_final.py...")
result = subprocess.run([
    "python", os.path.join(root_path, "magi_functional/main.py"),
    "-i", colorized_path,
    "-j", json_path,
    "-a", audio_path,
    "-s", final_output_path
])
if result.returncode != 0:
    print(f"Error in main_final.py: {result.stderr}")

print("Pipeline completed successfully!")