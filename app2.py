import streamlit as st
import time
import uuid
from services.tts import generate_audio
from services.parser import extract_text_from_pdf, split_into_chunks
from services.chain import split_summaries, prepare_final_summary
from services.closest import return_closest_indices
from services.translator import translate_text
from config import languages

st.set_page_config(page_title="PDF Summarizer", layout="centered")

st.title("📄 Research Paper Summarizer")
st.markdown("Upload a PDF, choose a language, and get a summary with audio output.")

with st.form("summarize_form"):
    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
    language = st.selectbox("Select output language", list(languages.keys()))
    submit = st.form_submit_button("Summarize")

if submit and uploaded_file:
    start = time.time()
    with st.spinner("Extracting text..."):
        contents = extract_text_from_pdf(uploaded_file)
        chunks = split_into_chunks(contents)
        selected_indices = return_closest_indices(chunks)
    with st.spinner("Building summary..."):
        summaries = split_summaries(selected_indices, chunks)
    with st.spinner("Finializing summary..."):
        final_result = prepare_final_summary(summaries)
        result_text = final_result["output_text"]
    with st.spinner("Translating"):
        translated = translate_text(result_text, languages[language])
    
    with st.spinner("Building audio.."):
        audio = generate_audio(translated, languages[language])
    
    st.success("✅ Summary Generated!")
    st.markdown(f"**Time taken:** {round(time.time() - start, 2)} sec")
    st.markdown("**Summary**")
    st.markdown(str(translated))
    st.audio(audio, format='audio/mp3')
