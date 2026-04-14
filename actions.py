import subprocess

# =========================
# 🖐 DESKTOP SWITCH
# =========================
def swipe_right():
    subprocess.run([
        "osascript",
        "-e",
        'tell application "System Events" to key code 124 using control down'
    ])

def swipe_left():
    subprocess.run([
        "osascript",
        "-e",
        'tell application "System Events" to key code 123 using control down'
    ])

# =========================
# 📜 SCROLL
# =========================
def scroll_up():
    subprocess.Popen([
        "osascript",
        "-e",
        'tell application "System Events" to key code 126'
    ])

def scroll_down():
    subprocess.Popen([
        "osascript",
        "-e",
        'tell application "System Events" to key code 125'
    ])

# =========================
# 🔊 FEEDBACK
# =========================
def feedback():
    subprocess.Popen([
        "afplay",
        "/System/Library/Sounds/Tink.aiff"
    ])