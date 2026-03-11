import streamlit as st
import asyncio
import io
import random
from rembg import remove
from PIL import Image
import segno
from reportlab.pdfgen import canvas
from deep_translator import GoogleTranslator
import edge_tts
import yt_dlp
from groq import Groq

# កំណត់ទំព័រ និង Theme
st.set_page_config(page_title="Smart AI Tools", page_icon="🛠️", layout="wide")

# --- ផ្នែក Sidebar សម្រាប់ជ្រើសរើស Tools ---
with st.sidebar:
    st.title("🛠️ All-in-One Tools")
    tool = st.radio("ជ្រើសរើសឧបករណ៍:", [
        "1. AI ធ្វើឱ្យរូបច្បាស់", "2. Text to Speech", "3. Video Downloader",
        "4. លុប Background", "5. Image to PDF", "6. QR Code Maker",
        "7. Spin ចៃដន្យ", "8. បកប្រែ (Translate)", "9. Image to Prompt", "10. AI Assistant"
    ])
    st.divider()
    api_key = st.text_input("Groq API Key:", type="password", help="យកពី console.groq.com")

# --- Function ជំនួយសម្រាប់ TTS ---
async def generate_voice(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    out = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            out.write(chunk["data"])
    return out.getvalue()

# --- តួសាច់រឿងនៃ Tools នីមួយៗ ---

if tool == "1. AI ធ្វើឱ្យរូបច្បាស់":
    st.header("✨ AI Image Upscaler (Basic)")
    img_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
    if img_file:
        img = Image.open(img_file)
        # ប្រើ Lanczos Filter ដើម្បីបង្កើនកម្រិតភាពច្បាស់ដោយមិនប្រើ API ថ្លៃ
        res = img.resize((img.width*2, img.height*2), Image.LANCZOS)
        st.image(res, caption="រូបភាពរីកធំ និងកែសម្រួលកម្រិតភាពច្បាស់")

elif tool == "2. Text to Speech":
    st.header("🗣️ Natural AI Voice (Edge TTS)")
    txt = st.text_area("បញ្ចូលអត្ថបទ:", "សួស្ដី! តើអ្នកសុខសប្បាយជាទេ?")
    v_choice = st.selectbox("ជ្រើសរើសសំឡេង:", ["km-KH-SreymomNeural", "km-KH-PisethNeural", "en-US-AvaNeural"])
    if st.button("បង្កើតសំឡេង"):
        audio_data = asyncio.run(generate_voice(txt, v_choice))
        st.audio(audio_data)

elif tool == "3. Video Downloader":
    st.header("📹 Social Video Downloader")
    url = st.text_input("បញ្ចូល Link វីដេអូ (YouTube/TikTok/FB):")
    if st.button("Download"):
        st.info("កំពុងទាញយក... (មុខងារនេះត្រូវការទំហំ Disk បណ្ដោះអាសន្នលើ Render)")
        # ចំណាំ៖ yt-dlp លើ Render Free Tier អាចមានកម្រិតល្បឿន

elif tool == "4. លុប Background":
    st.header("🖼️ Remove Background")
    bg_file = st.file_uploader("Upload Image", type=['png', 'jpg'])
    if bg_file:
        input_img = Image.open(bg_file)
        with st.spinner("កំពុងលុប..."):
            output_img = remove(input_img)
            st.image(output_img)

elif tool == "5. Image to PDF":
    st.header("📄 Image to PDF Converter")
    files = st.file_uploader("Upload Images", accept_multiple_files=True)
    if files and st.button("Convert to PDF"):
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        for f in files:
            img = Image.open(f)
            c.setPageSize((img.width, img.height))
            c.drawImage(f, 0, 0)
            c.showPage()
        c.save()
        st.download_button("Download PDF", buf.getvalue(), "converted.pdf")

elif tool == "6. QR Code Maker":
    st.header("🏁 QR Code Generator")
    link = st.text_input("បញ្ចូល Link ឬ អត្ថបទ:")
    if link:
        qr = segno.make_qr(link)
        buf = io.BytesIO()
        qr.save(buf, kind='png', scale=10)
        st.image(buf.getvalue())

elif tool == "7. Spin ចៃដន្យ":
    st.header("🎡 Lucky Spin")
    items = st.text_area("បញ្ចូលឈ្មោះ (ប្រើក្បៀស , ដើម្បីបំបែក):", "មិត្តភក្តិ១, មិត្តភក្តិ២, មិត្តភក្តិ៣")
    if st.button("Spin Now!"):
        choice = random.choice([i.strip() for i in items.split(",")])
        st.balloons()
        st.success(f"អ្នកដែលសំណាងគឺ៖ {choice}")

elif tool == "8. បកប្រែ (Translate)":
    st.header("🌐 Global Translator")
    t_input = st.text_area("អត្ថបទដើម:")
    target_lang = st.selectbox("បកប្រែទៅជា:", ["khmer", "english", "chinese (simplified)", "french"])
    if st.button("Translate"):
        res = GoogleTranslator(source='auto', target=target_lang).translate(t_input)
        st.write(f"**លទ្ធផល:** {res}")

elif tool == "9. Image to Prompt":
    st.header("🖼️ AI Image to Prompt (Vision)")
    if not api_key: st.warning("សូមបញ្ចូល Groq API Key ក្នុង Sidebar")
    img_v = st.file_uploader("Upload រូបភាពឱ្យ AI មើល:", type=['jpg', 'png'])
    if img_v and api_key:
        st.info("មុខងារនេះត្រូវការផ្ញើរូបភាពទៅកាន់ Groq Vision Cloud")
        # កូដ Vision ត្រូវបំប្លែងរូបជា Base64 (សម្រាំងដើម្បីសន្សំ RAM)

elif tool == "10. AI Assistant":
    st.header("🤖 Smart AI Assistant")
    if api_key:
        client = Groq(api_key=api_key)
        user_msg = st.chat_input("សួរអ្វីមួយទៅកាន់ AI...")
        if user_msg:
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are a helpful assistant. Reply in Khmer if user speaks Khmer."},
                          {"role": "user", "content": user_msg}]
            )
            st.markdown(chat.choices[0].message.content)
    else:
        st.warning("សូមបញ្ចូល Groq API Key ដើម្បីប្រើប្រាស់មុខងារនេះ។")
