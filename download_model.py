from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

model.save("./src/models/all-MiniLM-L6-v2")

print("Saved successfully")