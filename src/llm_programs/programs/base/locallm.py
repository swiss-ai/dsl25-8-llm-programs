from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig


class LocalLM():

    def __init__(self, model_name="google/gemma-2-2b-it", load_in_8bit=True):
        self.model_name = model_name
        self.load_in_8bit = load_in_8bit
        self.model = None

    def load(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        quantization_config = BitsAndBytesConfig(load_in_8bit=self.load_in_8bit)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=quantization_config,
        )

    def __call__(self, input_text, max_new_tokens=1024):
        if self.model is None:
            self.load()
        input_ids = self.tokenizer(input_text, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids, max_new_tokens=max_new_tokens)
        prompt_length = input_ids['input_ids'].shape[1]
        new_tokens_decoded = self.tokenizer.decode(outputs[0][prompt_length:], skip_special_tokens=True)
        return new_tokens_decoded



