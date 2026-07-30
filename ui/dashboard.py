import streamlit as st


def show_dashboard():

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------
    # Assistant Panel
    # ---------------------------
    assistant = st.empty()

    assistant.info(
        """
### 🎙 Assistant Says

Welcome to VisionMate.

I am ready to help you.

Please say one of the following:

- Start Navigation
- Describe Scene
- Read Document
- Emergency
"""
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------
    # Live Camera
    # ---------------------------
    camera = st.empty()

    camera.info("📷 Waiting for camera...")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------
    # Emergency
    # ---------------------------
    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        sos = st.button(
            "🚨 EMERGENCY",
            use_container_width=True,
            type="primary"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------
    # Hidden placeholders
    # ---------------------------

    navigation = st.empty()

    scene = st.empty()

    objects = st.empty()

    ocr = st.empty()

    voice = st.empty()

    return {

        "camera": camera,

        "assistant": assistant,

        "navigation": navigation,

        "scene": scene,

        "objects": objects,

        "ocr": ocr,

        "voice": voice,

        "emergency": st.empty(),

        "navigate": False,

        "listen": True,

        "read": False,

        "sos": sos,

    }