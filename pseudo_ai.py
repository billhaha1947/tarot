import random, time, json

TAROT_78 = [
    # 22 Major Arcana
    "0. The Fool","I. The Magician","II. The High Priestess","III. The Empress","IV. The Emperor",
    "V. The Hierophant","VI. The Lovers","VII. The Chariot","VIII. Strength","IX. The Hermit",
    "X. Wheel of Fortune","XI. Justice","XII. The Hanged Man","XIII. Death","XIV. Temperance",
    "XV. The Devil","XVI. The Tower","XVII. The Star","XVIII. The Moon","XIX. The Sun",
    "XX. Judgement","XXI. The World",

    # 56 Minor Arcana – 4 suits đầy đủ 1→10 + Court (Page, Knight, Queen, King)
    *[f"Wands {n}" for n in range(1,11)], "Page of Wands","Knight of Wands","Queen of Wands","King of Wands",
    *[f"Cups {n}" for n in range(1,11)], "Page of Cups","Knight of Cups","Queen of Cups","King of Cups",
    *[f"Swords {n}" for n in range(1,11)], "Page of Swords","Knight of Swords","Queen of Swords","King of Swords",
    *[f"Pentacles {n}" for n in range(1,11)], "Page of Pentacles","Knight of Pentacles","Queen of Pentacles","King of Pentacles"
]

COLORS = ["🔮 Tím neon", "🔥 Đỏ oracle", "💎 Cyan tâm linh", "🌙 Bạc huyền bí", "🟢 Lục năng lượng"]

def generate_reply(prompt, temperature=0.7, max_tokens=200):
    card = random.choice(TAROT_78)
    lucky = random.sample(range(1,100), 3)
    pct = random.randint(40,99)
    obj = {
        "prediction": f"Thông điệp thần bí dành cho bạn về: {prompt[:50]}...",
        "tarot_card": card,
        "lucky_numbers": lucky,
        "luck_pct": pct,
        "advice": "Giữ cân bằng nội tâm, quyết định bằng lý trí & trái tim.",
        "emoji": random.choice(["🔮","✨","🌙","🔥","💫","🧿"]),
        "color": random.choice(COLORS)
    }
    return json.dumps(obj, ensure_ascii=False)

def stream_generate_reply(prompt, temperature=0.7, max_tokens=200):
    base = json.loads(generate_reply(prompt))
    text_stream = [
        f"🔮 Rút lá: {base['tarot_card']}\n",
        "✨ Đang luận giải thông điệp...\n",
        f"{base['prediction']}\n",
        f"🎯 May mắn: {base['luck_pct']}%\n",
        f"🎲 Số tài lộc: {base['lucky_numbers']}\n",
        f"💡 Lời khuyên: {base['advice']}\n",
        f"🎨 Năng lượng màu: {base['color']} {base['emoji']}"
    ]
    for chunk in text_stream:
        time.sleep(0.3)
        for char in chunk:
            yield char
