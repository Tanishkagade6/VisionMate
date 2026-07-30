import streamlit as st

def show_footer():

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        """
<div style="
text-align:center;
padding:15px;
font-size:16px;
color:#666;
">

<b>VisionMate V2</b><br>

Built with ❤️ to empower visually impaired users.

YOLOv8 • OCR • Speech Recognition • Text-to-Speech • Streamlit

</div>
""",
        unsafe_allow_html=True,
    )