import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_PATH = os.path.join("models", MODEL_NAME)

if __name__ == "__main__":
    print(f"Downloading model: {MODEL_NAME} to {MODEL_PATH}")
    os.makedirs(MODEL_PATH, exist_ok=True)
    SentenceTransformer(MODEL_NAME).save(MODEL_PATH)
    print("Model download complete.")