import time
import random

TAROT_CARDS = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Lovers", "The Chariot", "Strength",
    "The Hermit", "Wheel of Fortune", "Justice", "Death",
    "The Tower", "The Star", "The Sun", "The Moon"
]

def stream_pseudo_ai(prompt, max_tokens=120):
    text = f"🔮 Oracle trả lời cho truy vấn: '{prompt[:40]}...'\n\n"
    card = random.choice(TAROT_CARDS)
    luck = random.randint(45, 99)
    nums = random.sample(range(1, 99), 4)
    advice = random.choice([
        "Hãy tin trực giác của bạn",
        "Cơ hội đang đến gần, chuẩn bị đi",
        "Không phải mọi thứ đều như vẻ bề ngoài",
        "Đây là lúc thay đổi lớn trong bạn"
    ])
    structured = {
        "prediction": text.strip(),
        "tarot_card": card,
        "lucky_numbers": nums,
        "luck_pct": luck,
        "advice": advice,
        "emoji": "🔮",
        "color": random.choice(["neon-purple","neon-blue","neon-pink"])
    }

    out = ""
    for ch in str(structured):
        out += ch
        yield ch
        time.sleep(0.03)
        if len(out.split()) > max_tokens:
            break
