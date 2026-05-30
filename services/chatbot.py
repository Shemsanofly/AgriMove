import google.generativeai as genai
import os
import uuid
from gtts import gTTS
from dotenv import load_dotenv
load_dotenv()

os.makedirs("static/audio", exist_ok=True)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

SYSTEM_PROMPT = """
Wewe ni Amina, msaidizi wa AgriMove Tanzania.
Unasaidia wakulima wa Tanzania kwa Kiswahili.

Unajua:
- Bei za mazao: mahindi, mpunga, nyanya,
  vitunguu, muhogo, kahawa, korosho
- Masoko: Kariakoo, Arusha, Mbeya, 
  Mwanza, Dodoma
- Usafiri wa pamoja kwa wakulima
- Hifadhi na maghala ya karibu
- Malipo ya M-Pesa na Tigo Pesa

Kanuni:
- Jibu KWA KISWAHILI TU
- Tumia maneno rahisi
- Sentensi fupi fupi tu
- Bei kwa shilingi za Tanzania TSh
- Kuwa mkarimu na wa kupendeza
"""

def get_ai_response(user_message):
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Samahani, kuna hitilafu. Jaribu tena."

def text_to_swahili_audio(text):
    try:
        filename = f"reply_{uuid.uuid4().hex[:8]}.mp3"
        filepath = f"static/audio/{filename}"
        tts = gTTS(text=text, lang='sw', slow=False)
        tts.save(filepath)
        return f"/static/audio/{filename}"
    except Exception as e:
        print(f"Audio error: {e}")
        return None
