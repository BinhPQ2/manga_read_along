import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import os
import subprocess
import torch
from transformers import AutoModel
from TTS.api import TTS
from unittest.mock import patch

# Load Lottie animation
@st.cache_data()
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Streamlit UI setup
st.set_page_config(page_title="Manga Video Generator Interface", page_icon=":movie_camera:", layout="wide")
st.title(":movie_camera: Manga Video Generator Interface")

with st.sidebar:
    lottie = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_cjnxwrkt.json")
    st_lottie(lottie)
    st.button("Upgrade to Plus", icon="🗝️", use_container_width=True)
    st.header("Team Info")
    with st.expander("", expanded=True):
        st.write("23C11018 - Phạm Quốc Bình")
        st.write("23C11054 - Nguyễn Khắc Toàn")
        st.write("23C15030 - Nguyễn Vũ Linh")
        st.write("23C15037 - Bùi Trọng Quý")
    st.header("Instructions")
    st.write("**Step 1**: Upload Chapter Pages and Character Reference Images.")
    st.write("**Step 2**: Enter Character Names (comma separated).")
    st.write("**Step 3**: Check the Colorization checkbox if needed.")
    st.write("**Step 4**: Click 'Generate Video' to generate the video.")
    st.write("**Step 5**: Click 'Clear' to clear all input fields.")

# Ensure directories exist
root_path = "/kaggle/working/"  # Update if necessary
raw_image_path = os.path.join(root_path, "manga_read_along/input/raw")
character_path = os.path.join(root_path, "manga_read_along/input/character")
raw_image_rename_path = os.path.join(root_path, "output/renamed")
colorized_path = os.path.join(root_path, "output/colorized")
json_path = os.path.join(root_path, "output/json")
transcript_path = os.path.join(root_path, "output/transcript")
audio_path = os.path.join(root_path, "output/audio")
final_output_path = os.path.join(root_path, "output/output_final")
voice_bank = os.path.join(root_path, "/kaggle/input/ravdess-emotional-speech-audio/")

for path in [raw_image_path, character_path, raw_image_rename_path, colorized_path, json_path, transcript_path, audio_path, final_output_path]:
    os.makedirs(path, exist_ok=True)

# UI file upload and input
st.header("Upload Chapter Pages")
chapter_files = st.file_uploader("Upload images for Chapter Pages", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
st.header("Upload Character Reference Images")
character_files = st.file_uploader("Upload images for Character Reference", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
st.header("Character Names")
character_names = st.text_input("Enter Character Names (comma separated)", placeholder="Luffy,Hank,Nami")
colorize = st.checkbox("Colorization")

# Function to save uploaded files
def save_uploaded_files(files, directory):
    for file in files:
        with open(os.path.join(directory, file.name), "wb") as f:
            f.write(file.getbuffer())

# Initialize session state
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "progress_complete" not in st.session_state:
    st.session_state.progress_complete = False

left, right = st.columns(2)

if left.button("Generate Video", icon="🔥", use_container_width=True):
    if chapter_files and character_files:
        st.session_state.video_url = ""
        st.session_state.progress_complete = False

        # Save the uploaded files to respective directories
        save_uploaded_files(chapter_files, raw_image_path)
        save_uploaded_files(character_files, character_path)

        with open(os.path.join(character_path, "character_names.txt"), "w") as f:
            f.write(character_names)

        # Run the pipeline steps within Streamlit
        progress_text = "Generating video in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        percent_complete = 0

        def update_progress(increment=10):
            nonlocal percent_complete
            percent_complete += increment
            my_bar.progress(min(percent_complete, 100), text=progress_text)
        
        # Step 1: Initialize MAGI model
        update_progress()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        magiv2 = AutoModel.from_pretrained("ragavsachdeva/magiv2", trust_remote_code=True).to(device).eval()

        # Step 2: Run MAGI processing
        update_progress()
        result = subprocess.run([
            "python", os.path.join(root_path, "manga_read_along/magi_functional/magiv2.py"),
            "--image", raw_image_path,
            "--rename_image", raw_image_rename_path,
            "--character", character_path,
            "--json", json_path,
            "--transcript", transcript_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("Error in MAGI processing.")
            print(result.stderr)

        # Step 3: Run colorization if selected
        update_progress()
        if colorize:
            result = subprocess.run([
                "python", os.path.join(root_path, "manga_read_along/manga-colorization-v2-custom/inference_v2.py"),
                "-p", raw_image_rename_path,
                "-des_path", colorization_model_path,
                "-gen", denoising_model_path,
                "-s", colorized_path,
                "-ds", "0",
                "--gpu"
            ], capture_output=True, text=True)
            if result.returncode != 0:
                st.error("Error in colorization.")
                print(result.stderr)

        # Step 4: Text-to-speech
        update_progress()
        with patch('builtins.input', return_value='y'):
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        result = subprocess.run([
            "python", os.path.join(root_path, "manga_read_along/magi_functional/text_to_speech.py"),
            "-i", raw_image_rename_path,
            "-v", voice_bank,
            "-t", os.path.join(transcript_path, "transcript.txt"),
            "-o", audio_path,
            "-m", "male_character"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("Error in text-to-speech processing.")
            print(result.stderr)

        # Step 5: Final video assembly
        update_progress()
        result = subprocess.run([
            "python", os.path.join(root_path, "manga_read_along/magi_functional/main.py"),
            "-i", colorized_path if colorize else raw_image_rename_path,
            "-j", json_path,
            "-a", audio_path,
            "-s", final_output_path
        ], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("Error in final video assembly.")
            print(result.stderr)

        # Check if the video was generated successfully
        my_bar.empty()
        generated_video_path = os.path.join(final_output_path, "video_Padding_True.mp4")
        if os.path.exists(generated_video_path):
            st.session_state.video_url = generated_video_path
            st.session_state.progress_complete = True
            st.success("Video generated successfully!")
        else:
            st.session_state.video_url = "https://files.vuxlinh.com/demo.mp4"
            st.warning("An error occurred or the video file was not found. Displaying the default video.")
    else:
        st.error("Please fill in all required fields before generating the video.")

if right.button("Clear", icon="💣", use_container_width=True):
    st.session_state.video_url = ""
    st.session_state.progress_complete = False
    st.query_params.update({})

# Display video
st.header("Play Output Video")
if st.session_state.video_url:
    video_html = f"""
        <div style="width: 100%; height: auto;">
            <video width="100%" height="720" controls>
                <source src="{st.session_state.video_url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    """
    st.markdown(video_html, unsafe_allow_html=True)
else:
    st.write("No video to display. Click 'Generate Video' to load the video.")
