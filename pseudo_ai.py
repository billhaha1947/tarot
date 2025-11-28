import time
import random

TAROT_CARDS = [
  # Major Arcana (22)
  "The Fool","The Magician","The High Priestess","The Empress","The Emperor",
  "The Hierophant","The Lovers","The Chariot","Strength","The Hermit",
  "Wheel of Fortune","Justice","The Hanged Man","Death","Temperance","The Devil",
  "The Tower","The Star","The Moon","The Sun","Judgement","The World",
  # Wands
  "Ace of Wands","Two of Wands","Three of Wands","Four of Wands","Five of Wands",
  "Six of Wands","Seven of Wands","Eight of Wands","Nine of Wands","Ten of Wands",
  "Page of Wands","Knight of Wands","Queen of Wands","King of Wands",
  # Cups
  "Ace of Cups","Two of Cups","Three of Cups","Four of Cups","Five of Cups",
  "Six of Cups","Seven of Cups","Eight of Cups","Nine of Cups","Ten of Cups",
  "Page of Cups","Knight of Cups","Queen of Cups","King of Cups",
  # Swords
  "Ace of Swords","Two of Swords","Three of Swords","Four of Swords","Five of Swords",
  "Six of Swords","Seven of Swords","Eight of Swords","Nine of Swords","Ten of Swords",
  "Page of Swords","Knight of Swords","Queen of Swords","King of Swords",
  # Pentacles
  "Ace of Pentacles","Two of Pentacles","Three of Pentacles","Four of Pentacles","Five of Pentacles",
  "Six of Pentacles","Seven of Pentacles","Eight of Pentacles","Nine of Pentacles","Ten of Pentacles",
  "Page of Pentacles","Knight of Pentacles","Queen of Pentacles","King of Pentacles"
]

COLORS = ["Tím","Xanh neon","Đen","Bạc","Vàng glow"]

def stream_pseudo_reply(prompt, temperature=0.7, max_tokens=150):
    reply = random.choice([
        "Hãy kiên nhẫn, vận may đang gõ cửa…",
        "Một thay đổi lớn sắp xuất hiện…",
        "Hãy lắng nghe trực giác của bạn…",
        "Cơ hội đến rất nhanh nhưng cũng đi rất nhanh…",
        "Đừng sợ bóng tối, tòa tháp phải sụp để ngôi sao tỏa sáng…"
    ])

    card = random.choice(TAROT_CARDS)
    lucky = random.sample(range(1,100), 3)
    luck_pct = random.randint(50,99)

    structured = {
        "prediction": reply,
        "tarot_card": card,
        "lucky_numbers": lucky,
        "luck_pct": f"{luck_pct}%",
        "advice": "Tin vào dòng chảy, hành động nhưng đừng cưỡng cầu.",
        "emoji": random.choice(["🔮","✨","🌙","🔥","⚔️","💰"]),
        "color": random.choice(COLORS)
    }

    out = structured["prediction"]
    for ch in out[:max_tokens]:
        time.sleep(0.03)
        yield ch

    yield "\n" + str(structured)
