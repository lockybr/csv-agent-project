from flask import Flask, request, render_template_string, redirect, url_for
import os
from agents.csv_agent import CsvAgent
import sys
from pyunpack import Archive
from utils.file_unpacker import unpack_archives

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
ALLOWED_EXTENSIONS = {'csv', 'zip'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
csv_agent = CsvAgent()

# List of free models available on OpenRouter
FREE_MODELS = [
    "deepseek/deepseek-prover-v2:free",
    "nousresearch/nous-capybara-7b:free",
    "openchat/openchat-7b:free"
]

HTML = '''
<!doctype html>
<title>CSV Query Agent</title>
<script>
function showProcessing() {
  document.getElementById('processing-indicator').style.display = 'block';
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
    <option value="{{ model }}">{{ model }}</option>
    {% endfor %}
  </select>
  <input type="text" name="question" placeholder="Ask your question here" required>
  <input type=submit value=Ask>
</form>
<div id="processing-indicator" style="display:none;color:blue;font-weight:bold;">Processando... Por favor, aguarde.</div>
{% if response %}<h3>Response:</h3><pre>{{ response }}</pre>{% endif %}
{% if files %}<h3>Available CSVs:</h3><ul>{% for f in files %}<li>{{ f }}</li>{% endfor %}</ul>{% endif %}
'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML, response=None, files=files, models=FREE_MODELS)

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
        csv_agent._load_csvs()  # Reload CSVs
    return redirect(url_for('index'))

@app.route('/query', methods=['POST'])
def query():
    selected_model = request.form.get('model')
    question = request.form.get('question')
    if not selected_model or not question:
        return "Error: Model and question are required.", 400
    response = csv_agent.process_query(question,selected_model)
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML, response=f"Model: {selected_model}\nQuestion: {question}\n\n{response}", files=files, models=FREE_MODELS)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    print('Starting Flask server on http://127.0.0.1:5000 or http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
