import json
import re
from collections import defaultdict
from langchain_community.document_loaders import PyPDFLoader

# ================= CONFIG =================

PDF_PATH = "/home/coffeee/Desktop/project/Anuvada_AI/backend/data/Life_Eternal_Book1_Book2.pdf"
OUTPUT_JSON = "life_eternal_topic_chunks.json"

AUTHOR = "Meher Baba"
COLLECTION = "Life Eternal"
COLLECTION_INFO = (
    "Life Eternal is a collection of spiritual teachings of Meher Baba, "
    "arranged by subject, in the order in which he gave them."
)

TOPIC_REGEX = re.compile(r"^\s*([A-Z][A-Z\s]{3,})\s*$")

TOPIC_DESCRIPTIONS = {
    "AGENTS": "Agents are men and women who work on the inner planes of consciousness for Perfect Masters and the Avatar.",
    "ANGELS": "Angels are beings who live in the inner planes.",
    "ARCHANGELS": "Archangels are beings who live between the sixth and seventh plane.",
    "THE ASTRAL WORLD": "The Astral World is the realm between the Gross and Subtle worlds.",
    "THE AVATAR": "The Avatar incarnates from time to time and oversees creation.",
    "CREATION": "How the universe came about.",
    "DEATH": "What happens when we die.",
    "DESTINY": "Fate versus free will.",
    "DIET": "What Meher Baba said about food.",
    "DREAMS": "Seven kinds of dreams explained by Baba.",
    "DRUGS": "Teachings on mind-altering substances.",
    "GOD-REALISATION": "The highest state of consciousness.",
    "LIBERATION": "Final freedom attained after God-realisation.",
    "LOVE": "Different kinds of love.",
    "MEDITATION": "How, when and why to meditate.",
    "MIRACLES": "Miracles and their spiritual meaning.",
    "THE PATH": "Journey through the seven planes.",
    "PERFECTION": "God-realised souls who return to help others.",
    "PRAYER": "Teachings on prayer.",
    "SANSKARAS": "Mental impressions binding the soul.",
    "SPIRITUAL HIERARCHY": "Spiritual governance of creation.",
    "SURRENDER": "Giving everything to God or to a Perfect Master."
}

# ================= LOAD PDF =================

loader = PyPDFLoader(PDF_PATH)
pages = loader.load()
text = "\n".join(p.page_content for p in pages)

# ================= EXTRACT TOPICS =================

lines = text.splitlines()
topics = defaultdict(list)
current_topic = None

for line in lines:
    match = TOPIC_REGEX.match(line.strip())
    if match:
        current_topic = match.group(1).strip()
        topics[current_topic].append(line)
    elif current_topic:
        topics[current_topic].append(line)

# ================= BUILD CHUNKS =================

chunks = []

for topic, content in topics.items():
    chunk = {
        "id": f"life_eternal_{topic.lower().replace(' ', '_')}",
        "collection": COLLECTION,
        "collection_info": COLLECTION_INFO,
        "topic": topic.title(),
        "description": TOPIC_DESCRIPTIONS.get(
            topic, "Topic-wise teachings of Meher Baba."
        ),
        "author": AUTHOR,
        "source": "Life Eternal (Merged Edition)",
        "text": "\n".join(content).strip()
    }
    chunks.append(chunk)

# ================= SAVE =================

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"✅ Created {len(chunks)} topic chunks")
print(f"📦 Output → {OUTPUT_JSON}")
