from flask import Flask, request, render_template_string, redirect, url_for
import os
from agents.csv_agent import CsvAgent
from utils.file_unpacker import unpack_archives
import logging
from datetime import datetime
import requests

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
ALLOWED_EXTENSIONS = {'csv', 'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = None
csv_agent = CsvAgent()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"

def fetch_models(free_only=True):
    try:
        headers = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}"}
        response = requests.get(OPENROUTER_API_URL, headers=headers)
        response.raise_for_status()
        all_models = response.json().get('data', [])
        if free_only:
            return [model['id'] for model in all_models if 'free' in model.get('name', '').lower()]
        else:
            return [model['id'] for model in all_models]
    except Exception:
        return []

FREE_MODELS = fetch_models(free_only=True)
ALL_MODELS = fetch_models(free_only=False)

HTML = '''
<!doctype html>
<title>CSV Query Agent</title>
<script>
function showProcessing() {
  document.getElementById('processing-indicator').style.display = 'block';
  document.getElementById('response-container').innerHTML = '';
}
function toggleModelList() {
  document.getElementById('modelForm').submit();
}
</script>
<h1>Upload CSV File</h1>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<h2>Ask a question about your CSV files:</h2>
<form id="modelForm" method=post action="/" onsubmit="showProcessing()">
  <label><input type="checkbox" name="free_only" value="1" onchange="toggleModelList()" {% if free_only %}checked{% endif %}> Free Models Only</label>
  <br>
  <select name="model" required>
    <option value="">Select a model</option>
    {% for model in models %}
    <option value="{{ model }}" {% if model == selected_model %}selected{% endif %}>{{ model }}</option>
    {% endfor %}
  </select>
  <br><br>
  <input type="text" name="question" placeholder="Ask your question here" required value="{{ question }}">
  <input type="text" name="api_key" placeholder="Enter your API key here (optional)" value="{{ api_key }}">
  <input type=submit value=Ask>
</form>
<div id="processing-indicator" style="display:none;color:blue;font-weight:bold;">Processando... Por favor, aguarde.</div>
<div id="response-container">
  {% if response %}<h3>Response:</h3><pre>{{ response }}</pre>{% endif %}
</div>
{% if files %}<h3>Available CSVs:</h3><ul>{% for f in files %}<li>{{ f }}</li>{% endfor %}</ul>{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    user_api_key = ''
    response = ''
    question = ''
    model = ''
    free_only = True

    if request.method == 'POST':
        question = request.form.get('question', '')
        user_api_key = request.form.get('api_key', '')
        model = request.form.get('model', '')
        # Corrige: checkbox envia 'on' se desmarcado, '1' se marcado
        free_only = request.form.get('free_only') == '1'
        if question and model:
            api_key = user_api_key if user_api_key else os.environ.get('OPENROUTER_API_KEY')
            response = csv_agent.process_query(question, model=model, api_key=api_key)
        # Se não, só atualiza a lista de modelos

    files = os.listdir(UPLOAD_FOLDER)
    models = FREE_MODELS if free_only else ALL_MODELS
    return render_template_string(HTML, response=response, files=files, models=models, api_key=user_api_key, question=question, selected_model=model, free_only=free_only)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        if file.filename.endswith('.zip'):
            unpack_archives(app.config['UPLOAD_FOLDER'])
        csv_agent._load_csvs()
    return redirect(url_for('index'))

@app.route('/query', methods=['POST'])
def query():
    selected_model = request.form.get('model')
    question = request.form.get('question')
    user_api_key = request.form.get('api_key')
    files = os.listdir(UPLOAD_FOLDER)
    free_only = request.form.get('free_only') == '1'

    if not selected_model or not question:
        return "Error: Model and question are required.", 400

    api_key = user_api_key.strip() if user_api_key and user_api_key.strip() else os.environ.get('OPENAI_API_KEY')

    if not api_key:
        return render_template_string(HTML, response="Error: No valid API key provided. Please provide a valid API key.", files=files, models=FREE_MODELS, api_key=user_api_key)

    if len(api_key) < 10:
        return render_template_string(HTML, response="Error: Invalid API key format. Please check your API key.", files=files, models=FREE_MODELS, api_key=user_api_key)

    if free_only and selected_model not in FREE_MODELS:
        return render_template_string(HTML, response=f"Error: The selected model '{selected_model}' is not supported or unavailable.", files=files, models=FREE_MODELS, api_key=user_api_key)

    try:
        response = csv_agent.process_query(question, selected_model, api_key=api_key)
    except ValueError as e:
        if "402" in str(e):
            response = "Error: Insufficient credits. Please check your OpenRouter account or reduce query complexity."
        else:
            response = f"Error: {str(e)}"

    files = os.listdir(UPLOAD_FOLDER)
    api_key_display = user_api_key.strip() if user_api_key and user_api_key.strip() else '[OS Environment]'
    return render_template_string(HTML, response=f"Model: {selected_model}\nQuestion: {question}\nAPI Key: {api_key_display}\n\n{response}", files=files, models=FREE_MODELS, api_key=user_api_key, question=question, selected_model=selected_model, api_key_display=api_key_display)

@app.route('/debug-html', methods=['GET'])
def debug_html():
    rendered_html = render_template_string(HTML, response='', files=os.listdir(UPLOAD_FOLDER), models=FREE_MODELS, api_key='')
    return rendered_html, 200

@app.before_request
def log_request_info():
    print(f"[{datetime.now()}] Incoming request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    print(f"Remote Address: {request.remote_addr}")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
