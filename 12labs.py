import streamlit as st
import os
from glob import glob
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task
import requests


# Function to create index and upload video
def create_index_and_upload_video(client, video_file, index_name):
    index = client.index.create(
        name=index_name,
        engines=[
            {
                "name": "pegasus1",
                "options": ["visual", "conversation"],
            }
        ]
    )
    st.success(f"Created index: id={index.id} name={index.name} engines={index.engines}")

    st.info(f"Uploading {video_file.name}")
    task = client.task.create(index_id=index.id, file=video_file, language="en")
    st.success(f"Created task: id={task.id}")

    # Monitor the video indexing process
    def on_task_update(task: Task):
        st.info(f"  Status={task.status}")

    task.wait_for_done(sleep_interval=50, callback=on_task_update)
    if task.status != "ready":
        st.error(f"Indexing failed with status {task.status}")
        return None

    st.success(f"Uploaded {video_file.name}. The unique identifier of your video is {task.video_id}")
    return index.id

# Function to generate text for video
def generate_text_for_video(client, index_id):
    videos = client.index.video.list(index_id)
    for video in videos:
        st.info(f"Generating text for {video.id}")

        res = client.generate.gist(video_id=video.id, types=["title", "topic", "hashtag"])
        st.write(f"**Title**: {res.title}\n**Topics**={res.topics}\n**Hashtags**={res.hashtags}")

        res = client.generate.summarize(video_id=video.id, type="summary")
        st.write(f"**Summary**: {res.summary}")

        st.write("**Chapters**:")
        res = client.generate.summarize(video_id=video.id, type="chapter")
        for chapter in res.chapters:
            st.write(
                f"  **Chapter {chapter.chapter_number}**: {chapter.chapter_title}\n    Summary: {chapter.chapter_summary}\n    Start: {chapter.start}, End: {chapter.end}"
            )

        st.write("**Highlights**:")
        res = client.generate.summarize(video_id=video.id, type="highlight")
        for highlight in res.highlights:
            st.write(
                f"  Highlight: {highlight.highlight}\n    Start: {highlight.start}, End: {highlight.end}"
            )

        res = client.generate.text(video_id=video.id, prompt="Based on this video, I want to generate five keywords for SEO (Search Engine Optimization).")
        st.write(f"**Open-ended Text**: {res.data}")

# Streamlit app
st.title('Video-to-Text Application')

# Input fields for API key and index name
api_key = st.text_input("Enter your Twelve Labs API key", type="password")
index_name = st.text_input("Enter the Index Name")

uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("Upload and Process Video"):
        if api_key and index_name:
            client = TwelveLabs(api_key=api_key)

            # Upload and process the video directly
            index_id = create_index_and_upload_video(client, uploaded_file, index_name)
            if index_id:
                generate_text_for_video(client, index_id)
        else:
            st.warning("Please provide both the API key and index name")





# uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

# if uploaded_file is not None:
#     st.video(uploaded_file)

# def process_video(api_key, video_file):
#     url = "https://api.twelvelabs.io/v1.2/generate"
#     headers = {"Authorization": f"Bearer {api_key}"}
#     files = {"file": video_file}

#     response = requests.post(url, headers=headers, files=files)
#     return response.json()

# if uploaded_file is not None:
#     api_key = "tlk_1KNS9E41MY0HZ42VBM9PZ25M5CX9"  # Replace with your actual Twelve Labs API key
#     with st.spinner('Processing video...'):
#         result = process_video(api_key, uploaded_file)
#         st.write(result)

# if uploaded_file is not None:
#     api_key = "YOUR_API_KEY"
#     with st.spinner('Processing video...'):
#         result = process_video(api_key, uploaded_file)
#         st.write("**Generated Text**")
#         st.write(result.get("text", "No text generated"))

# def process_video(api_key, video_file):
#     try:
#         url = "https://api.twelvelabs.io/v1.2/generate"
#         headers = {"Authorization": f"Bearer {api_key}"}
#         files = {"file": video_file}

#         response = requests.post(url, headers=headers, files=files)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         st.error(f"An error occurred: {e}")
#         return None

# if uploaded_file is not None:
#     api_key = "YOUR_API_KEY"
#     with st.spinner('Processing video...'):
#         result = process_video(api_key, uploaded_file)
#         if result:
#             st.write("**Generated Text**")
#             st.write(result.get("text", "No text generated"))
