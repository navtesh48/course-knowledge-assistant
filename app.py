"""Streamlit chat + library browser.   streamlit run app.py"""
import streamlit as st

from cka import config, db, rag

st.set_page_config(page_title="Course Knowledge Assistant", page_icon="📚", layout="wide")
st.title("📚 Course Knowledge Assistant")

try:
    courses = db.list_courses()
except Exception as e:
    st.error(f"Database unavailable: {e}")
    st.stop()

with st.sidebar:
    st.header("Filter")
    course = st.selectbox("Course", ["All"] + courses)
    st.caption(f"Drop files into `{config.INBOX_DIR}/<course>/<topic>/` and run `python -m cka.ingest --watch`.")

chat_tab, library_tab = st.tabs(["Ask", "Library"])

with chat_tab:
    if "history" not in st.session_state:
        st.session_state.history = []
    for role, msg, sources in st.session_state.history:
        with st.chat_message(role):
            st.markdown(msg)
            for s in sources:
                st.caption(f"[{s['n']}] {s['title']} · {s['course']}/{s['topic']} · {s['source_type']}")
    if q := st.chat_input("Ask a question about your materials"):
        st.session_state.history.append(("user", q, []))
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("Searching your notes…"):
                a = rag.ask(q, None if course == "All" else course)
            st.markdown(a.text)
            for s in a.sources:
                st.caption(f"[{s['n']}] {s['title']} · {s['course']}/{s['topic']} · {s['source_type']}")
        st.session_state.history.append(("assistant", a.text, a.sources))

with library_tab:
    docs = db.list_documents(None if course == "All" else course)
    st.metric("Documents", len(docs))
    st.dataframe(docs, use_container_width=True)
