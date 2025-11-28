import random, time, json

# 78 lá Tarot
TAROT_CARDS = [
    # Major Arcana
    "The Fool","The Magician","The High Priestess","The Empress","The Emperor",
    "The Hierophant","The Lovers","The Chariot","Strength","The Hermit",
    "Wheel of Fortune","Justice","The Hanged Man","Death","Temperance",
    "The Devil","The Tower","The Star","The Moon","The Sun","Judgement","The World",
    # Wands
    "Ace of Wands","Two of Wands","Three of Wands","Four of Wands","Five of Wands","Six of Wands",
    "Seven of Wands","Eight of Wands","Nine of Wands","Ten of Wands","Page of Wands",
    "Knight of Wands","Queen of Wands","King of Wands",
    # Cups
    "Ace of Cups","Two of Cups","Three of Cups","Four of Cups","Five of Cups","Six of Cups",
    "Seven of Cups","Eight of Cups","Nine of Cups","Ten of Cups","Page of Cups",
    "Knight of Cups","Queen of Cups","King of Cups",
    # Swords
    "Ace of Swords","Two of Swords","Three of Swords","Four of Swords","Five of Swords","Six of Swords",
    "Seven of Swords","Eight of Swords","Nine of Swords","Ten of Swords","Page of Swords",
    "Knight of Swords","Queen of Swords","King of Swords",
    # Pentacles
    "Ace of Pentacles","Two of Pentacles","Three of Pentacles","Four of Pentacles","Five of Pentacles",
    "Six of Pentacles","Seven of Pentacles","Eight of Pentacles","Nine of Pentacles","Ten of Pentacles",
    "Page of Pentacles","Knight of Pentacles","Queen of Pentacles","King of Pentacles"
]

ADVICE_TEMPLATES = [
    "Hãy tin vào con đường đang đi.",
    "Buông bỏ để tái sinh.",
    "Cân bằng để làm chủ vận mệnh.",
    "Can đảm đối mặt thử thách.",
    "Giữ kỷ luật và tầm nhìn."
]

COLORS = ["#00f2ff","#8a2be2","#ff00d4","#39ff14","#ffd700"]
EMOJIS = ["🔮","🃏","✨","🌙","🔥","💎","🧿"]

SYMBOL_KEY = {
    "thiên thần": "Thông điệp bảo hộ tâm linh.",
    "nước": "Dòng chảy cảm xúc và tiềm thức.",
    "lửa": "Đam mê và năng lượng bùng nổ.",
    "đồng xu": "Vật chất và giá trị.",
    "thanh kiếm": "Lý trí và quyết định."
}

def decode_symbols(prompt):
    f=[]
    low=prompt.lower()
    for k,v in SYMBOL_KEY.items():
        if k in low:
            f.append({"symbol":k,"meaning":v})
    return f

def draw_three():
    a=random.sample(TAROT_CARDS,3)
    return {"past":a[0],"present":a[1],"future":a[2]}

def stream_generate_reply(prompt, temperature=0.7, max_tokens=120):
    words = ("🔮 Oracle trả lời: " + random.choice(ADVICE_TEMPLATES)).split()
    for w in words[:max_tokens]:
        time.sleep(0.04 + random.random()*0.015)
        yield w + " "

    card = random.choice(TAROT_CARDS)
    oracle = {
        "prediction": random.choice(["Một chuyển biến lớn sắp đến","Cơ hội bất ngờ xuất hiện",
                                     "Thử thách mở ra sức mạnh tiềm ẩn"]),
        "tarot_card": card,
        "lucky_numbers": random.sample(range(1,49),4),
        "luck_pct": random.randint(60,100),
        "advice": random.choice(ADVICE_TEMPLATES),
        "emoji": random.choice(EMOJIS),
        "color": random.choice(COLORS),
        "symbols": decode_symbols(prompt),
        "three_draw": draw_three()
    }
    j=json.dumps(oracle,ensure_ascii=False)
    for ch in j:
        time.sleep(0.015 + random.random()*0.005)
        yield ch
