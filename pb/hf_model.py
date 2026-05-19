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
        # Check CUDA availability
        self.cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {self.cuda_available}")
        if self.cuda_available:
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
            self.device_str = "cuda"
        else:
            print("WARNING: CUDA is not available. Falling back to CPU. This will be very slow!")
            self.device_str = "cpu"
            
        print(f"Loading HuggingFace model {model_name} to VRAM...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Set configuration for model loading
        if self.cuda_available:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32
            )
        
        # Build text generation pipeline
        # When device_map="auto" is used, we do not pass device parameter to pipeline
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        print("Model loaded successfully!")

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
