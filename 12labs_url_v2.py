import streamlit as st
from twelvelabs import TwelveLabs
from pytube import YouTube
import time
import os


# Hard-coded API key
API_KEY = "tlk_1KNS9E41MY0HZ42VBM9PZ25M5CX9"  
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


# Function to create an index if it doesn't exist
def create_index(client):
    if st.session_state['index_id'] is None:
        try:
            index = client.index.create(
                name="new_v3",
                engines=[
                    {
                        "name": "pegasus1",
                        "options": ["visual", "conversation"],
                    }
                ]
            )
            st.session_state['index_id'] = index.id
            st.success(f"Created index: id={index.id} name={index.name} engines={index.engines}")
        except Exception as e:
            st.error(f"Failed to create index: {e}")

# Function to download YouTube video
def download_youtube_video(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_path = video.download(output_path='/tmp', filename='downloaded_video.mp4')
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
    # if is_url == True:
    #     st.success(f"Uploaded video from URL. The unique identifier of your video is {task.video_id}")
    # else:
    #     st.success(f"Uploaded {video_source.name}. The unique identifier of your video is {task.video_id}")
    # return task.video_id
    st.success(f"Uploaded {video_source if is_url else video_source}. The unique identifier of your video is {task.video_id}")
    return task.video_id

# Function to generate text for video
def generate_text_for_video(client, video_id, selected_prompt):
    content = ""

    if selected_prompt == "Provide a detailed summary of the video.":
        res = client.generate.summarize(video_id=video_id, type="summary")
        content = f"**Summary**: {res.summary}"

    elif selected_prompt == "Generate keywords for SEO.":
        res = client.generate.text(video_id=video_id, prompt="Generate five keywords for SEO from the content of the video.")
        if hasattr(res, 'data'):
            content = f"**SEO Keywords**: {res.data}"
        else:
            content = "**SEO Keywords**: Unable to generate keywords."

    elif selected_prompt == "Create an engaging social media post based on the video.":
        res = client.generate.text(video_id=video_id, prompt="Create an engaging social media post based on the content of the video uploaded.")
        if hasattr(res, 'data'):
            content = f"**Social Media Post**: {res.data}"
        else:
            content = "**Social Media Post**: Unable to generate post."

    elif selected_prompt == "Suggest educational insights and questions from the video content.":
        res = client.generate.text(video_id=video_id, prompt="Suggest educational insights and questions that are relevant to the content of the video uploaded.")
        if hasattr(res, 'data'):
            content = f"**Educational Insights and Questions**: {res.data}"
        else:
            content = "**Educational Insights and Questions**: Unable to generate insights and questions."

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
    "Generate keywords for SEO.",
    "Create an engaging social media post based on the video.",
    "Suggest educational insights and questions from the video content."
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

