from gpt4all import GPT4All
import os

MODEL_PATH = "models/llama.gguf"
model = None

def load_model(name):
    global model
    try:
        model = GPT4All(name)
        return True
    except:
        model = None
        return False

def generate_reply(prompt, temperature=0.7, max_tokens=200):
    if model:
        return model.generate(prompt, temp=temperature, max_tokens=max_tokens)
    from pseudo_ai import stream_pseudo_reply
    return "".join(stream_pseudo_reply(prompt, temperature, max_tokens))

def stream_generate_reply(prompt, temperature=0.7, max_tokens=200):
    if model:
        for token in model.generate(prompt, temp=temperature, max_tokens=max_tokens, streaming=True):
            yield token
    else:
        from pseudo_ai import stream_pseudo_reply
        for ch in stream_pseudo_reply(prompt, temperature, max_tokens):
            yield ch
