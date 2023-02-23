import openai
import speech_recognition as sr
import requests
import json
import streamlit as st
import keyboard
import pyaudio

openai.api_key = st.secrets["openai_api_key"]
xi_api_key = st.secrets["xi_api_key"]


def synthesize_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # replace with desired voice ID
    headers = {"xi-api-key": xi_api_key, "Content-Type": "application/json"}
    data = {"text": text}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    audio_content = response.content

    # use PyAudio to play audio content
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=22050, output=True)
    stream.write(audio_content)
    stream.close()
    p.terminate()


def prompt_to_listen(recognizer, prompt):
    st.write(prompt)

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        audio = recognizer.listen(source, timeout=10)
    try:
        user_question = recognizer.recognize_google(audio_data=audio)
        st.write(f"\n<< {user_question.capitalize()}")
    except sr.UnknownValueError:
        st.write("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        st.write("Could not request results from Google Speech Recognition service; {0}".format(e))

    if len(user_question) > 0:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_question,
            temperature=0,
            max_tokens=250,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )

        response_text = response.choices[0].text
        st.write(f"{response_text}")
        st.write(f"\nTotal Tokens Consumed: {response.usage.total_tokens}")
        synthesize_speech(response_text)

        action_prompt = f"\nPress Spacebar to ask follow up question? Press Enter to end."
        st.write(action_prompt)

        while True:
            if keyboard.read_key() == "space":
                prompt = f"\nGo ahead, I am listening..."
                prompt_to_listen(recognizer, prompt)
                break
            if keyboard.read_key() == "enter":
                break


def main():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200
    recognizer.dynamic_energy_threshold = True

    context_prompt = f"\nHow would you like AI to help you? Speak, I am listening..."

    # Recursive method to process user input with OpenAI API
    prompt_to_listen(recognizer, context_prompt)


if __name__ == "__main__":
    main()
