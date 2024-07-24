# Video_to_Text

This repository contains a Streamlit-based application that transforms video content into text using the Twelve Labs API. The app allows users to upload video files or provide YouTube URLs. It generates various forms of text based on the video content, such as summaries, keywords, social media posts, and educational insights.

## Features
Upload Video Files or YouTube URLs: Users can either upload local video files or enter a YouTube URL for processing.

Text Generation: The application offers multiple text generation options including summaries, keywords, social media posts, and educational insights.

Real-Time Processing: Users can see the status of video processing and text generation in real-time.

Feedback Collection: Users can provide feedback on the generated content, which can be stored for further analysis.

## Getting Started
### Prerequisites
Python 3.7+

Streamlit

Twelve Labs API key and index name

yt-dlp Python package

### How to Run the File
streamlit run 12labs_url_v2.py on Anaconda command prompt. 

### Usage
Choose Video Source: Select either "Upload a video file" or "Provide a YouTube URL".

Upload or Enter URL: Upload video files or enter a YouTube URL.

Select Prompt: Choose a prompt for text generation from the provided options.

Process Videos: Click the "Process Videos" button to start processing.

View Generated Content: The generated text will be displayed under "About the Video".

Provide Feedback: Rate the generated content and provide additional comments if any.

### Design Choices
Streamlit: Chosen for its simplicity and ease of creating interactive web applications.

Twelve Labs API: Used for powerful video-to-text transformations.

yt-dlp: Utilized for downloading YouTube videos.

Session State: Manages the state of generated content and video index to ensure consistent behavior.

#### Files in the Repo:
1. 12labs_url_v2.py: The main Python code where you add the API key and index name
2. style.css: The CSS with interface design details. The .py file and CSS should be in the same folder.

#### Acknowledgments
Twelve Labs for providing the API.

Streamlit for the interactive web framework.

yt-dlp for YouTube video handling.
