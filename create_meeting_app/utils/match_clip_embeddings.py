import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def match_summary_to_screenshots(summary_sentences, screenshot_paths):
    print("🔍 Matching summaries to screenshots using CLIP...")

    matches = {}

    if not summary_sentences or not screenshot_paths:
        print("⚠️ No summaries or screenshots to process.")
        return matches

    print(f"📝 Sentences: {len(summary_sentences)} | 🖼️ Screenshots: {len(screenshot_paths)}")

    # 1. Encode summary
    inputs = processor(text=summary_sentences, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        text_embeddings = model.get_text_features(**inputs)
    print("✅ Text embeddings created")

    # 2. Encode screenshots
    images = [Image.open(path).convert("RGB") for path in screenshot_paths]
    image_inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        image_embeddings = model.get_image_features(**image_inputs)
    print("✅ Image embeddings created")

    # 3. Normalize
    text_embeddings = text_embeddings / text_embeddings.norm(p=2, dim=-1, keepdim=True)
    image_embeddings = image_embeddings / image_embeddings.norm(p=2, dim=-1, keepdim=True)

    # 4. Compute similarity
    similarity = torch.matmul(text_embeddings, image_embeddings.T)

    for i, sentence in enumerate(summary_sentences):
        best_match_index = similarity[i].argmax().item()
        matches[sentence] = screenshot_paths[best_match_index]
        print(f"🔗 Matched: \"{sentence}\" --> {screenshot_paths[best_match_index]}")

    return matches
