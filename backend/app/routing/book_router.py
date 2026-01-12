CONCEPTUAL_TOPICS = [
    "sanskara", "sanskaras", "creation",
    "evolution", "involution",
    "consciousness", "soul", "ego",
    "mind", "maya", "gross", "subtle",
    "mental", "avatar", "god realization"
]

def decide_book(question: str):
    q = question.lower()
    for topic in CONCEPTUAL_TOPICS:
        if topic in q:
            return "God Speaks"
    return "Discourses"
