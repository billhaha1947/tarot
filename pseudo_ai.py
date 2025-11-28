import random
import time
import json

class PseudoAI:
    def __init__(self):
        # 78 lá bài Tarot đầy đủ (22 Major Arcana + 56 Minor Arcana)
        self.tarot_cards = {
            # Major Arcana (22 lá)
            "The Fool": {"meaning": "khởi đầu mới, phiêu lưu, tiềm năng vô hạn", "color": "#FFD700", "emoji": "🃏"},
            "The Magician": {"meaning": "sức mạnh sáng tạo, kỹ năng, biểu hiện", "color": "#FF4500", "emoji": "🎩"},
            "The High Priestess": {"meaning": "trực giác, bí ẩn, tri thức tiềm thức", "color": "#4B0082", "emoji": "🌙"},
            "The Empress": {"meaning": "sinh sản, nuôi dưỡng, dư dật", "color": "#FF69B4", "emoji": "👑"},
            "The Emperor": {"meaning": "quyền lực, cấu trúc, kiểm soát", "color": "#8B0000", "emoji": "⚔️"},
            "The Hierophant": {"meaning": "truyền thống, giáo dục tâm linh, phù hợp", "color": "#FFD700", "emoji": "📿"},
            "The Lovers": {"meaning": "tình yêu, hài hòa, lựa chọn", "color": "#FF1493", "emoji": "💕"},
            "The Chariot": {"meaning": "ý chí, quyết tâm, thành công", "color": "#4169E1", "emoji": "🏇"},
            "Strength": {"meaning": "sức mạnh nội tâm, can đảm, kiên nhẫn", "color": "#FF6347", "emoji": "🦁"},
            "The Hermit": {"meaning": "tự soi xét, cô đơn, tìm kiếm chân lý", "color": "#696969", "emoji": "🕯️"},
            "Wheel of Fortune": {"meaning": "vận may, chu kỳ, số phận", "color": "#FFD700", "emoji": "🎡"},
            "Justice": {"meaning": "công bằng, chân lý, luật pháp", "color": "#4682B4", "emoji": "⚖️"},
            "The Hanged Man": {"meaning": "buông bỏ, quan điểm mới, hy sinh", "color": "#87CEEB", "emoji": "🙃"},
            "Death": {"meaning": "kết thúc, chuyển đổi, tái sinh", "color": "#000000", "emoji": "💀"},
            "Temperance": {"meaning": "cân bằng, điều độ, hài hòa", "color": "#7B68EE", "emoji": "⚗️"},
            "The Devil": {"meaning": "ràng buộc, cám dỗ, vật chất hóa", "color": "#8B0000", "emoji": "😈"},
            "The Tower": {"meaning": "thay đổi đột ngột, hỗn loạn, mặc khải", "color": "#FF4500", "emoji": "⚡"},
            "The Star": {"meaning": "hy vọng, cảm hứng, bình yên", "color": "#00BFFF", "emoji": "⭐"},
            "The Moon": {"meaning": "ảo tưởng, sợ hãi, tiềm thức", "color": "#4B0082", "emoji": "🌙"},
            "The Sun": {"meaning": "niềm vui, thành công, sức sống", "color": "#FFA500", "emoji": "☀️"},
            "Judgement": {"meaning": "phản ánh, tha thứ, nội tâm kêu gọi", "color": "#9370DB", "emoji": "📯"},
            "The World": {"meaning": "hoàn thành, thành tựu, trọn vẹn", "color": "#32CD32", "emoji": "🌍"},
            
            # Wands (Gậy) - 14 lá
            "Ace of Wands": {"meaning": "cơ hội mới, nguồn cảm hứng, tiềm năng", "color": "#FF6347", "emoji": "🔥"},
            "Two of Wands": {"meaning": "lập kế hoạch, quyết định, tiến bộ", "color": "#FF7F50", "emoji": "🗺️"},
            "Three of Wands": {"meaning": "mở rộng, tầm nhìn xa, tiên đoán", "color": "#FF8C00", "emoji": "🔭"},
            "Four of Wands": {"meaning": "kỷ niệm, hài hòa, ổn định", "color": "#FFA500", "emoji": "🎉"},
            "Five of Wands": {"meaning": "xung đột, cạnh tranh, căng thẳng", "color": "#FF4500", "emoji": "⚔️"},
            "Six of Wands": {"meaning": "chiến thắng, công nhận, thành công", "color": "#FFD700", "emoji": "🏆"},
            "Seven of Wands": {"meaning": "thách thức, kiên trì, bảo vệ", "color": "#FF6347", "emoji": "🛡️"},
            "Eight of Wands": {"meaning": "hành động nhanh, tiến triển, di chuyển", "color": "#FF7F50", "emoji": "🚀"},
            "Nine of Wands": {"meaning": "kiên cường, bền bỉ, ranh giới", "color": "#CD853F", "emoji": "🏔️"},
            "Ten of Wands": {"meaning": "gánh nặng, trách nhiệm, căng thẳng", "color": "#8B4513", "emoji": "⚖️"},
            "Page of Wands": {"meaning": "nhiệt tình, khám phá, tin tức", "color": "#FF8C00", "emoji": "📜"},
            "Knight of Wands": {"meaning": "hành động, phiêu lưu, năng lượng", "color": "#FF4500", "emoji": "🐎"},
            "Queen of Wands": {"meaning": "tự tin, quyến rũ, độc lập", "color": "#FF6347", "emoji": "👸"},
            "King of Wands": {"meaning": "lãnh đạo, tầm nhìn, doanh nhân", "color": "#8B0000", "emoji": "🤴"},
            
            # Cups (Chén) - 14 lá
            "Ace of Cups": {"meaning": "tình yêu mới, trực giác, sáng tạo", "color": "#00BFFF", "emoji": "💧"},
            "Two of Cups": {"meaning": "quan hệ đối tác, hòa hợp, hợp nhất", "color": "#1E90FF", "emoji": "💑"},
            "Three of Cups": {"meaning": "kỷ niệm, bạn bè, cộng đồng", "color": "#4169E1", "emoji": "🎊"},
            "Four of Cups": {"meaning": "trầm tư, bất mãn, nội tâm", "color": "#6495ED", "emoji": "🤔"},
            "Five of Cups": {"meaning": "mất mát, hối tiếc, bi quan", "color": "#4682B4", "emoji": "😢"},
            "Six of Cups": {"meaning": "hoài niệm, ngây thơ, quá khứ", "color": "#87CEEB", "emoji": "🎠"},
            "Seven of Cups": {"meaning": "lựa chọn, ảo tưởng, mơ mộng", "color": "#B0E0E6", "emoji": "☁️"},
            "Eight of Cups": {"meaning": "từ bỏ, tìm kiếm, rời xa", "color": "#5F9EA0", "emoji": "🚶"},
            "Nine of Cups": {"meaning": "mãn nguyện, hạnh phúc, thành tựu", "color": "#00CED1", "emoji": "🌟"},
            "Ten of Cups": {"meaning": "hài hòa, hạnh phúc gia đình, trọn vẹn", "color": "#20B2AA", "emoji": "🏡"},
            "Page of Cups": {"meaning": "sáng tạo, trực giác, tin tức cảm xúc", "color": "#48D1CC", "emoji": "🐠"},
            "Knight of Cups": {"meaning": "lãng mạn, quyến rũ, theo đuổi lý tưởng", "color": "#40E0D0", "emoji": "🦄"},
            "Queen of Cups": {"meaning": "nuôi dưỡng, đồng cảm, trực giác", "color": "#00CED1", "emoji": "🧜‍♀️"},
            "King of Cups": {"meaning": "kiểm soát cảm xúc, từ bi, trưởng thành", "color": "#008B8B", "emoji": "🧙‍♂️"},
            
            # Swords (Kiếm) - 14 lá
            "Ace of Swords": {"meaning": "rõ ràng, đột phá, chân lý", "color": "#C0C0C0", "emoji": "⚔️"},
            "Two of Swords": {"meaning": "bế tắc, quyết định khó, cân bằng", "color": "#A9A9A9", "emoji": "🤷"},
            "Three of Swords": {"meaning": "đau khổ, phản bội, tổn thương", "color": "#808080", "emoji": "💔"},
            "Four of Swords": {"meaning": "nghỉ ngơi, hồi phục, trầm tư", "color": "#D3D3D3", "emoji": "🛏️"},
            "Five of Swords": {"meaning": "xung đột, thất bại, tự trọng", "color": "#696969", "emoji": "⚡"},
            "Six of Swords": {"meaning": "chuyển tiếp, di chuyển, phục hồi", "color": "#B0C4DE", "emoji": "⛵"},
            "Seven of Swords": {"meaning": "lừa dối, chiến lược, lén lút", "color": "#778899", "emoji": "🦊"},
            "Eight of Swords": {"meaning": "hạn chế, bẫy tự đặt, nạn nhân", "color": "#708090", "emoji": "🕸️"},
            "Nine of Swords": {"meaning": "lo lắng, ác mộng, sợ hãi", "color": "#2F4F4F", "emoji": "😰"},
            "Ten of Swords": {"meaning": "kết thúc đau đớn, phản bội, đáy", "color": "#000000", "emoji": "🗡️"},
            "Page of Swords": {"meaning": "tò mò, cảnh giác, tin tức", "color": "#B0C4DE", "emoji": "🔍"},
            "Knight of Swords": {"meaning": "hành động, sôi nổi, trực tiếp", "color": "#4682B4", "emoji": "🏇"},
            "Queen of Swords": {"meaning": "trí tuệ, độc lập, rõ ràng", "color": "#87CEEB", "emoji": "👩‍⚖️"},
            "King of Swords": {"meaning": "quyền lực trí tuệ, chân lý, đạo đức", "color": "#1E90FF", "emoji": "🧑‍⚖️"},
            
            # Pentacles (Đồng tiền) - 14 lá
            "Ace of Pentacles": {"meaning": "cơ hội mới, thịnh vượng, biểu hiện", "color": "#FFD700", "emoji": "💰"},
            "Two of Pentacles": {"meaning": "cân bằng, thích nghi, thời gian", "color": "#DAA520", "emoji": "🎭"},
            "Three of Pentacles": {"meaning": "hợp tác, kỹ năng, chất lượng", "color": "#B8860B", "emoji": "🏗️"},
            "Four of Pentacles": {"meaning": "kiểm soát, an toàn, bảo thủ", "color": "#CD853F", "emoji": "🔒"},
            "Five of Pentacles": {"meaning": "khó khăn, mất mát, nghèo khổ", "color": "#8B4513", "emoji": "❄️"},
            "Six of Pentacles": {"meaning": "hào phóng, từ thiện, chia sẻ", "color": "#DEB887", "emoji": "🤝"},
            "Seven of Pentacles": {"meaning": "đánh giá, kiên nhẫn, đầu tư dài hạn", "color": "#F4A460", "emoji": "🌱"},
            "Eight of Pentacles": {"meaning": "thủ công, cống hiến, kỹ năng", "color": "#D2691E", "emoji": "🔨"},
            "Nine of Pentacles": {"meaning": "độc lập, sang trọng, tự đủ", "color": "#FFD700", "emoji": "🦚"},
            "Ten of Pentacles": {"meaning": "di sản, gia đình, tài sản", "color": "#B8860B", "emoji": "🏰"},
            "Page of Pentacles": {"meaning": "học tập, cơ hội, tham vọng", "color": "#F0E68C", "emoji": "📚"},
            "Knight of Pentacles": {"meaning": "trách nhiệm, chăm chỉ, đáng tin", "color": "#BDB76B", "emoji": "🐂"},
            "Queen of Pentacles": {"meaning": "thực tế, nuôi dưỡng, sung túc", "color": "#DAA520", "emoji": "🌻"},
            "King of Pentacles": {"meaning": "thịnh vượng, an ninh, lãnh đạo", "color": "#B8860B", "emoji": "🦁"}
        }
        
        self.response_templates = [
            "Lá bài {card} xuất hiện cho bạn với thông điệp về {meaning}. {advice}",
            "Vũ trụ dẫn bạn đến {card}, mang ý nghĩa {meaning}. {advice}",
            "{card} hiện ra trong số phận của bạn, báo hiệu {meaning}. {advice}",
            "Các vì sao cho thấy {card}, đại diện cho {meaning}. {advice}",
            "Oracle nhìn thấy {card} trong tương lai của bạn, phản ánh {meaning}. {advice}"
        ]
        
        self.advice_templates = [
            "Hãy tin vào trực giác của bạn và tiến về phía trước với sự tự tin.",
            "Đây là thời điểm tốt để suy ngẫm và lắng nghe nội tâm.",
            "Hành động với sự khôn ngoan và kiên nhẫn sẽ mang lại kết quả tốt.",
            "Mở rộng tâm trí và đón nhận những cơ hội mới.",
            "Cân bằng giữa lý trí và cảm xúc sẽ dẫn đường cho bạn.",
            "Hãy dũng cảm đối mặt với thử thách, bạn mạnh mẽ hơn bạn nghĩ.",
            "Tập trung vào những gì thực sự quan trọng trong cuộc sống.",
            "Tin tưởng vào quá trình và cho phép mọi thứ diễn ra tự nhiên.",
            "Kết nối với những người xung quanh và chia sẻ năng lượng tích cực.",
            "Đây là lúc để thực hiện những thay đổi mà bạn mong muốn."
        ]
    
    def generate_oracle_data(self, prompt):
        """Tạo dữ liệu Oracle với lá bài Tarot"""
        card_name = random.choice(list(self.tarot_cards.keys()))
        card_info = self.tarot_cards[card_name]
        
        # Tạo số may mắn
        lucky_numbers = sorted(random.sample(range(1, 79), 6))
        
        # Tính toán luck_pct dựa trên context
        base_luck = random.randint(50, 95)
        if any(word in prompt.lower() for word in ['tình yêu', 'love', 'yêu']):
            base_luck = random.randint(60, 98)
        elif any(word in prompt.lower() for word in ['tiền', 'money', 'tài chính', 'công việc', 'career']):
            base_luck = random.randint(55, 90)
        
        oracle_data = {
            'prediction': f"Năng lượng của {card_name} đang ảnh hưởng đến con đường của bạn",
            'tarot_card': card_name,
            'lucky_numbers': lucky_numbers,
            'luck_pct': base_luck,
            'advice': random.choice(self.advice_templates),
            'emoji': card_info['emoji'],
            'color': card_info['color']
        }
        
        return oracle_data
    
    def generate_reply(self, prompt, temperature=0.8, max_tokens=500):
        """Tạo câu trả lời hoàn chỉnh"""
        oracle_data = self.generate_oracle_data(prompt)
        
        card_name = oracle_data['tarot_card']
        card_info = self.tarot_cards[card_name]
        
        template = random.choice(self.response_templates)
        response = template.format(
            card=card_name,
            meaning=card_info['meaning'],
            advice=oracle_data['advice']
        )
        
        # Thêm thông tin chi tiết dựa trên prompt
        if 'tương lai' in prompt.lower() or 'future' in prompt.lower():
            response += f" Trong tương lai gần, bạn sẽ gặp những cơ hội mới liên quan đến {card_info['meaning']}."
        
        if 'tình yêu' in prompt.lower() or 'love' in prompt.lower():
            response += f" Về mặt tình cảm, năng lượng của {card_name} cho thấy sự phát triển tích cực."
        
        if 'công việc' in prompt.lower() or 'career' in prompt.lower() or 'work' in prompt.lower():
            response += f" Trong sự nghiệp, {card_name} báo hiệu thời kỳ quan trọng cần sự {card_info['meaning']}."
        
        return response, oracle_data
    
    def stream_generate_reply(self, prompt, temperature=0.8, max_tokens=500):
        """Tạo câu trả lời streaming (từng token)"""
        response, oracle_data = self.generate_reply(prompt, temperature, max_tokens)
        
        # Streaming từng ký tự với delay ngẫu nhiên
        words = response.split(' ')
        for i, word in enumerate(words):
            time.sleep(random.uniform(0.02, 0.08))  # Delay tự nhiên
            yield {
                'type': 'token',
                'content': word + (' ' if i < len(words) - 1 else '')
            }
        
        # Gửi oracle data cuối cùng
        yield {
            'type': 'oracle',
            'data': oracle_data
        }
