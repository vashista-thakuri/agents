import speech_recognition as sr

def get_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    print("Calibrating mic for background noise...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening... (Speak now)")
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing speech...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio. Please type your input.")
    except sr.RequestError:
        print("API unavailable or request failed. Please type your input.")
    
    return input("\nMe: ")

prompt = get_voice_input()