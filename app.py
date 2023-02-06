import gradio as gr
import openai
from openai.embeddings_utils import distances_from_embeddings
import pandas as pd
import numpy as np
from pdb import set_trace
import os
os.system("wget https://zenodo.org/record/7609690/files/mappings.csv?download=1 -O mappings.csv")
os.system("wget https://zenodo.org/record/7609690/files/knn.index?download=1 -O knn.index")
os.system("wget https://zenodo.org/record/7609690/files/index_infos.json?download=1 -O index_infos.json")
def create_context(
    question, df
):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    _, I = index.search(np.array(q_embeddings)[None], 5)
    context_sources = df.iloc[I[0]]

    returns = []

    for _,i in context_sources.iterrows():
        tmp = pd.read_csv("embeddings/"+i["source"])
        out = tmp.iloc[i["row"]]["combined"]
        returns.append(out)
    # Return the context
    return returns

import faiss
index = faiss.read_index("knn.index", faiss.IO_FLAG_MMAP | faiss.IO_FLAG_READ_ONLY)
mapping = pd.read_csv("mappings.csv")
def chat(message, history, openai_api_key):
    openai.api_key = openai_api_key
    returns = create_context(
        message,
        mapping
    )
    context = "\n\n###\n\n".join(returns)
    try:
        # Create a completions using the question and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            model="text-davinci-003",
        )
        out = response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return ""
    history = history or []
    history.append((message, out))
    
    return history, history, pd.DataFrame(returns)

with gr.Blocks() as demo:
  gr.HTML("""<div style="text-align: center; max-width: 700px; margin: 0 auto;">
        <div
        style="
            display: inline-flex;
            align-items: center;
            gap: 0.8rem;
            font-size: 1.75rem;
        "
        >
        <h1 style="font-weight: 900; margin-bottom: 7px; margin-top: 5px;">
            DOSM QandA bot
        </h1>
        </div>
        <p style="margin-bottom: 10px; font-size: 94%">
        Hi, I'm a Q and A DOSM expert bot, start by typing in your OpenAI API key, questions/issues you are facing in your DOSM implementations and then press enter.<br>
        </p>
        <p> Cutoff period: 4 FEB 2023 https://open.dosm.gov.my/data-catalogue</p>
        Get OpenAI API key <a href=https://platform.openai.com/account/api-keys>here</a>
    </div>""")  
  with gr.Row():
    question = gr.Textbox(label = 'Type in your questions about DOSM here and press Enter!', placeholder = 'What questions do you want to ask about data in DOSM?')
    openai_api_key = gr.Textbox(type='password', label="Enter your OpenAI API key here")
  with gr.Row():
    context = gr.Dataframe(type="pandas", datatype="str")
  state = gr.State()
  chatbot = gr.Chatbot()
  question.submit(chat, [question, state, openai_api_key], [chatbot, state, context])
  gr.HTML("""
        TLDR; Working on this because of this tweet https://twitter.com/huseinzolkepli/status/1620662587410243584?s=20 <br/> 
        Only working on the embeddings part, for the visualization I did not working on it because afraid of someone do remote code exec which can trigger any code <br/>
        Need to study how to avoid user input lead to RCE <br/>
        That's why until now ChatGPT only allow q&a without executing or searching web in order to avoid connecting to some weird server.
        <br/><br/>
        Time Taken building this project:
        4-5 hours study and work on it:<br/>
        2 days building embeddings :v (pikachu shock face), $4 for all embeddings of DOSM<br/>
        
        <br/><br/>
        Learn from: https://platform.openai.com/docs/tutorials/web-qa-embeddings <br/>
        Other embeddings db if you want to try: https://platform.openai.com/docs/guides/embeddings/how-can-i-retrieve-k-nearest-embedding-vectors-quickly <br/>
        Steal UI code from https://huggingface.co/spaces/ysharma/LangchainBot-space-creator <br/>
    </div>""")

demo.launch()