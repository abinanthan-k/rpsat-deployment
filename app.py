import uuid
import time
import secrets
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from services.tts import generate_audio
from services.parser import extract_text_from_pdf, split_into_chunks
from services.chain import split_summaries, prepare_final_summary
from services.closest import return_closest_indices
from services.translator import translate_text

app = Flask(__name__, static_folder='static', template_folder='../templates')
app.secret_key = secrets.token_hex(16)
app.wsgi_app = ProxyFix(app.wsgi_app)
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result')
def result():
    summary = session.get('summary', 'No summary available.')
    time_taken = session.get('time_taken', 'Unknown')
    audio_file = session.get('audio_file', '')
    return render_template("result.html", summary=summary, time_taken=time_taken, audio_file=audio_file)

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files or 'language' not in request.form:
        return "Missing file or language", 400

    file = request.files['file']
    language = request.form['language']
    start = time.time()

    contents = extract_text_from_pdf(file)
    chunks = split_into_chunks(contents)
    selected_indices = return_closest_indices(chunks)
    summaries = split_summaries(selected_indices, chunks)
    final_result = prepare_final_summary(summaries)
    result_text = final_result["output_text"]
    translated = translate_text(result_text, language)
    done_in = round(time.time() - start, 2)

    audio_filename = f"static/audio_{uuid.uuid4().hex}.mp3"
    generate_audio(translated, audio_filename, language)

    session['summary'] = translated
    session['time_taken'] = str(done_in)
    session['audio_file'] = audio_filename

    return redirect(url_for('result'))

# Don't include if __name__ == '__main__'
