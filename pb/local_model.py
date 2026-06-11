import ollama
import concurrent.futures
import threading

class LocalGeneration:
    def __init__(self, text):
        self.text = text

class LocalResult:
    def __init__(self, text):
        self.generations = [LocalGeneration(text)]
    
    def __getitem__(self, index):
        return self.generations[index]
    
    def __len__(self):
        return 1

class LocalClient:
    _semaphore = threading.Semaphore(2)  # Limit to 2 concurrent Ollama calls
    
    def __init__(self, model_name="qwen2.5:1.5b"):
        self.model_name = model_name

    def generate(self, prompt, **kwargs):
        # Map some common kwargs if needed, though Ollama uses different ones
        # For now, just focus on prompt and model
        options = {}
        if 'temperature' in kwargs:
            options['temperature'] = kwargs['temperature']
        
        if 'num_predict' in kwargs:
            options['num_predict'] = kwargs['num_predict']
            
        with self._semaphore:
            response = ollama.generate(model=self.model_name, prompt=prompt, options=options)
        return LocalResult(response['response'])

    def batch_generate(self, prompts, **kwargs):
        # For local models, running in parallel might be too much for some systems,
        # but the project seems to expect it. We can use a small number of workers.
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_prompt = {executor.submit(self.generate, prompt, **kwargs): prompt for prompt in prompts}
            # We need to maintain the order of prompts
            prompt_to_result = {}
            for future in concurrent.futures.as_completed(future_to_prompt):
                prompt = future_to_prompt[future]
                try:
                    prompt_to_result[prompt] = future.result()
                except Exception as e:
                    print(f"Error generating for prompt: {e}")
                    prompt_to_result[prompt] = LocalResult("")
            
            # Reconstruct in order
            for prompt in prompts:
                results.append(prompt_to_result[prompt])
        
        return results
