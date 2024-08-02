import streamlit as st
from twelvelabs import TwelveLabs
#from pytube import YouTube
import time
import os


# Hard-coded API key
API_KEY = "tlk_1K68Z2V2SQ6GWR2NA0J6211WSXEJ"  # Replace with your actual Twelve Labs API key
client = TwelveLabs(api_key = API_KEY)

# Initialize session state for generated content and index
if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = []
if 'index_id' not in st.session_state:
    st.session_state['index_id'] = None


# Injest css for background
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")


def create_index(client):
    if st.session_state['index_id'] is None:
        try:
            index = client.index.create(
                name = "test_index_12",
                engines=[
                    {
                        "name": "pegasus1.1",
                        "options": ["visual", "conversation"],
                    }
                ]
            )   
            st.session_state['index_id'] = index.id
            st.success(f"Created index: id={index.id} name={index.name} engines={index.engines}")
        except Exception as e:
            st.error(f"Failed to create index: {e}")

def download_youtube_video(url):
    try:
        video_path = 'downloaded_video.mp4'  # Adjusted for Windows environment
        ydl_opts = {'outtmpl': video_path}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return video_path
    except Exception as e:
        st.error(f"Failed to download YouTube video: {e}")
        return None

# Function to upload video to the existing index
def upload_video(client, video_source, is_url=False):
    try:
        task = client.task.create(index_id=st.session_state['index_id'], file=video_source, language="en")
        st.success(f"Created task: id={task.id}")
    except Exception as e:
        st.error(f"Failed to create task: {e}")
        return None

    progress_bar = st.progress(0)
    status_text = st.empty()

    while True:
        task_status = client.task.retrieve(task.id)
        status_text.text(f"Status: {task_status.status}")

        if task_status.status == "processing":
            progress_bar.progress(50)
        elif task_status.status == "ready":
            progress_bar.progress(100)
            break
        elif task_status.status == "failed":
            st.error(f"Indexing failed with status {task_status.status}")
            return None

        time.sleep(5)
    if is_url:
        st.success(f"Uploaded video from URL. The unique identifier of your video is {task.video_id}")
    else:
        st.success(f"Uploaded {video_source}. The unique identifier of your video is {task.video_id}")
    return task.video_id

# Function to generate text for video
def generate_text_for_video(client, video_id, selected_prompt):
    content = ""
    try:
        if selected_prompt == "Provide a detailed summary of the video.":
            res = client.generate.summarize(video_id=video_id, type="summary")
            content = f"**Summary**: {res.summary}"

        elif selected_prompt == "Generate important keywords.":
            res = client.generate.gist(video_id=video_id, types=["title", "topic", "hashtag"])
            content = f"**Title**: {res.title}\n\n**Topics**: {', '.join(res.topics)}\n\n**Hashtags**: {', '.join(res.hashtags)}"

        elif selected_prompt == "Create an engaging social media post based on the video.":
            res = client.generate.text(video_id=video_id, prompt="Based on this video, create an engaging social media post. Can you also give any relevant suggestions for the user?")
            content = f"**Social media post**: {res.data}"

        elif selected_prompt == "Suggest educational insights from the video content.":
            res = client.generate.summarize(video_id=video_id, type="highlight")
            for highlight in res.highlights:
                content = f"  **Highlight**: {highlight.highlight}\n    Start: {highlight.start}, End: {highlight.end}"

    except Exception as e:
        content = f"Error generating content: {e}"

    st.session_state['generated_content'].append(content)

# Streamlit app interface
st.title('Video-to-Text Application')

upload_option = st.radio("Choose a video source:", ("Upload a video file", "Provide a YouTube URL"))

if upload_option == "Upload a video file":
    uploaded_files = st.file_uploader("Choose video files", type=["mp4", "avi", "mov"], accept_multiple_files=True)
else:
    youtube_url = st.text_input("Enter YouTube URL")

predefined_prompts = [
    "Provide a detailed summary of the video.",
    "Generate important keywords.",
    "Create an engaging social media post based on the video.",
    "Suggest educational insights from the video content."
]

selected_prompt = st.selectbox("Select a prompt for text generation:", predefined_prompts)

def process_videos(uploaded_files, youtube_url, upload_option, selected_prompt):
    create_index(client)  # Ensure the index is created
    if upload_option == "Upload a video file":
        for uploaded_file in uploaded_files:
            st.video(uploaded_file)
            video_id = upload_video(client, uploaded_file)
            if video_id:
                generate_text_for_video(client, video_id, selected_prompt)
    elif upload_option == "Provide a YouTube URL" and youtube_url:
        video_path = download_youtube_video(youtube_url)
        if video_path:
            video_id = upload_video(client, video_path)
            if video_id:
                generate_text_for_video(client, video_id, selected_prompt)
            os.remove(video_path)  # Clean up downloaded video file

if st.button("Process Videos"):
    if upload_option == "Upload a video file" and uploaded_files:
        process_videos(uploaded_files, None, upload_option, selected_prompt)
    elif upload_option == "Provide a YouTube URL" and youtube_url:
        youtube_url = youtube_url.strip()  # Remove leading/trailing whitespace
        process_videos(None, youtube_url, upload_option, selected_prompt)

# Display generated content
if st.session_state['generated_content']:
    st.write("### About the Video")
    for content in st.session_state['generated_content']:
        st.write(content)

# User feedback section
st.header("Feedback")
rating = st.radio("How would you rate the generated content?", ("Excellent", "Good", "Average", "Poor"))
feedback = st.text_area("Any additional comments or suggestions?")

if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")
