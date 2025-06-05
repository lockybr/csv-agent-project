from flask import Flask, request, render_template_string, redirect, url_for
import os
from agents.csv_agent import CsvAgent
from utils.file_unpacker import unpack_archives
import requests

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
ALLOWED_EXTENSIONS = {'csv', 'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = None
csv_agent = CsvAgent()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"

def fetch_free_models():
    try:
        headers = {"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}"}
        response = requests.get(OPENROUTER_API_URL, headers=headers)
        response.raise_for_status()
        all_models = response.json().get('data', [])
        free_models = [
            model['id'] for model in all_models
            if 'free' in model.get('name', '').lower()
        ]
        return free_models
    except Exception:
        return []

FREE_MODELS = fetch_free_models()

HTML = '''
<!doctype html>
<title>CSV Query Agent</title>
<script>
function showProcessing() {
  document.getElementById('processing-indicator').style.display = 'block';
  document.getElementById('response-container').innerHTML = ''; 
}
</script>
<h1>Upload CSV File</h1>
<form method=post enctype=multipart/form-data action="/upload">
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<h2>Ask a question about your CSV files:</h2>
<form method=post action="/query" onsubmit="showProcessing()">
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

    if request.method == 'POST':
        question = request.form.get('question', '')
        user_api_key = request.form.get('api_key', '')
        model = request.form.get('model', '')
        api_key = user_api_key if user_api_key else os.environ.get('OPENAI_API_KEY')
        response = csv_agent.process_query(question, model=model, api_key=api_key)

    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML, response=response, files=files, models=FREE_MODELS, api_key=user_api_key, question=question, selected_model=model)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        if file.filename.endswith('.zip'):
            unpack_archives(UPLOAD_FOLDER)
    return redirect(url_for('index'))

@app.route('/query', methods=['POST'])
def query():
    question = request.form.get('question', '')
    user_api_key = request.form.get('api_key', '')
    model = request.form.get('model', '')
    api_key = user_api_key if user_api_key else os.environ.get('OPENAI_API_KEY')
    response = csv_agent.process_query(question, model=model, api_key=api_key)
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML, response=response, files=files, models=FREE_MODELS, api_key=user_api_key, question=question, selected_model=model)

@app.route('/debug-html', methods=['GET'])
def debug_html():
    rendered_html = render_template_string(HTML, response='', files=os.listdir(UPLOAD_FOLDER), models=FREE_MODELS, api_key='')
    return rendered_html, 200

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
