import pickle
from .btc_dataloader import get_account_summary
import numpy as np

model_path = "models/rfc_bitcoin.bin"

def predict_if_btc_fraud(btc_address):
    rfc_clf = pickle.load(open(model_path, 'rb'))
    in_data = get_account_summary(btc_address)
    pred = rfc_clf.predict(np.array(in_data).reshape(1, -1))

    return True if pred == 1 else False

def predict_if_btc_fraud_with_model(btc_address, model):
    rfc_clf = model
    in_data = get_account_summary(btc_address)
    pred = rfc_clf.predict(np.array(in_data).reshape(1, -1))

    return True if pred == 1 else False