import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class HFGeneration:
    def __init__(self, text):
        self.text = text

class HFResult:
    def __init__(self, text):
        self.generations = [HFGeneration(text)]
    
    def __getitem__(self, index):
        return self.generations[index]
    
    def __len__(self):
        return 1

class HFClient:
    def __init__(self, model_name="Qwen/Qwen2.5-1.5B-Instruct", device="cuda"):
        print(f"Loading HuggingFace model {model_name} to VRAM...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set pad token to eos token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto" if device == "cuda" and torch.cuda.is_available() else None
        )
        
        # Build text generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        print("Model loaded successfully into VRAM!")

    def generate(self, prompt, **kwargs):
        temperature = kwargs.get('temperature', 0.7)
        max_new_tokens = kwargs.get('max_new_tokens', 256)
        pad_token_id = self.tokenizer.eos_token_id
        do_sample = temperature > 0.0
        
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature if do_sample else None,
            pad_token_id=pad_token_id,
            return_full_text=False
        )
        
        generated_text = outputs[0]['generated_text']
        return HFResult(generated_text)

    def batch_generate(self, prompts, **kwargs):
        temperature = kwargs.get('temperature', 0.7)
        max_new_tokens = kwargs.get('max_new_tokens', 256)
        pad_token_id = self.tokenizer.eos_token_id
        do_sample = temperature > 0.0
        
        # Kaggle GPUs (T4 or P100) can handle batch size of 8 or 16 easily for 1.5B/3B models
        outputs = self.generator(
            prompts,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature if do_sample else None,
            pad_token_id=pad_token_id,
            return_full_text=False,
            batch_size=8
        )
        
        results = []
        for out in outputs:
            if isinstance(out, list):
                generated_text = out[0]['generated_text']
            else:
                generated_text = out['generated_text']
            results.append(HFResult(generated_text))
            
        return results
