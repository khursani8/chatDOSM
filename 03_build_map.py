from glob import glob
import pandas as pd
from tqdm import tqdm
files = glob("embeddings/*")

mappings = []
for i in tqdm(files):
    df = pd.read_csv(i)
    ll = df.embeddings.tolist()
    for idx,emb in enumerate(ll):
        mappings.append([i.split("/")[-1],idx,emb])

df = pd.DataFrame(mappings)
df.columns = ["source","row","embeddings"]
df.to_csv("mappings.csv")