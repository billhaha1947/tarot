import os
import json
from pseudo_ai import PseudoAI

class ModelManager:
    def __init__(self):
        self.current_model = 'pseudo_tarot'
        self.temperature = 0.8
        self.max_tokens = 500
        self.gpt4all_model = None
        self.pseudo_ai = PseudoAI()
        
        # Thử load GPT4All nếu có
        self._try_load_gpt4all()
    
    def _try_load_gpt4all(self):
        """Thử load GPT4All model nếu có"""
        try:
            from gpt4all import GPT4All
            model_path = os.environ.get('GPT4ALL_MODEL_PATH', './models')
            model_name = os.environ.get('GPT4ALL_MODEL_NAME', 'mistral-7b-openorca.Q4_0.gguf')
            
            if os.path.exists(os.path.join(model_path, model_name)):
                self.gpt4all_model = GPT4All(model_name, model_path=model_path)
                self.current_model = 'gpt4all'
                print(f"✓ Loaded GPT4All model: {model_name}")
            else:
                print("✗ GPT4All model not found, using Pseudo AI")
        except ImportError:
            print("✗ GPT4All not installed, using Pseudo AI")
        except Exception as e:
            print(f"✗ Error loading GPT4All: {str(e)}, using Pseudo AI")
    
    def get_available_models(self):
        """Lấy danh sách models có sẵn"""
        models = [{
            'id': 'pseudo_tarot',
            'name': 'Pseudo Tarot AI (Built-in)',
            'description': 'AI giả lập với 78 lá bài Tarot đầy đủ'
        }]
        
        if self.gpt4all_model:
            models.append({
                'id': 'gpt4all',
                'name': 'GPT4All Local Model',
                'description': 'Mô hình AI cục bộ thực sự'
            })
        
        return models
    
    def set_model(self, model_id):
        """Đổi model hiện tại"""
        if model_id == 'gpt4all' and self.gpt4all_model:
            self.current_model = 'gpt4all'
        else:
            self.current_model = 'pseudo_tarot'
    
    def generate_reply(self, prompt, temperature=None, max_tokens=None):
        """Tạo câu trả lời hoàn chỉnh (không streaming)"""
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.current_model == 'gpt4all' and self.gpt4all_model:
            response = self.gpt4all_model.generate(
                prompt,
                temp=temp,
                max_tokens=max_tok
            )
            oracle_data = self.pseudo_ai.generate_oracle_data(prompt)
            return response, oracle_data
        else:
            return self.pseudo_ai.generate_reply(prompt, temp, max_tok)
    
    def stream_generate_reply(self, prompt, temperature=None, max_tokens=None):
        """Tạo câu trả lời streaming (token by token)"""
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.current_model == 'gpt4all' and self.gpt4all_model:
            # GPT4All streaming
            full_response = ""
            for token in self.gpt4all_model.generate(
                prompt,
                temp=temp,
                max_tokens=max_tok,
                streaming=True
            ):
                full_response += token
                yield {
                    'type': 'token',
                    'content': token
                }
            
            # Generate oracle data sau khi hoàn thành
            oracle_data = self.pseudo_ai.generate_oracle_data(prompt)
            yield {
                'type': 'oracle',
                'data': oracle_data
            }
        else:
            # Pseudo AI streaming
            for chunk in self.pseudo_ai.stream_generate_reply(prompt, temp, max_tok):
                yield chunk
