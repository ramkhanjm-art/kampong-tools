import streamlit as st
import asyncio
import io
import os
import random
from rembg import remove
from PIL import Image
import segno
from reportlab.pdfgen import canvas
from deep_translator import GoogleTranslator
import edge_tts
import yt_dlp
from groq import Groq

# កំណត់ Port សម្រាប់ Render (សំខាន់ខ្លាំង)
PORT = os.environ.get("PORT", 8501)

st.set_page_config(page_title="AI Tools", page_icon="🛠️")

# --- Sidebar ---
with st.sidebar:
    st.title("🛠️ Tools Box")
    tool = st.radio("រើសឧបករណ៍:", [
        "1. AI ធ្វើឱ្យរូបច្បាស់", "2. Text to Speech", "3. Video Downloader",
        "4. លុប Background", "5. Image to PDF", "6. QR Code Maker",
        "7. Spin ចៃដន្យ", "8. បកប្រែ", "9. Image to Prompt", "10. AI Assistant"
    ])
    api_key = st.text_input("Groq API Key:", type="password")

# --- Tool 3: Video Downloader (កូដពេញលេញ) ---
if tool == "3. Video Downloader":
    st.header("📹 Video Downloader")
    url = st.text_input("បញ្ចូល Link វីដេអូ:")
    
    if st.button("ទាញយក"):
        if url:
            try:
                with st.spinner("កំពុងទាញយក... សូមរង់ចាំ"):
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': 'video.mp4',
                        'noplaylist': True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    with open("video.mp4", "rb") as f:
                        st.download_button("ចុចទីនេះដើម្បី Save វីដេអូ", f, file_name="downloaded_video.mp4")
                    os.remove("video.mp4") # លុបចេញវិញដើម្បីកុំឱ្យពេញ RAM Render
            except Exception as e:
                st.error(f"មានបញ្ហា៖ {e}")
        else:
            st.warning("សូមបញ្ចូល Link!")

# --- Tool 4: លុប Background (កែសម្រួលឱ្យស្រាល) ---
elif tool == "4. លុប Background":
    st.header("🖼️ Remove Background")
    file = st.file_uploader("Upload រូបភាព", type=['jpg', 'png'])
    if file:
        img = Image.open(file)
        with st.spinner("កំពុងដំណើរការ..."):
            # កាត់បន្ថយទំហំរូបភាពបន្តិចមុនលុប ដើម្បីកុំឱ្យ Render គាំង RAM
            img.thumbnail((800, 800)) 
            res = remove(img)
            st.image(res)

# (ចំណែក Tools ផ្សេងទៀត ប្រើកូដដែលខ្ញុំផ្ដល់ឱ្យលើកមុនបញ្ចូលបន្តបាន)
