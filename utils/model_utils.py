import os
import re
import joblib
from tqdm import tqdm
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.svm import LinearSVC
from transformers import AutoTokenizer, AutoModel
from functools import lru_cache

 # Model-related helpers

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def sanitise(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)

def mean_pool(last_hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """
    Усереднює токен-ембедінги з урахуванням attention_mask.
    Повертає тензор розміру [batch_size, hidden_size].
    """
    # Перемістимо маску на той самий пристрій, що й last_hidden
    device = last_hidden.device
    mask = attention_mask.unsqueeze(-1)            \
             .expand_as(last_hidden)               \
             .to(device)                           \
             .float()

    summed = torch.sum(last_hidden * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts

@lru_cache(maxsize=None)
def load_encoder(encoder_name: str):
    trust = encoder_name.startswith("Goader/liberta")
    tokenizer = AutoTokenizer.from_pretrained(
        encoder_name, trust_remote_code=trust
    )
    model = AutoModel.from_pretrained(
        encoder_name,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        trust_remote_code=trust
    )
    model.config.output_attentions = True
    model.eval()
    return tokenizer, model

def get_embeddings(texts: list[str],
                   encoder_name: str,
                   batch_size: int = 32) -> np.ndarray:
    tokenizer, model = load_encoder(encoder_name)
    all_embeds = []
    for i in tqdm(range(0, len(texts), batch_size),
                  desc=f"Процесс ({encoder_name})"):
        batch = texts[i : i + batch_size]
        enc = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt"
        ).to(DEVICE)

        with torch.no_grad():
            out = model(**enc)
            emb = mean_pool(out.last_hidden_state, enc["attention_mask"])
        all_embeds.append(emb.cpu().numpy())

    return np.vstack(all_embeds)

def train_and_save(df: pd.DataFrame,
                   text_column: str,
                   label_column: str,
                   encoders: list[str],
                   classifiers: list[str],
                   batch_size: int = 32,
                   cv_folds: int = 5,
                   save_dir: str = "models/") -> None:
    texts = df[text_column].astype(str).tolist()
    labels = df[label_column].astype(int).to_numpy()

    os.makedirs(save_dir, exist_ok=True)

    for enc_name in encoders:
        X = get_embeddings(texts, enc_name, batch_size=batch_size)

        for clf_name in classifiers:
            if clf_name == "logreg":
                clf = LogisticRegression(max_iter=1000)
            elif clf_name == "linear_svc":
                clf = LinearSVC()
            elif clf_name == "rf":
                clf = RandomForestClassifier()
            else:
                continue

            scores = cross_val_score(clf, X, labels, cv=cv_folds, scoring="roc_auc")
            print(f"{enc_name} + {clf_name}: AUC = {scores.mean():.3f}")

            clf.fit(X, labels)

            fname = f"{sanitise(enc_name)}_{clf_name}.joblib"
            out_path = os.path.join(save_dir, fname)
            joblib.dump(clf, out_path)
            print(f"→ Saved {clf_name} for {enc_name} to {out_path}")