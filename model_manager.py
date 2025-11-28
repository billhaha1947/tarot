import os
from gpt4all import GPT4All
from pseudo_ai import stream_generate_reply as pseudo_stream

model = None
MODEL_STORE = "models"
DEFAULT_MODEL_NAME = "local-llama"

def load_model(model_name=DEFAULT_MODEL_NAME):
    global model
    try:
        model = GPT4All(model_name, model_path=MODEL_STORE, allow_download=False)
        return True
    except Exception:
        model = None
        return False

def generate_reply(prompt, temperature=0.7, max_tokens=200):
    if model:
        try:
            return model.generate(prompt, temp=temperature, max_tokens=max_tokens)
        except:
            return "".join(pseudo_stream(prompt, temperature, max_tokens))
    return "".join(pseudo_stream(prompt, temperature, max_tokens))

def stream_generate_reply(prompt, temperature=0.7, max_tokens=200):
    if model:
        try:
            for token in model.generate(prompt, temp=temperature, max_tokens=max_tokens, streaming=True):
                yield token
        except:
            for ch in pseudo_stream(prompt, temperature, max_tokens):
                yield ch
    else:
        for ch in pseudo_stream(prompt, temperature, max_tokens):
            yield ch
