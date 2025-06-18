import os
import joblib
import torch
import numpy as np
import shap
from typing import Tuple, List
from config import ENCODER_NAME, CLASSIFIER_NAME, MODEL_DIR
from utils.model_utils import sanitise, mean_pool, load_encoder

# Прогрів при імпорті
_tokenizer, _model = load_encoder(ENCODER_NAME)

# Підвантаження класифікатора
clf_fname = f"{sanitise(ENCODER_NAME)}_{CLASSIFIER_NAME}.joblib"
clf_path = os.path.join(MODEL_DIR, clf_fname)
_clf = joblib.load(clf_path)

def predict_clickbait(title: str) -> Tuple[bool, float]:
    enc = _tokenizer([title], padding=True, truncation=True, max_length=64, return_tensors="pt")
    enc = {k: v.to(_model.device) for k, v in enc.items()}

    with torch.no_grad():
        out = _model(**enc)
        emb = mean_pool(out.last_hidden_state, enc["attention_mask"])

    vec = emb.cpu().numpy()

    pred = _clf.predict(vec)[0]
    is_clickbait = bool(pred)

    if hasattr(_clf, "predict_proba"):
        probability = float(_clf.predict_proba(vec)[0][1])
    elif hasattr(_clf, "decision_function"):
        score = float(_clf.decision_function(vec)[0])
        probability = float(1 / (1 + np.exp(-score)))
    else:
        probability = 1.0 if is_clickbait else 0.0

    return is_clickbait, probability
