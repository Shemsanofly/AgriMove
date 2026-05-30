from google import genai
import os
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents="""
    Wewe ni msaidizi wa AgriMove Tanzania.
    Jibu kwa Kiswahili tu kwa sentensi fupi.
    Swali: Bei ya mahindi leo ni ngapi?
    """
)

reply = response.text
print("Gemini Reply:", reply)

#  Convert to Swahili audio
tts = gTTS(text=reply, lang='sw', slow=False)
tts.save("test_gemini.mp3")
print("Done! Open test_gemini.mp3 to hear Swahili!")