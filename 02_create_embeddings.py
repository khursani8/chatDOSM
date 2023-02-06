from glob import glob
import pandas as pd
import tiktoken
from tqdm import tqdm
import openai
import time
from openai.embeddings_utils import get_embedding
from pathlib import Path
# embedding model parameters
embedding_model = "text-embedding-ada-002"
embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191
encoding = tiktoken.get_encoding(embedding_encoding)

def proc(x):
    text = [f"{i.capitalize()}: {v};" for i,v in zip(x.index,x.values) if v is not None]
    return " ".join(text)

files = glob("processed/*")
for i in tqdm(files):
    targ = i.replace("processed/","embeddings/")
    if Path(targ).is_file():
        continue
    df = pd.read_csv(i)
    if 'date' in df.columns: df['date'] = pd.to_datetime(df['date'])
    df["combined"] = df.apply(proc,axis=1)
    df["combined"] = df.combined.apply(lambda x:x + f" Source: {i.split('/')[-1]};")
    df["n_tokens"] = df.combined.apply(lambda x: len(encoding.encode(x)))

    embds = []
    for x in tqdm(df.combined.tolist()):
        try:
            emb = get_embedding(x, engine=embedding_model)
        except:
            print("10 timeout\n")
            time.sleep(10)
            try:
                emb = get_embedding(x, engine=embedding_model)
            except:
                print("10 timeout\n")
                time.sleep(10)
                emb = get_embedding(x, engine=embedding_model)
        embds.append(emb)
        time.sleep(0.9)
    df["embeddings"] = embds
    df.to_csv(targ)