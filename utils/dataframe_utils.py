import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from utils.text_utils import clean_text


# Load dataframe
def load_csv(path: str, encoding: str = 'utf-8') -> pd.DataFrame:
    return pd.read_csv(path, encoding=encoding)

  # Save dataframe
def save_csv(df: pd.DataFrame, path: str, encoding: str = 'utf-8') -> None:
    df.to_csv(path, index=False, encoding=encoding)

# Cleaning
def clean_dataframe(df: pd.DataFrame, text_cols: list = None) -> pd.DataFrame:
        df = df.copy()
        if text_cols is None:
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
        for col in text_cols:
            df[col] = df[col].apply(clean_text)
        return df

def get_top_ngrams(corpus, ngram_range=(1,1), top_n=10):
    vect = CountVectorizer(ngram_range=ngram_range)
    X = vect.fit_transform(corpus)
    sums = X.sum(axis=0)
    freqs = [(ngram, sums[0, idx]) for ngram, idx in vect.vocabulary_.items()]
    return sorted(freqs, key=lambda x: x[1], reverse=True)[:top_n]