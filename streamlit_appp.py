import time
import cv2
import streamlit as st

import config
from vision.detector import VisionDetector
from ocr.reader import OCRReader
from modules.emergency import Emergency
from core.speaker_manager import speaker
from voice.listener import VoiceListener

st.set_page_config(page_title="VisionMate", page_icon="🦯", layout="wide")
st.title("🦯 VisionMate Dashboard")
st.caption("Deep learning-based assistive tool for visually impaired users")

cam_choice = st.sidebar.radio("Camera source", ["Phone / IP camera (config.py)", "Laptop webcam (index 0)"])
CAM_SOURCE = config.VIDEO_URL if cam_choice.startswith("Phone") else 0
st.sidebar.caption(f"Using: `{CAM_SOURCE}`")


@st.cache_resource
def get_detector():
    return VisionDetector()


@st.cache_resource
def get_ocr_reader():
    return OCRReader()


@st.cache_resource
def get_listener():
    return VoiceListener()


# ---------------------------------------------------------------------
# Shared placeholders (used by both button clicks and voice commands)
# ---------------------------------------------------------------------
status_slot = st.empty()
frame_slot = st.empty()
scene_slot = st.empty()
objects_slot = st.empty()


def run_navigation(duration=15):
    status_slot.info("Starting navigation...")
    speaker.speak_async("Starting navigation")

    with st.spinner("Loading vision engine (first run only)..."):
        detector = get_detector()

    cap = cv2.VideoCapture(CAM_SOURCE, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        status_slot.error(f"Could not open camera source `{CAM_SOURCE}`.")
        speaker.speak_async("Camera not available.")
        return

    end_time = time.time() + duration
    last_warning = None
    last_warning_time = 0
    WARNING_DISPLAY_TIME = 1.0

    while time.time() < end_time:
        success, frame = cap.read()
        if not success:
            status_slot.warning("Camera stopped sending frames.")
            break

        detected_objects, decision, scene_description, annotated_frame = detector.process_frame(frame)

        categorized = detector.object_filter.filter_objects(detected_objects)
        warnings = detector.safety_engine.analyze(categorized)
        warning = detector.warning_manager.get_warning(warnings)

        if warning:
            last_warning = warning
            last_warning_time = time.time()
            speaker.speak_async(warning["message"])

        if last_warning is not None and time.time() - last_warning_time < WARNING_DISPLAY_TIME:
            annotated_frame = detector.ui.draw_warning_panel(annotated_frame, last_warning)
            annotated_frame = detector.ui.draw_object_labels(annotated_frame, detected_objects)

        frame_slot.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
        scene_slot.info(f"**Scene:** {scene_description}")

        if detected_objects:
            rows = [f"- {o['name']} ({o['direction']}, {o['distance']})" for o in detected_objects]
            objects_slot.markdown("\n".join(rows))
        else:
            objects_slot.write("No objects detected.")

    cap.release()
    status_slot.success("Navigation stopped.")


def run_describe_scene():
    status_slot.info("Describing scene...")
    with st.spinner("Loading vision engine (first run only)..."):
        detector = get_detector()

    cap = cv2.VideoCapture(CAM_SOURCE, cv2.CAP_FFMPEG)
    frame = None
    if cap.isOpened():
        success, frame = cap.read()
    cap.release()

    if frame is None:
        status_slot.error(f"Could not open camera source `{CAM_SOURCE}`.")
        speaker.speak_async("Camera not available.")
        return

    detected_objects, decision, scene_description, annotated_frame = detector.process_frame(frame)
    frame_slot.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
    scene_slot.info(f"**Scene:** {scene_description}")
    speaker.speak_async(scene_description)
    status_slot.success("Scene described.")


def run_read_document():
    status_slot.info("Reading document...")
    with st.spinner("Loading OCR engine (first run only)..."):
        reader = get_ocr_reader()

    speaker.speak("Hold the document steady.")

    cap = cv2.VideoCapture(CAM_SOURCE, cv2.CAP_FFMPEG)
    frame = None
    if cap.isOpened():
        for _ in range(10):
            success, frame = cap.read()
        cap.release()

    if frame is None:
        status_slot.error(f"Could not open camera source `{CAM_SOURCE}`.")
        speaker.speak_async("Camera not available.")
        return

    frame_slot.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Captured frame", use_container_width=True)

    with st.spinner("Reading text..."):
        texts = reader.read_text(frame)

    if texts:
        full_text = " ".join(texts)
        scene_slot.success(full_text)
        speaker.speak_async(full_text)
    else:
        scene_slot.warning("No text detected. Move closer and try again.")
        speaker.speak_async("No text detected. Please move closer and try again.")

    status_slot.success("Done reading.")


def run_emergency():
    status_slot.info("Triggering emergency alert...")
    emergency = Emergency()
    emergency.activate()
    status_slot.success("Emergency sequence triggered (check terminal for status).")


COMMAND_MAP = {
    "start navigation": lambda: run_navigation(15),
    "describe scene": run_describe_scene,
    "read document": run_read_document,
    "read text": run_read_document,
    "emergency": run_emergency,
}

# ---------------------------------------------------------------------
# Voice command entry point
# ---------------------------------------------------------------------
st.subheader("🎤 Voice Control")
st.caption("Say one of: 'start navigation', 'describe scene', 'read document', 'emergency'")

if st.button("🎤 Listen for command", use_container_width=True):
    with st.spinner("Loading voice model (first run only)..."):
        listener = get_listener()

    status_slot.info("Listening...")
    command = listener.listen()
    status_slot.write(f"Heard: **{command}**")

    action = COMMAND_MAP.get(command)
    if action:
        action()
    else:
        status_slot.warning(f"Command not recognized: '{command}'")
        speaker.speak_async("Sorry, I didn't understand that command.")

st.markdown("---")
st.subheader("Or trigger manually")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶ Start Navigation", use_container_width=True):
        run_navigation(15)
with col2:
    if st.button("📄 Read Document", use_container_width=True):
        run_read_document()
with col3:
    if st.button("🚨 Emergency", use_container_width=True):
        run_emergency()

st.sidebar.markdown("---")
st.sidebar.caption("VisionMate • run with `streamlit run streamlit_app.py`")
