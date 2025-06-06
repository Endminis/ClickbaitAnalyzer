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

# Кешування SHAP компоненти

def shap_pipeline(inputs: List) -> np.ndarray:
    texts = [" ".join(x) if isinstance(x, list) else str(x) for x in inputs]
    enc = _tokenizer(texts, padding=True, truncation=True, max_length=64, return_tensors="pt")
    enc = {k: v.to(_model.device) for k, v in enc.items()}

    with torch.no_grad():
        out = _model(**enc)
        emb = mean_pool(out.last_hidden_state, enc["attention_mask"])

    return _clf.predict_proba(emb.cpu().numpy())[:, 1]

_explainer = shap.Explainer(
    shap_pipeline,
    shap.maskers.Text(_tokenizer),
    algorithm="partition"
)


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

def shap_explain_clickbait(title: str, num_samples: int = None) -> List[Tuple[str, float]]:
    tokens = _tokenizer.tokenize(title)
    max_evals = num_samples or min(64, len(tokens) * 6)

    shap_values = _explainer([title], max_evals=max_evals)
    tokens = shap_values.data[0]
    scores = shap_values.values[0]
    if len(tokens) > 2:
        tokens = tokens[1:-1]
        scores = scores[1:-1]
    return list(zip(tokens, scores))