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
import base64

# កំណត់ការបង្ហាញទំព័រ
st.set_page_config(page_title="Smart AI Tools", page_icon="🛠️", layout="centered")

# --- Sidebar ---
with st.sidebar:
    st.title("🛠️ All-in-One Tools")
    tool = st.radio("ជ្រើសរើសឧបករណ៍:", [
        "1. AI ធ្វើឱ្យរូបច្បាស់", "2. Text to Speech", "3. Video Downloader",
        "4. លុប Background", "5. Image to PDF", "6. QR Code Maker",
        "7. Spin ចៃដន្យ", "8. បកប្រែ", "9. Image to Prompt", "10. AI Assistant"
    ])
    st.divider()
    api_key = st.text_input("Groq API Key:", type="password", help="យកពី console.groq.com")

# --- Functions ជំនួយ ---
async def generate_voice(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    out = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            out.write(chunk["data"])
    return out.getvalue()

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- ដំណើរការ Tools នីមួយៗ ---

if tool == "1. AI ធ្វើឱ្យរូបច្បាស់":
    st.header("✨ AI Image Upscaler")
    file = st.file_uploader("Upload Image", type=['jpg', 'png'])
    if file:
        img = Image.open(file)
        res = img.resize((img.width*2, img.height*2), Image.LANCZOS)
        st.image(res, caption="រូបភាពច្បាស់ជាងមុន ២ដង")

elif tool == "2. Text to Speech":
    st.header("🗣️ Natural AI Voice")
    txt = st.text_area("បញ្ចូលអត្ថបទ:", "សួស្ដី! ស្វាគមន៍មកកាន់វែបសាយរបស់យើង។")
    voice = st.selectbox("ជ្រើសរើសសំឡេង:", ["km-KH-SreymomNeural", "km-KH-PisethNeural", "en-US-AvaNeural"])
    if st.button("បំប្លែងជាសំឡេង"):
        with st.spinner("កំពុងបង្កើត..."):
            audio_data = asyncio.run(generate_voice(txt, voice))
            st.audio(audio_data)

elif tool == "3. Video Downloader":
    st.header("📹 Video Downloader")
    v_url = st.text_input("បញ្ចូល Link វីដេអូ (YT/TikTok):")
    if st.button("ទាញយក"):
        try:
            with st.spinner("កំពុងទាញយក..."):
                ydl_opts = {'format': 'best', 'outtmpl': 'v.mp4'}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([v_url])
                with open("v.mp4", "rb") as f:
                    st.download_button("Download Now", f, file_name="video.mp4")
                os.remove("v.mp4")
        except Exception as e:
            st.error(f"Error: {e}")

elif tool == "4. លុប Background":
    st.header("🖼️ Remove Background")
    file = st.file_uploader("ជ្រើសរើសរូបភាព", type=['jpg', 'png'])
    if file:
        img = Image.open(file)
        with st.spinner("កំពុងលុប..."):
            res = remove(img)
            st.image(res)

elif tool == "5. Image to PDF":
    st.header("📄 Image to PDF")
    files = st.file_uploader("Upload Images", accept_multiple_files=True)
    if files and st.button("បង្កើត PDF"):
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        for f in files:
            img = Image.open(f)
            c.setPageSize((img.width, img.height))
            c.drawImage(f, 0, 0)
            c.showPage()
        c.save()
        st.download_button("Download PDF", buf.getvalue(), "file.pdf")

elif tool == "6. QR Code Maker":
    st.header("🏁 QR Code Maker")
    data = st.text_input("Link/Text:")
    if data:
        qr = segno.make_qr(data)
        buf = io.BytesIO()
        qr.save(buf, kind='png', scale=10)
        st.image(buf.getvalue())

elif tool == "7. Spin ចៃដន្យ":
    st.header("🎡 Lucky Spin")
    items = st.text_input("ឈ្មោះ (បំបែកដោយក្បៀស):", "A, B, C")
    if st.button("Spin"):
        res = random.choice(items.split(","))
        st.success(f"លទ្ធផល៖ {res}")

elif tool == "8. បកប្រែ":
    st.header("🌐 Translator")
    t_in = st.text_area("អត្ថបទដើម:")
    lang = st.selectbox("ទៅជា:", ["khmer", "english", "chinese (simplified)"])
    if st.button("បកប្រែ"):
        res = GoogleTranslator(source='auto', target=lang).translate(t_in)
        st.write(res)

elif tool == "9. Image to Prompt":
    st.header("🖼️ Image to Prompt (Groq Vision)")
    img_v = st.file_uploader("Upload Image", type=['jpg', 'png'])
    if img_v and api_key:
        client = Groq(api_key=api_key)
        base64_image = encode_image(img_v)
        chat = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{"role": "user", "content": [{"type": "text", "text": "Describe this image for a prompt:"}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
        )
        st.write(chat.choices[0].message.content)

elif tool == "10. AI Assistant":
    st.header("🤖 AI Assistant")
    if api_key:
        client = Groq(api_key=api_key)
        q = st.chat_input("សួរអ្វីមួយ...")
        if q:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": q}])
            st.markdown(res.choices[0].message.content)
    else:
        st.warning("បញ្ចូល API Key សិន")
