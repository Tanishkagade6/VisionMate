import time
import cv2
import streamlit as st
import config
from vision.detector import VisionDetector
from ocr.reader import OCRReader
from modules.emergency import Emergency
from core.speaker_manager import speaker
from voice.listener import VoiceListener
from ui.header import show_header
from ui.sidebar import show_sidebar
from ui.dashboard import show_dashboard
from ui.footer import show_footer

def assistant_reply(message, level="info"):

    if level == "info":
        assistant_slot.info(f"### 🎙 Assistant Says\n\n{message}")

    elif level == "success":
        assistant_slot.success(f"### 🎙 Assistant Says\n\n{message}")

    elif level == "warning":
        assistant_slot.warning(f"### 🎙 Assistant Says\n\n{message}")

    elif level == "error":
        assistant_slot.error(f"### 🎙 Assistant Says\n\n{message}")

    speaker.speak_async(message)

def load_css():
    with open("assets/theme.css") as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)

st.set_page_config(page_title="VisionMate", page_icon="🦯", layout="wide")

load_css()

sidebar = show_sidebar()
CAM_SOURCE = config.VIDEO_URL if sidebar["camera"] == "Phone / IP camera" else 0

header = show_header()
dashboard = show_dashboard()
assistant_slot = dashboard["assistant"]

if "mode" not in st.session_state:
    st.session_state.mode = "listening"

if "current_command" not in st.session_state:
    st.session_state.current_command = None

# Welcome message
if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = True

    speaker.speak_async("Welcome to VisionMate. I am ready. Please say a command.")

    assistant_slot.success("""### 🎙 Assistant Says Welcome to VisionMate. 
                           I am ready. Please say a command. """)

@st.cache_resource
def get_detector():
    return VisionDetector()

@st.cache_resource
def get_ocr_reader():
    return OCRReader()

@st.cache_resource
def get_listener():
    return VoiceListener()

@st.cache_resource
def get_camera():
    if isinstance(CAM_SOURCE, str):
        cap = cv2.VideoCapture(CAM_SOURCE)
    else:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    return cap

# ---------------------------------------------------------------------
# Shared placeholders (used by both button clicks and voice commands)
# ---------------------------------------------------------------------
status_slot = st.empty()

frame_slot = dashboard["camera"]

emergency_slot = dashboard["emergency"]

def run_navigation(duration=15):
    header["camera_status"].success("🟢 Camera Active")
    assistant_slot.info("""### \
        🎙 Assistant Says 
        Starting Navigation...
        """)
    speaker.speak_async("Starting navigation")

    with st.spinner("Loading vision engine (first run only)..."):
        detector = get_detector()

    cap = get_camera()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        assistant_slot.error("""
    ### 🎙 Assistant Says

    I couldn't access the camera.

    You can try another command.

    For example:

    • Read document

    • Describe scene

    • Emergency
    """)

        speaker.speak_async(
            "I couldn't access the camera. Please try another command."
        )

        header["voice_status"].success("🎤 Listening...")

        time.sleep(1)

        # st.rerun()
        
        
    end_time = time.time() + duration
    last_warning = None
    last_warning_time = 0
    WARNING_DISPLAY_TIME = 1.0

    while time.time() < end_time:
        success, frame = cap.read()
        print("Camera success:", success)
        
        if not success:
            status_slot.warning("Camera stopped sending frames.")
            break

        detected_objects, decision, scene_description, annotated_frame = detector.process_frame(frame)

        if decision is None:
            navigation = "No navigation instruction."
        else:
            navigation = decision.get("navigation", "No navigation instruction.")        
                
        if decision is None:
            decision = "No navigation instruction available."

        # decision = str(decision)
        assistant_reply(navigation)

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
        assistant_slot.info(f"""### 🎙 Assistant Says {scene_description}""")
        
    status_slot.success("Navigation stopped.")
    header["camera_status"].success("📷 Camera Ready")

def run_describe_scene():
    assistant_slot.info("""### 
                        🎙 Assistant Says 
                        Looking around...""")  
    
    with st.spinner("Loading vision engine (first run only)..."):
        detector = get_detector()

    cap = get_camera()
    frame = None
    if cap.isOpened():
        success, frame = cap.read()
   

    if frame is None:
        status_slot.error(f"Could not open camera source `{CAM_SOURCE}`.")
        speaker.speak_async("Camera not available.")
        return

    detected_objects, decision, scene_description, annotated_frame = detector.process_frame(frame)
    frame_slot.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB), use_container_width=True)
    assistant_slot.info(f"""### 
                        🎙 Assistant Says 
                        {scene_description} 
                        """)
    speaker.speak_async(scene_description)
    status_slot.success("Scene described.")
    
    time.sleep(1)

    # st.rerun()

def run_read_document():
    header["ocr_status"].success("📷 Camera Ready")
    assistant_slot.info("""### 
                        🎙 Assistant Says 
                        Hold the document steady...
                        Reading document...
                        """)
    
    with st.spinner("Loading OCR engine (first run only)..."):
        reader = get_ocr_reader()

    speaker.speak("Hold the document steady.")

    cap = get_camera()
    frame = None
    
    if cap.isOpened():
        for _ in range(10):
            success, frame = cap.read()

    if frame is None:
        status_slot.error(f"Could not open camera source `{CAM_SOURCE}`.")
        speaker.speak_async("Camera not available.")
        return

    frame_slot.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 
                     caption="Captured frame", use_container_width=True)

    with st.spinner("Reading text..."):
        texts = reader.read_text(frame)

    if texts:
        full_text = " ".join(texts)
        assistant_slot.success(f"""### 
                               🎙 Assistant Says 
                               {full_text} 
                               """)        
        speaker.speak_async(full_text)
    else:
        assistant_slot.warning("""### 
                               🎙 Assistant Says No text detected.
                                Please move closer and try again.
                                """)
        
        speaker.speak_async("No text detected. Please move closer and try again.")
    
    header["ocr_status"].success("📄 OCR Ready")
    status_slot.success("Done reading.")
    
    time.sleep(1)

    # st.rerun()

def run_emergency():
    assistant_slot.error("""### 
                         🚨 Assistant Says 
                         Emergency Activated 
                         """)
    emergency = Emergency()
    emergency.activate()
    emergency_slot.error("🚨 SOS Activated")
    status_slot.success("Emergency sequence triggered.")
    
COMMAND_MAP = {
    "start navigation": lambda: run_navigation(15),
    "describe scene": run_describe_scene,
    "read document": run_read_document,
    "read text": run_read_document,
    "emergency": run_emergency,
}

# ==========================================
# Dashboard Button Actions
# ==========================================

if dashboard["navigate"]:
    run_navigation(15)

if dashboard["read"]:
    run_read_document()

if dashboard["sos"]:
    run_emergency()

with st.spinner("Loading Voice Assistant..."):
    listener = get_listener()

header["voice_status"].success("🎤 Listening...")

assistant_slot.info("""### 
                    🎙 Assistant Says Listening... 
                    Say a command.
                    """)


# assistant_slot.success(f"""### 
#                        🎙 Assistant Says 
#                        Command Recognised 
#                        {command}
#                        """)

# action = COMMAND_MAP.get(command)

# if action:
#     action()

# else:
#     speaker.speak_async("Sorry. I didn't understand.")
#     assistant_slot.warning("""### 
#                            🎙 Assistant Says Sorry. 
#                            Please repeat your command.
#                            """)

# if not command:
#     assistant_reply(
#         "I didn't hear anything. Please try again.",
#         "warning"
#     )
#     st.rerun()

if st.session_state.mode == "listening":

    print("STEP 1")

    header["voice_status"].success("🎤 Listening...")

    assistant_slot.info("""
    ### 🎙 Assistant Says

    Listening...
    Say a command.
    """)

    print("STEP 2")

    command = listener.listen()

    print("STEP 3")
    print(command)

    if not command:
        print("STEP 4")
        assistant_reply(
            "I didn't hear anything.",
            "warning"
        )
        st.rerun()

    print("STEP 5")

    st.session_state.current_command = command
    st.session_state.mode = "executing"

    print("STEP 6")

    st.rerun()

elif st.session_state.mode == "executing":

    command = st.session_state.current_command

    assistant_reply(f"Command recognised: {command}")

    action = COMMAND_MAP.get(command)

    if action:
        action()
    else:
        assistant_reply(
            "Sorry, I didn't understand.",
            "warning"
        )

    st.session_state.mode = "listening"

    st.session_state.current_command = None

    st.rerun()
    
# ==========================================
# Sidebar Actions
# ==========================================

if sidebar["start"]:
    run_navigation(15)

if sidebar["emergency_btn"]:
    run_emergency()

st.markdown("---")
show_footer()