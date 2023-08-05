from flask import render_template, redirect, request, jsonify
from celery.result import AsyncResult
from .worker import run_bambu_models
from .config import app, celery

@app.route('/')
def index():
    return render_template(
        "index.html",
        app_name=app.config['BAMBU_CONFIG']['name'],
        app_description=app.config['BAMBU_CONFIG']['description']
    )

@app.route('/predict', methods=['POST'])
def predict():
    molecules_smiles = request.form.get('molecules_smiles')
    job_id = run_bambu_models.apply_async((molecules_smiles, app.config['BAMBU_CONFIG']),)
    return redirect(f'/results/{job_id}')

@app.route('/results/<job_id>', methods=['GET'])
def results(job_id:str):
    job_result = AsyncResult(job_id, app=celery)
    
    return render_template(
        'results.html', 
        app_name=app.config['BAMBU_CONFIG']['name'], 
        app_description=app.config['BAMBU_CONFIG']['description'],
        job_result=job_result,
        job_state=job_result.state
    )

@app.route('/results/<job_id>.json', methods=['GET'])
def results_json(job_id:str):
    job_result = AsyncResult(job_id, app=celery)
    return jsonify(job_result.get())
    
