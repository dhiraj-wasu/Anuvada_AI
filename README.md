

# 🧠 Anuvada — A Philosophy-Aware Retrieval & Guidance System

**Anuvada** is a philosophy-aware AI system designed to **faithfully retrieve and explain spiritual teachings without altering their original meaning**.
Unlike standard Retrieval-Augmented Generation (RAG) systems, Anuvada introduces **intent-aware source routing** and **quote-grounded response generation** to preserve doctrinal integrity and eliminate hallucination.

---

## ✨ Why Anuvada Is Different

Most RAG systems treat all documents as interchangeable vectors.
Anuvada does **not**.

It understands that **different kinds of human questions require different kinds of philosophical sources** — and enforces that separation at the system level.

---

## 📚 Knowledge Sources (Strictly Separated)

* **God Speaks**
  Metaphysical and doctrinal text explaining:

  * Consciousness
  * Sanskaras
  * Evolution and involution
  * Planes of awareness
  * God-realization

* **Life Eternal**
  Practical spiritual guidance addressing:

  * Human suffering
  * Love and relationships
  * Discipline and patience
  * Life difficulties
  * Inner growth

⚠️ These sources are **never mixed** during retrieval or response generation.

---

## 🎯 Core Problem Solved

Traditional systems fail in spiritual or philosophical domains because they:

* Mix doctrinal and practical texts
* Paraphrase authoritative material
* Hallucinate interpretations
* Blur philosophical boundaries

**Anuvada solves this by design.**

---

## 🏗️ System Architecture (High Level)

```
User Query
   ↓
Intent Detection
   ↓
Philosophy-Aware Book Routing
   ↓
Single-Source Vector Retrieval (Qdrant)
   ↓
Exact Quote Extraction
   ↓
Constrained Explanation Layer
```

---

## 🔑 Key Features

### 1️⃣ Intent-Aware Book Routing (Beyond Standard RAG)

Anuvada introduces a **deterministic intent classification layer** before retrieval.

* Personal life problems → *Life Eternal*
* Conceptual / metaphysical questions → *God Speaks*

This guarantees:

* No doctrinal contamination
* Philosophical consistency
* Source correctness

> This capability is **not supported by standard RAG architectures**, which rely purely on semantic similarity.

---

### 2️⃣ Quote-Faithful Response Generation (Hallucination-Safe)

Responses are structured in **two strict layers**:

#### A. Authoritative Source Text

* Retrieved passages are presented **verbatim**
* No paraphrasing
* No summarization
* No reinterpretation

#### B. Constrained Explanation Layer

* Explains the quote in simple language
* Relates it to the user’s situation
* Does **not** add new teachings
* Does **not** modify meaning

This design ensures:

* Semantic integrity
* Interpretive restraint
* Trustworthy output

---

### 3️⃣ Local, Offline Embeddings (Ethical & Reproducible)

* Uses **local sentence-transformer embeddings**
* No dependency on paid APIs
* No quota limits
* Fully reproducible and auditable
* Suitable for sensitive or sacred texts

---

### 4️⃣ Dual Qdrant Collections (Isolation by Design)

| Collection                | Purpose               |
| ------------------------- | --------------------- |
| `god_speaks_collection`   | Metaphysical doctrine |
| `life_eternal_collection` | Human life guidance   |

Each query interacts with **only one collection**, selected before retrieval.

---

## 🧩 Example Workflow

### User Query

> *“I feel my timing in life is wrong and nothing moves forward.”*

### System Behavior

1. Detects **personal life problem**
2. Routes query to **Life Eternal**
3. Retrieves Baba’s exact words on patience and preparation
4. Presents:

   * **Exact quote**
   * **Gentle explanation related to the problem**

No mixing. No hallucination.

---

### Another Query

> *“What are sanskaras?”*

### System Behavior

1. Detects **conceptual question**
2. Routes query to **God Speaks**
3. Retrieves doctrinal explanation
4. Presents text faithfully with minimal clarification

---

## 🛠️ Tech Stack

| Layer            | Technology                                 |
| ---------------- | ------------------------------------------ |
| Backend          | Python                                     |
| Vector DB        | Qdrant (Docker)                            |
| Embeddings       | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Architecture     | RAG with Intent Routing                    |
| Design Principle | Philosophy-Aware Retrieval                 |

---

## 📂 Project Structure

```
backend/
│
├── data/
│   ├── god_chunks/
│   ├── life_eternal/
│   └── normalized/
│
├── ingestion/
│   ├── ingest_god_speaks_local.py
│   └── ingest_life_eternal_local.py
│
├── retrieval/
│   └── router.py
│
└── app/
    └── (API layer – planned)
```

---

## 🚀 Current Status

* ✅ God Speaks normalized & ingested
* ✅ Life Eternal normalized & ingested
* ✅ Dual Qdrant collections active
* ✅ Philosophy-aware routing implemented
* ⏳ API & UI layers in progress

---

## 🔮 Future Enhancements

* FastAPI `/ask` endpoint
* Conversational follow-up handling
* Topic confidence scoring
* UI (ChatGPT-style interaction)
* Multi-text expansion (discourses, letters)

---

## 🧭 Design Philosophy

> *“Do not distort meaning in the name of explanation.”*

Anuvada is built on the principle that **wisdom systems must preserve truth before providing guidance**.

---

## 🏁 Summary

**Anuvada is not a generic chatbot.**
It is a **philosophy-aware retrieval system** that respects textual authority, preserves doctrinal boundaries, and delivers guidance with integrity.

.
