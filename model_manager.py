import os, random
from gpt4all import GPT4All
from pseudo_ai import stream_generate_reply as pseudo_stream, TAROT_CARDS

MODEL_PATH_ENV="LOCAL_AI_MODEL_PATH"

def load_model():
    path=os.getenv(MODEL_PATH_ENV,"")
    if not path or not os.path.exists(path):
        return None
    return GPT4All(path, allow_download=False)

_model=load_model()

def generate_reply(prompt, temperature=0.7, max_tokens=200):
    if _model is None:
        return random.choice([
            "Oracle thấy năng lượng đang chuyển biến…",
            "Vũ trụ sắp gửi tín hiệu quan trọng cho bạn.",
            "Hãy dừng lại lắng nghe trái tim."
        ])
    return _model.generate(prompt, temp=temperature, max_tokens=max_tokens)

def stream_generate_reply(prompt, temperature=0.7, max_tokens=200):
    if _model is None:
        for part in pseudo_stream(prompt,temperature,max_tokens):
            yield part
    else:
        text=_model.generate(prompt,temp=temperature,max_tokens=max_tokens)
        for token in text.split():
            yield token + " "
