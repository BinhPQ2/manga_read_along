import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import validators

@st.cache_data()
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def validate_urls(url_list):
    invalid_urls = [url for url in url_list if url and not validators.url(url)]
    return invalid_urls

st.set_page_config(page_title="Manga Video Generator Interface", page_icon=":movie_camera:", layout="wide")
st.title(":movie_camera: Manga Video Generator Interface")

with st.sidebar:
    # https://assets1.lottiefiles.com/packages/lf20_HjK9Ol.json
    # https://assets6.lottiefiles.com/packages/lf20_cjnxwrkt.json
    # https://assets8.lottiefiles.com/packages/lf20_jh9gfdye.json
    lottie = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_cjnxwrkt.json")
    st_lottie(lottie)

    st.button("Upgrade to Plus", icon="🗝️", use_container_width=True)

    st.header("Team Info")
    with st.expander("",expanded=True):
            st.write("23C11018 - Phạm Quốc Bình")
            st.write("23C11054 - Nguyễn Khắc Toàn")
            st.write("23C15030 - Nguyễn Vũ Linh")
            st.write("23C15037 - Bùi Trọng Quý")

    st.header("Instructions")
    st.write("**Step 1**: Enter URLs for Chapter Pages and Character Reference Images.")
    st.write("**Step 2**: Enter Character Names (comma separated).")
    st.write("**Step 3**: Check the Colorization checkbox if needed.")
    st.write("**Step 4**: Click 'Generate Video' to generate the video.")
    st.write("**Step 5**: Click 'Clear' to clear all input fields.")

    st.title("Feedback")
    sentiment_mapping = ["one", "two", "three", "four", "five"]
    selected = st.feedback("stars")
    if selected is not None:
        st.info(f"You gave **{selected + 1}** stars. Thank you for the feedback!")

st.header("Chapter Pages in Chronological Order")
chapter_urls = st.text_area("Enter URLs for Chapter Pages (one URL per line)", height=150)
if not chapter_urls:
    st.warning("⚠️ This field is required: Please enter URLs for Chapter Pages.")
chapter_url_list = chapter_urls.splitlines()
invalid_chapter_urls = validate_urls(chapter_url_list)

st.header("Character Reference Images")
character_urls = st.text_area("Enter URLs for Character Reference Images (one URL per line)", height=150)
if not character_urls:
    st.warning("⚠️ This field is required: Please enter URLs for Character Reference Images.")
character_url_list = character_urls.splitlines()
invalid_character_urls = validate_urls(character_url_list)

if invalid_chapter_urls:
    st.error("❌ Invalid URLs in 'Chapter Pages in Chronological Order':")
    for url in invalid_chapter_urls:
        st.write(f"- {url}")

if invalid_character_urls:
    st.error("❌ Invalid URLs in 'Character Reference Images':")
    for url in invalid_character_urls:
        st.write(f"- {url}")

st.header("Character Names")
character_names = st.text_input("Enter Character Names (comma separated)", placeholder="Luffy,Hank,Nami")

colorize = st.checkbox("Colorization")

if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "progress_complete" not in st.session_state:
    st.session_state.progress_complete = False

left, right = st.columns(2)

if left.button("Generate Video", icon="🔥", use_container_width=True):
    if chapter_urls and character_urls and not invalid_chapter_urls and not invalid_character_urls:
        st.session_state.video_url = ""
        st.session_state.progress_complete = False

        progress_text = "Generating video in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)

        my_bar.empty()
        time.sleep(1)

        st.session_state.video_url = "https://files.vuxlinh.com/demo.mp4"
        st.session_state.progress_complete = True
    else:
        st.error("Please fill in all required fields before generating the video.")

if right.button("Clear", icon="💣", use_container_width=True):
    st.session_state.video_url = ""
    st.session_state.progress_complete = False
    st.query_params.update({})

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

# DEBUGGING
# if chapter_urls:
#     st.write("### Chapter URLs")
#     st.write(chapter_urls.splitlines())

# if character_urls:
#     st.write("### Character Reference URLs")
#     st.write(character_urls.splitlines())
