from pseudo_ai import generate_reply, stream_generate_reply

ACTIVE_MODEL = None

def load_model(name):
    global ACTIVE_MODEL
    if name.lower() in ["gpt4all","llama","llama.gguf"]:
        # Giả lập: chưa có model thật -> để None và dùng pseudo AI
        ACTIVE_MODEL = None
    else:
        ACTIVE_MODEL = None

def get_active_model():
    return ACTIVE_MODEL

def generate_reply(prompt, temperature=0.7, max_tokens=200):
    return generate_reply(prompt, temperature, max_tokens)

def stream_generate_reply(prompt, temperature=0.7, max_tokens=200):
    for token in stream_generate_reply(prompt, temperature, max_tokens):
        yield token
