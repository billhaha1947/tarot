import time, random

TAROT_CARDS = [
    # MAJOR (22)
    "The Fool","The Magician","The High Priestess","The Empress","The Emperor",
    "The Hierophant","The Lovers","The Chariot","Strength","The Hermit",
    "Wheel of Fortune","Justice","The Hanged Man","Death","Temperance","The Devil",
    "The Tower","The Star","The Moon","The Sun","Judgement","The World",

    # WANDS (14)
    "Ace of Wands","Two of Wands","Three of Wands","Four of Wands","Five of Wands",
    "Six of Wands","Seven of Wands","Eight of Wands","Nine of Wands","Ten of Wands",
    "Page of Wands","Knight of Wands","Queen of Wands","King of Wands",

    # CUPS (14)
    "Ace of Cups","Two of Cups","Three of Cups","Four of Cups","Five of Cups",
    "Six of Cups","Seven of Cups","Eight of Cups","Nine of Cups","Ten of Cups",
    "Page of Cups","Knight of Cups","Queen of Cups","King of Cups",

    # SWORDS (14)
    "Ace of Swords","Two of Swords","Three of Swords","Four of Swords","Five of Swords",
    "Six of Swords","Seven of Swords","Eight of Swords","Nine of Swords","Ten of Swords",
    "Page of Swords","Knight of Swords","Queen of Swords","King of Swords",

    # PENTACLES (14)
    "Ace of Pentacles","Two of Pentacles","Three of Pentacles","Four of Pentacles","Five of Pentacles",
    "Six of Pentacles","Seven of Pentacles","Eight of Pentacles","Nine of Pentacles","Ten of Pentacles",
    "Page of Pentacles","Knight of Pentacles","Queen of Pentacles","King of Pentacles"
]

EMOJIS = ["🔮","✨","🌙","🔥","⚔️","💰","🌿"]
COLORS = ["Tím neon","Xanh aqua glow","Vàng solar","Bạc shimmer","Đỏ inferno"]

def stream_generate_reply(prompt, temperature=0.7, max_tokens=150):
    template = random.choice([
        "Oracle thì thầm: bạn sắp gặp bước ngoặt lớn… ",
        "Lá bài tiết lộ: thời cơ đang đến rất gần… ",
        "Vũ trụ mách bảo: hãy tin vào trực giác… ",
        "Thông điệp huyền bí: mọi chuyển động đều có lý do… ",
        "Dự đoán ánh trăng: con đường mới mở ra… "
    ])
    for ch in template:
        time.sleep(0.025)
        yield ch
    oracle_json = {
        "emoji": random.choice(EMOJIS),
        "prediction": template.strip(),
        "tarot_card": random.choice(TAROT_CARDS),
        "lucky_numbers": random.sample(range(1,50), 4),
        "luck_pct": random.randint(50,99),
        "advice": "Đừng sợ thay đổi. Hãy hành động với niềm tin.",
        "color": random.choice(COLORS)
    }
    time.sleep(0.05)
    yield "\n"
    yield json.dumps(oracle_json, ensure_ascii=False)
    yield "\n"
    convo = draw_three()
    time.sleep(0.02)
    yield json.dumps({"three_draw": convo}, ensure_ascii=False)
    yield "\n"
    symbols = decode_symbols(prompt)
    time.sleep(0.02)
    yield json.dumps({"symbol_decode": symbols}, ensure_ascii=False)

def draw_three():
    card1 = random.choice(TAROT_CARDS)
    card2 = random.choice(TAROT_CARDS)
    card3 = random.choice(TAROT_CARDS)
    return [
        {"position":"past","card":card1,"meaning":"Dư âm bài học cũ, nền tảng hình thành."},
        {"position":"present","card":card2,"meaning":"Trọng tâm hiện tại, năng lượng đang chi phối."},
        {"position":"future","card":card3,"meaning":"Xu hướng sắp xảy ra, gợi ý con đường mới."}
    ]

def decode_symbols(text):
    syms = ["Nước","Lửa","Khí","Đất","Mặt Trăng","Mặt Trời","Tòa Tháp","Ngôi Sao","Thanh Kiếm","Tiền Xu","Hoa Hồng","Rắn","Thiên Thần"]
    found = [s for s in syms if s.lower() in text.lower()]
    if not found:
        return ["Không có biểu tượng rõ ràng – tập trung vào cảm xúc chung."]
    return [f"Biểu tượng '{s}': hàm ý năng lượng {random.randint(1,5)}/5 trong bối cảnh." for s in found]
