import json
import re
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/pdfs/GS_P2_Part_10_Conclusion_and_Supplements.pdf"
OUTPUT_FILE = "supplement_topicwise_chunks.json"

BOOK_NAME = "God Speaks"
PART_NAME = "Supplement"

TOPICS = [
    "Impressioned Consciousness",
    "Practical Mysticism",
    "The First Plane",
    "The Second Plane",
    "The Third Plane",
    "The Stage Between the Third and Fourth Planes",
    "Pilgrim of the Mental Sphere",
    "The Sixth Plane",
    "Gnosis of the Sixth Plane",
    "The Seventh Plane",
    "Different Types of Miracles",
    "Kinds of Powers",
    "Meditation",
    "The Divine Theme by Meher Baba",
    "The Five Spheres Described by Meher Baba",
    "The Types of Conviction and of Knowledge",
    "Paramatma Is Infinite and Everything",
    "Five Spiritual Facts",
    "Real Birth and Real Death",
    "Fana and Fana-Fillah",
    "The Sufi Conception of Fana and Baqa",
    "Involution of Consciousness",
    "Five Algebraic Definitions",
    "The Four Types of Mukti or Liberation",
    "A Summary of the Four Types of Mukti",
    "Signs of Perfection",
    "Hal and Muqam",
    "Advent of the Avatar",
    "Gnosis of the Seventh Plane",
    "The Avatar and the Sadguru",
    "Action and Inaction",
    "Meher Baba on the Hierarchy",
    "Advent of God as Avatar",
    "Tauhid or the Unitary State of God",
    "Maya",
    "Meher Baba Says",
    "The World of the Astral"
]


def load_full_text():
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    return "\n".join(page.page_content for page in pages)


def topic_to_regex(topic: str) -> str:
    """
    Converts topic into a PDF-safe regex:
    - Allows line breaks between words
    - Allows symbols (*, page numbers)
    """
    words = topic.split()
    pattern = r"\s*".join(map(re.escape, words))
    return rf"(?i){pattern}[^\n]*"


def find_topic_positions(text):
    positions = []

    for topic in TOPICS:
        pattern = topic_to_regex(topic)
        match = re.search(pattern, text)
        if match:
            positions.append((match.start(), topic))
        else:
            print(f"⚠️ Topic not found: {topic}")

    positions.sort(key=lambda x: x[0])
    return positions


def split_into_topic_chunks(text):
    positions = find_topic_positions(text)
    chunks = []

    for i, (start, topic) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        chunk_text = text[start:end].strip()

        chunks.append({
            "id": f"gs_supplement_{i+1}",
            "book": BOOK_NAME,
            "part": PART_NAME,
            "topic": topic,
            "text": chunk_text,
            "completeness": "FULL"
        })

    return chunks


def main():
    full_text = load_full_text()
    chunks = split_into_topic_chunks(full_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print("✅ Supplement chunking complete")
    print(f"📦 Output file: {OUTPUT_FILE}")
    print(f"📊 Total chunks created: {len(chunks)}")


if __name__ == "__main__":
    main()
