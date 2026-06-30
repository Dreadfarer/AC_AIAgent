# AC_AIAgent/voice.py
"""
Robust voice helpers: STT via SpeechRecognition, TTS via pyttsx3 with gTTS fallback.
- Local TTS (pyttsx3) is attempted first (requires eSpeak/espeak-ng on Linux).
- If pyttsx3/init or speaking fails, fallback to gTTS -> mp3 -> mpg123 (or ffplay).
"""
import tempfile
import subprocess

# STT
try:
    import speech_recognition as sr
except Exception:
    sr = None

_recognizer = sr.Recognizer() if sr else None

def listen(timeout=5, phrase_time_limit=10):
    if not _recognizer:
        raise RuntimeError("SpeechRecognition not available. Install: pip install SpeechRecognition")
    # Check for available microphones so we can fail fast with a clear message
    try:
        mic_names = sr.Microphone.list_microphone_names()
    except Exception:
        mic_names = []
    if not mic_names:
        raise RuntimeError(
            "No input devices found. Microphone not available. Attach or configure an input device, or run without --voice."
        )
    try:
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception as e:
        raise RuntimeError(f"Microphone/STT error: {e}")
    try:
        return _recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as err:
        raise RuntimeError(f"STT request failed: {err}")

# TTS
try:
    import pyttsx3
except Exception:
    pyttsx3 = None

_engine = None
if pyttsx3:
    try:
        _engine = pyttsx3.init()
    except Exception as e:
        # Keep going; we will fallback to gTTS
        print("pyttsx3 init failed:", e)
        _engine = None

def _play_file(path):
    # Try mpg123, otherwise ffplay (ffmpeg), otherwise fallback to system open
    for cmd in (["mpg123", path], ["ffplay", "-nodisp", "-autoexit", path]):
        try:
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except FileNotFoundError:
            continue
    # Last resort: try system's default player (may block)
    try:
        subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass

def speak(text):
    if not text:
        return

    # Try local engine first
    if _engine:
        try:
            _engine.say(text)
            _engine.runAndWait()
            return
        except Exception as e:
            print("pyttsx3 speaking failed:", e)
            print("Falling back to gTTS...")

    # Fallback to gTTS (online)
    try:
        from gtts import gTTS
    except Exception:
        print(
            "gTTS is not installed. Install it in a virtualenv: \n" 
            "python3 -m venv .venv && source .venv/bin/activate && pip install gTTS"
        )
        return

    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.write_to_fp(f)
            fname = f.name
    except Exception as e:
        print("gTTS generation failed:", e)
        return

    try:
        _play_file(fname)
    except Exception as e:
        print("Failed to play TTS audio. Ensure mpg123, ffmpeg, or a desktop player is installed:", e)
