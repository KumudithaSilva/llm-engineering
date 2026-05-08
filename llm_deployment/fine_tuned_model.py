import modal
from modal import Image, Volume

# Modal app setup
app = modal.App("stream_price")
image = Image.debian_slim().pip_install(
    "torch", "transformers", "bitsandbytes", "accelerate", "peft"
)
secrets = [modal.Secret.from_name("huggingface-secret")]

# Model and deployment configuration
GPU = "T4"

BASE_MODEL = "meta-llama/Llama-3.2-3B"

PROJECT_NAME = "stream_price"
HF_USER = "KumudithaSilva"
RUN_NAME = "fine-tuning-2026-04-30_11.01.12"
REVISION = "de4a39b1ae7666620aa49a6bff90a97190b098fd"

PROJECT_RUN_NAME = f"{PROJECT_NAME}-{RUN_NAME}"
FINETUNED_MODEL = f"{HF_USER}/{PROJECT_RUN_NAME}"

CACHE_DIR = "/cache"


MIN_CONTAINERS = 0

PREFIX = "Price is $"
QUESTION = "How much this stream game cost to the nearest dollar?"

# Set up a shared volume
hf_cache_volume = Volume.from_name("hf-hub-cache", create_if_missing=True)


# Define the Modal class for the fine-tuned model deployment
@app.cls(
    image=image.env({"HF_HUB_CACHE": CACHE_DIR}),
    secrets=secrets,
    gpu=GPU,
    timeout=1800,
    min_containers=MIN_CONTAINERS,
    volumes={CACHE_DIR: hf_cache_volume},
)
class StreamPricer:
    @modal.enter()
    def setup(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import PeftModel

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )

        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        self.base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL, quantization_config=quant_config, device_map="auto"
        )
        self.fine_tuned_model = PeftModel.from_pretrained(
            self.base_model, FINETUNED_MODEL, revision=REVISION
        )

    @modal.method()
    def price(self, description: str) -> float:
        import re
        import torch
        from transformers import set_seed

        set_seed(42)

        prompt = f"{QUESTION}\n\n{description}\n\n{PREFIX}"

        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to("cuda")
        prompt_len = inputs.shape[1]

        with torch.no_grad():
            outputs = self.fine_tuned_model.generate(inputs)

        generated_tokens = outputs[0][prompt_len:]
        result = self.tokenizer.decode(
            generated_tokens, skip_special_tokens=True
        ).strip()

        print("Generated:", result)

        result = result.replace("$", "").strip()
        return float(result)
