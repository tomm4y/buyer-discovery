import json
import emoji
import re
from pathlib import Path

def clean_reviews(reviews: list[dict], output_dir: str, batch_name: str) -> str:
    
    output_path = Path(output_dir) / f"{batch_name}.json"
    
    cleaned_reviews = []
    for review in reviews:
        text = review["text"]
        text = emoji.replace_emoji(text, replace="")

        text = re.sub(r"[‘’]", "'", text)
        text = re.sub(r"[“”]", '"', text)

        # punctuation fix
        text = re.sub(r"([!?])\1+", r"\1", text)
        text = re.sub(r"[!?]{2,}", lambda m: m.group(0)[-1], text)

        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        cleaned_reviews.append({"place_id": review["place_id"], "text": text})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(cleaned_reviews, file, indent=2, ensure_ascii=False)

    return str(output_path)

if __name__ == "__main__":
    output_file = clean_reviews("data/75080_law_firm.json", "cleaned_data")
    print(f"Cleaned reviews saved to {output_file}")