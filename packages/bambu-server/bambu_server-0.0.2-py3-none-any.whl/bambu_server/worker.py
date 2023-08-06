from .config import celery
from bambu.predict.run import model_predict_wrapper
from rdkit import Chem
from typing import List, Dict
import yagmail
import subprocess
import pandas as pd
import argparse
import pickle
import os

@celery.task()
def run_bambu_models(molecules_smiles:List[str], config:Dict) -> Dict:

    molecules_smiles = [m for m in molecules_smiles.split('\n') if m]

    loaded_models = []
    model_names = []

    for model_data in config['models']:
        preprocessor = pickle.loads(open(model_data['preprocessor'], 'rb').read())
        model = pickle.loads(open(model_data['model'], 'rb').read())
        loaded_models.append((model_data['name'], preprocessor, model))
        model_names.append(model_data['name'])

    results = {'model_names': model_names, 'results': []}

    for molecule_smile in molecules_smiles:
        molecule_smile = molecule_smile.strip("\n").strip('\r')
        mol = Chem.MolFromSmiles(molecule_smile)
        results['results'].append({"molecule": molecule_smile, 'predictions': {}})
        for model_name, preprocessor, model in loaded_models:
            _, predicted_activity_proba = model_predict_wrapper(mol, model, preprocessor)
            if predicted_activity_proba is None:
                predicted_activity_proba_str = "N/A"
            else:
                predicted_activity_proba_str = "%.4f"%(predicted_activity_proba * 100)
            results['results'][-1]['predictions'][model_name] = predicted_activity_proba_str
    
    return results

'''
@celery.task()
def send_email_notification(subject, body, to):
    yag = yagmail.SMTP('mygmailusername', 'mygmailpassword')
    yag.send(to, subject, body)
'''

def main():
    argument_parser = argparse.ArgumentParser(description="bambu-worker: async execution of bambu models")
    argument_parser.add_argument('-n', '--name', default="worker@%h", help="worker name")
    argument_parser.add_argument('-c', '--concurrency', default=1, help='max number concurrent jobs')
    arguments = argument_parser.parse_args()
    subprocess.call(f'celery -A bambu_server.worker.celery worker --concurrency={arguments.concurrency} -n {arguments.name}',
                    shell=True)

if __name__ == "__main__":
    main()
