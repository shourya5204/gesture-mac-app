import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

latest_command = None

def listen_loop():
    global latest_command

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")

                # 🔥 VERY IMPORTANT (noise adjustment)
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=3
                )

            command = recognizer.recognize_google(audio)
            latest_command = command.lower()
            print("Heard:", latest_command)

        except sr.WaitTimeoutError:
            print("No speech detected")

        except sr.UnknownValueError:
            print("Could not understand")

        except sr.RequestError:
            print("API error")

        except Exception as e:
            print("Error:", e)


def start_listening():
    thread = threading.Thread(target=listen_loop, daemon=True)
    thread.start()


def get_command():
    global latest_command
    cmd = latest_command
    latest_command = None
    return cmd