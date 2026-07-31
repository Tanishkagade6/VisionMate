"""
VisionMate — Streamlit port
Voice-only control. No buttons drive the three features:
  "navigate" / "start navigation"  -> live obstacle navigation
  "stop navigation"                -> stops navigation
  "read document"                  -> captures + reads a document aloud
  "stop reading"                   -> stops mid-sentence
  "emergency" / "help"             -> sends the SOS webhook
  "stop" (generic)                 -> stops whichever task is active
  "exit" / "quit"                  -> ends the session
"""

import threading
import time

import cv2
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

import config
from config import YOLO_MODEL
from core.speaker_manager import speaker
from core.safety_engine import SafetyEngine
from core.warning_manager import WarningManager
from vision.detector import VisionDetector
from vision.object_filter import ObjectFilter
from vision.ui import VisionUI
from voice.listener import VoiceListener
from ocr.document_reader import DocumentReader
from modules.emergency import Emergency


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="VisionMate", layout="centered")

try:
    with open("theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    """
    <style>
    .status-badge{
        padding:16px 24px;
        border-radius:18px;
        font-size:22px;
        font-weight:700;
        text-align:center;
        color:white;
        box-shadow:0px 6px 16px rgba(0,0,0,.12);
        margin-bottom:16px;
    }
    .camera-frame{
        background:white;
        border-radius:22px;
        padding:14px;
        box-shadow:0px 8px 20px rgba(0,0,0,.10);
        margin-bottom:16px;
        text-align:center;
    }
    .heard-caption{
        color:#666;
        font-size:16px;
        font-style:italic;
        margin-bottom:10px;
    }
    .result-card{
        background:white;
        border-radius:18px;
        padding:20px;
        font-size:18px;
        box-shadow:0px 4px 12px rgba(0,0,0,.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-box">
        <h1>🦯 VisionMate</h1>
        <p>Say "navigate", "read document", or "emergency" — no buttons needed.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Phone IP — changes with WiFi, so set it here instead of editing config.py
# ---------------------------------------------------------------------------
default_ip = config.VIDEO_URL.split("//")[1].split(":")[0]

with st.sidebar:
    st.markdown("### ⚙️ Setup")
    phone_ip = st.text_input("Phone's current IP (from IP Webcam app)", value=default_ip)
    if st.button("Apply IP"):
        config.VIDEO_URL = f"http://{phone_ip}:8081/video"
        config.EMERGENCY_URL = f"http://{phone_ip}:8080/emergency"
        st.success(f"Using {phone_ip}")
    st.caption(f"Video: {config.VIDEO_URL}")
    st.caption(f"Emergency: {config.EMERGENCY_URL}")

status_placeholder = st.empty()
heard_placeholder = st.empty()
image_placeholder = st.empty()
text_placeholder = st.empty()


STATUS_COLORS = {
    "listening": "#4CAF50",
    "navigation": "#2196F3",
    "reading": "#FF9800",
    "emergency": "#E53935",
    "ended": "#757575",
}
STATUS_ICONS = {
    "listening": "🎤",
    "navigation": "🧭",
    "reading": "📄",
    "emergency": "🚨",
    "ended": "⏹️",
}


def set_status(mode: str, message: str):
    color = STATUS_COLORS.get(mode, "#757575")
    icon = STATUS_ICONS.get(mode, "•")
    status_placeholder.markdown(
        f'<div class="status-badge" style="background:{color};">{icon} {message}</div>',
        unsafe_allow_html=True,
    )


def show_frame(frame_bgr):
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    image_placeholder.markdown('<div class="camera-frame">', unsafe_allow_html=True)
    image_placeholder.image(rgb, channels="RGB", use_container_width=True)


IDLE_MESSAGE = 'Listening... say "navigate", "read document", or "emergency"'


# ---------------------------------------------------------------------------
# Heavy resources — loaded once, shared across the session
# ---------------------------------------------------------------------------
@st.cache_resource
def load_detector():
    return VisionDetector(model_name=YOLO_MODEL)


@st.cache_resource
def load_document_reader():
    return DocumentReader()


@st.cache_resource
def load_listener():
    return VoiceListener()


@st.cache_resource
def load_emergency():
    return Emergency()


detector = load_detector()
doc_reader = load_document_reader()
listener = load_listener()
emergency_module = load_emergency()

if "nav_thread" not in st.session_state:
    st.session_state.nav_thread = None
    st.session_state.nav_stop_event = None

if "read_thread" not in st.session_state:
    st.session_state.read_thread = None
    st.session_state.read_stop_event = None


# ---------------------------------------------------------------------------
# Navigation background worker
# ---------------------------------------------------------------------------
class NavigationWorker(threading.Thread):
    """
    Reuses detector.process_frame() (unchanged detection/decision logic)
    in a loop, drawing frames into the Streamlit image placeholder
    instead of a native OpenCV window.
    """

    def __init__(self, detector, stop_event):
        super().__init__(daemon=True)
        self.detector = detector
        self.stop_event = stop_event
        self.object_filter = ObjectFilter()
        self.safety_engine = SafetyEngine()
        self.warning_manager = WarningManager()
        self.ui = VisionUI()

    def run(self):
        cap = cv2.VideoCapture(config.VIDEO_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        if not cap.isOpened():
            speaker.speak_async("Could not open the navigation camera.")
            set_status("ended", "Could not open the navigation camera.")
            return

        self.detector.reset()
        speaker.speak_async("Navigation started.")

        while not self.stop_event.is_set():

            for _ in range(2):
                cap.grab()

            success, frame = cap.read()
            if not success:
                continue

            detected_objects, decision, scene_description, annotated = self.detector.process_frame(frame)

            categorized = self.object_filter.filter_objects(detected_objects)
            warnings = self.safety_engine.analyze(categorized)
            warning = self.warning_manager.get_warning(warnings)

            if warning:
                annotated = self.ui.draw_warning_panel(annotated, warning)
                annotated = self.ui.draw_object_labels(annotated, detected_objects)

            display_frame = cv2.resize(annotated, (640, 480))

            try:
                show_frame(display_frame)
            except Exception:
                pass  # UI context can drop mid-rerun; safe to skip a frame

        cap.release()
        speaker.speak_async("Navigation stopped.")
        set_status("listening", IDLE_MESSAGE)


class ReadDocumentWorker(threading.Thread):
    """
    Runs capture_and_read() in the background so the main voice loop
    stays free to hear "stop" while a document is captured/read aloud.
    Streams the autofocus warm-up frames live via on_frame, so you see
    the camera feed before the shot is even taken — same as navigation.
    """

    def __init__(self, doc_reader, stop_event):
        super().__init__(daemon=True)
        self.doc_reader = doc_reader
        self.stop_event = stop_event

    def _on_frame(self, frame):
        try:
            show_frame(frame)
        except Exception:
            pass

    def run(self):
        frame, texts = self.doc_reader.capture_and_read(
            stop_event=self.stop_event,
            on_frame=self._on_frame,
        )

        if self.stop_event.is_set():
            text_placeholder.markdown('<div class="result-card">Reading stopped.</div>', unsafe_allow_html=True)
        else:
            content = " ".join(texts) if texts else "No text detected."
            text_placeholder.markdown(f'<div class="result-card">{content}</div>', unsafe_allow_html=True)

        set_status("listening", IDLE_MESSAGE)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
def start_navigation():
    if st.session_state.nav_thread and st.session_state.nav_thread.is_alive():
        speaker.speak_async("Navigation is already running.")
        return

    stop_event = threading.Event()
    worker = NavigationWorker(detector, stop_event)
    add_script_run_ctx(worker)

    st.session_state.nav_stop_event = stop_event
    st.session_state.nav_thread = worker

    set_status("navigation", 'Navigation running — say "stop navigation" to stop.')
    worker.start()


def stop_navigation():
    if st.session_state.nav_thread and st.session_state.nav_thread.is_alive():
        st.session_state.nav_stop_event.set()
        st.session_state.nav_thread.join(timeout=5)
        image_placeholder.empty()
    else:
        speaker.speak_async("Navigation is not running.")

    set_status("listening", IDLE_MESSAGE)


def handle_read_document():
    if st.session_state.read_thread and st.session_state.read_thread.is_alive():
        speaker.speak_async("Already reading a document.")
        return

    stop_event = threading.Event()
    worker = ReadDocumentWorker(doc_reader, stop_event)
    add_script_run_ctx(worker)

    st.session_state.read_stop_event = stop_event
    st.session_state.read_thread = worker

    set_status("reading", 'Reading document — say "stop reading" to stop.')
    worker.start()


def stop_reading():
    if st.session_state.read_thread and st.session_state.read_thread.is_alive():
        st.session_state.read_stop_event.set()
        speaker.stop()
        st.session_state.read_thread.join(timeout=5)
    else:
        speaker.speak_async("Not reading anything right now.")

    set_status("listening", IDLE_MESSAGE)


def handle_emergency():
    set_status("emergency", "EMERGENCY ACTIVATED")

    ok, msg = emergency_module.activate()
    text_placeholder.markdown(f'<div class="result-card">{msg}</div>', unsafe_allow_html=True)

    time.sleep(1)
    set_status("listening", IDLE_MESSAGE)


def route_command(raw_text: str):
    text = raw_text.lower()

    if "emergency" in text or text.strip() == "help":
        handle_emergency()

    elif "stop" in text and "navigat" in text:
        stop_navigation()

    elif "stop" in text and ("read" in text or "document" in text):
        stop_reading()

    elif text.strip() == "stop":
        if st.session_state.nav_thread and st.session_state.nav_thread.is_alive():
            stop_navigation()
        elif st.session_state.read_thread and st.session_state.read_thread.is_alive():
            stop_reading()
        else:
            speaker.stop()

    elif "navigat" in text or text.strip() == "walk":
        start_navigation()

    elif "read" in text or "document" in text:
        handle_read_document()

    elif "exit" in text or "quit" in text:
        speaker.speak_async("Goodbye.")
        stop_navigation()
        stop_reading()
        set_status("ended", "Session ended. Refresh the page to start again.")
        st.stop()

    else:
        speaker.speak_async("Sorry, I did not understand that.")


# ---------------------------------------------------------------------------
# Main voice loop
# ---------------------------------------------------------------------------
set_status("listening", IDLE_MESSAGE)

while True:
    command = listener.listen()
    heard_placeholder.markdown(f'<div class="heard-caption">Heard: "{command}"</div>', unsafe_allow_html=True)
    route_command(command)