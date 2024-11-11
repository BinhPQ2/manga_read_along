import os
import subprocess
import torch
from transformers import AutoModel
from TTS.api import TTS
from unittest.mock import patch

def pipeline(is_colorization: bool, is_panel_view: bool):
    root_path = "/kaggle/working/"

    raw_image_path = os.path.join(root_path, "manga_read_along/input/raw")
    character_path = os.path.join(root_path, "manga_read_along/input/character")
    raw_image_rename_path = os.path.join(root_path, "output/renamed")
    colorized_path = os.path.join(root_path, "output/colorized")
    json_path = os.path.join(root_path, "output/json")
    transcript_path = os.path.join(root_path, "output/transcript")
    audio_path = os.path.join(root_path, "output/audio")
    final_output_path = os.path.join(root_path, "output/output_final")
    voice_bank = os.path.join(root_path, "/kaggle/input/ravdess-emotional-speech-audio/")
    transcript_file = os.path.join(transcript_path, "transcript.txt")

    os.makedirs(raw_image_rename_path, exist_ok=True)
    os.makedirs(colorized_path, exist_ok=True)
    os.makedirs(json_path, exist_ok=True)
    os.makedirs(transcript_path, exist_ok=True)
    os.makedirs(audio_path, exist_ok=True)
    os.makedirs(final_output_path, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Running on {device}", flush=True)

    print("Initializing submodules...", flush=True)
    for submodule in ["manga_read_along", "manga_read_along/manga-colorization-v2-custom"]:
        submodule_path = os.path.join(root_path, submodule)
        result = subprocess.run(["git", "submodule", "init"], cwd=submodule_path)
        if result.returncode != 0:
            print(f"Error initializing submodule {submodule}: {result.stderr}")
        result = subprocess.run(["git", "submodule", "update", "--remote"], cwd=submodule_path)
        if result.returncode != 0:
            print(f"Error updating submodule {submodule}: {result.stderr}")

    print("Loading MAGI model...", flush=True)
    _ = AutoModel.from_pretrained("ragavsachdeva/magiv2", trust_remote_code=True).to(device).eval()

    colorization_model_path = os.path.join(root_path, "manga_read_along/manga-colorization-v2-custom/networks/generator.zip")
    denoising_model_path = os.path.join(root_path, "manga_read_along/manga-colorization-v2-custom/denoising/models/net_rgb.pth")
    if not os.path.exists(colorization_model_path):
        print("Downloading colorization model weights...", flush=True)
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
  
    _ = subprocess.run(["pip", "install", "-q", "numpy==1.24.2", "tensorflow==2.10.0", "--upgrade"])
        
    # Step 1: Run magiv2.py
    print("Running magiv2.py...", flush=True)
    result = subprocess.run([
        "python", os.path.join(root_path, "manga_read_along/magi_functional/magiv2.py"),
        "--image", raw_image_path,
        "--rename_image", raw_image_rename_path,
        "--character", character_path,
        "--json", json_path,
        "--transcript", transcript_path
    ])
    if result.returncode != 0:
        print(f"Error in magiv2.py: {result.stderr}", flush=True)
    
    if is_colorization:
        # Step 2: Run inference_v2.py for colorization
        print("Running inference_v2.py...", flush=True)
        result = subprocess.run([
            "python", os.path.join(root_path, "manga_read_along/manga-colorization-v2-custom/inference_v2.py"),
            "-p", raw_image_rename_path,
            "-des_path", denoising_model_path,
            "-gen", colorization_model_path,
            "-s", colorized_path,
            "-ds", "0",
            "--gpu"
        ])
        if result.returncode != 0:
            print(f"Error in inference_v2.py: {result.stderr}", flush=True)
    
    _ = subprocess.run(["pip", "install", "-q", "packaging==21.3", "--upgrade"]) 
    
    # Step 3: Text-to-speech
    print("Setting up text-to-speech...", flush=True)
    with patch('builtins.input', return_value='y'):
        try:
            _ = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())
        except Exception as e:
            print(f"Error during TTS setup: {e}", flush=True)

    print("Running text_to_speech.py...", flush=True)
    result = subprocess.run([
        "python", os.path.join(root_path, "manga_read_along/magi_functional/text_to_speech.py"),
        "-i", raw_image_rename_path,
        "-v", voice_bank,
        "-t", transcript_file,
        "-o", audio_path,
        "-m", "male_character"
    ])

    if result.returncode != 0:
        print(f"Error in text_to_speech.py: {result.stderr}", flush=True)

    # Step 4: Combine in main.py
    print("Running main.py...", flush=True)
    result = subprocess.run([
        "python", os.path.join(root_path, "manga_read_along/magi_functional/main.py"),
        "-i", colorized_path,
        "-j", json_path,
        "-a", audio_path,
        "-s", final_output_path, 
        "-panel", is_panel_view
    ])
    if result.returncode != 0:
        print(f"Error in main_final.py: {result.stderr}", flush=True)

    # Step 5: Re-encode final video
    generated_video_path = os.path.join(final_output_path, "video_Padding_True_audio.mp4")  # Use final output with audio merged
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
    pipeline(is_colorization=True)