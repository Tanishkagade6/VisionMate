import streamlit as st


def show_header():

    st.markdown(
        """
        <div class="hero-box">
            <h1>🦯 VisionMate</h1>
            <p>Your AI Navigation Companion</p>
            <hr>
            <h3 style="margin-top:15px;">
                🎤 Ready to Listen
            </h3>
            <p>
                Say:
                <b>"Start Navigation"</b>,
                <b>"Read Document"</b>,
                <b>"Describe Scene"</b>
                or
                <b>"Emergency"</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        camera_status = st.success("📷 Camera Ready")

    with col2:
        ocr_status = st.success("📄 OCR Ready")

    with col3:
        voice_status = st.success("🎤 Listening")

    st.markdown("<br>", unsafe_allow_html=True)

    return {

        "camera_status": camera_status,

        "ocr_status": ocr_status,

        "voice_status": voice_status

    }