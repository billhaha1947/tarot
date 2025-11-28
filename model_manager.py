import os
from pseudo_ai import stream_pseudo_ai

def load_local_model(model_name):
    return None

def generate_reply(prompt, temperature=0.7, max_tokens=120):
    if not load_local_model(model_name=None):
        text = "".join(stream_pseudo_ai(prompt, max_tokens))
        return text
    return "Local model loaded"

def stream_generate_reply(prompt, temperature=0.7, max_tokens=120):
    if not load_local_model(model_name=None):
        for token in stream_pseudo_ai(prompt, max_tokens):
            yield token
    else:
        yield "local_model_stream..."
