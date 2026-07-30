import streamlit as st


def show_sidebar():

    with st.sidebar:

        st.markdown("# ⚙️ Settings")

        st.markdown(
            """
            VisionMate is designed for hands-free navigation.

            Configure your preferences below.
            """
        )

        st.markdown("---")

        camera = st.radio(
            "📷 Camera Source",
            [
                "Laptop Camera",
                "Phone / IP camera"
            ]
        )

        st.markdown("---")

        language = st.selectbox(
            "🌍 Assistant Language",
            [
                "English",
                "Hindi",
                "Marathi"
            ],
            index=0
        )

        st.slider(
            "🔊 Voice Volume",
            0,
            100,
            80
        )

        st.slider(
            "⚡ Speech Speed",
            50,
            200,
            100
        )

        st.markdown("---")

        st.info(
            """
🎙 Voice Commands

• Start Navigation

• Describe Scene

• Read Document

• Emergency
"""
        )

        st.markdown("---")

        emergency_btn = st.button(
            "🚨 Emergency",
            use_container_width=True,
            type="primary"
        )

    return {

        "camera": camera,

        "language": language,

        "start": False,

        "emergency_btn": emergency_btn

    }