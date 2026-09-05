import json
import emoji
import re
from pathlib import Path

def clean_text(text: str) -> str:
    # r = raw string

    text = emoji.replace_emoji(text, replace="")

    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)

    # punctuation fix
    text = re.sub(r"([!?])\1+", r"\1", text)
    text = re.sub(r"[!?]{2,}", lambda m: m.group(0)[-1], text)

    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text

def clean_reviews(input_path: str, output_dir: str = "clean_data") -> str:
    input_file = Path(input_path)
    output_path = Path(output_dir) / input_file.name

    with input_file.open("r", encoding="utf-8") as file:
        reviews = json.load(file)

    cleaned_reviews = [clean_text(review) for review in reviews]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(cleaned_reviews, file, indent=2, ensure_ascii=False)

    return str(output_path)

if __name__ == "__main__":
    input_file = Path("data/75080_law_firm.json")
    output_file = clean_reviews(input_file)
    print(f"Cleaned reviews saved to {output_file}")