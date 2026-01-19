# Vision-Based Game HUD Extraction — Experiments & Prototypes

This repository contains **multiple experimental scripts and prototypes** exploring how to reliably extract structured data from **gambling / slot game images and videos** using OpenAI vision models.

The core problem being explored is:
> *How to accurately, reliably, and scalably extract game HUD information (credit, bet, win, free spins, feature state, etc.) from screenshots and video frames.*

---

## What this repo is (high level)

This is **not a single finished product**.  
It is a **collection of experiments** that test different approaches along the same pipeline:

**Video / Image → Vision Model → Structured Output**

Each script answers a slightly different question about:
- accuracy
- reliability
- scalability
- output format
- cost
- ease of integration

---

## Categories of experiments

### 1. Image-based extraction
Scripts that send:
- a **single image**
- or **multiple images in one request**

to the model and extract HUD fields.

**Why:**  
To validate prompt quality, schema correctness, and model consistency before touching video or scale.

---

### 2. Loose output vs strict output
Two output strategies are tested:
- **Loose text / CSV-like output** (parsed after)
- **Strict JSON schema output** (model forced into a fixed structure)

**Why:**  
To compare speed and flexibility vs downstream safety.  
Strict schemas are more production-safe; loose output is faster for exploration.

---

### 3. Image scripts vs video scripts
- Image scripts work on screenshots or extracted frames.
- Video scripts:
  - extract frames at intervals
  - batch frames
  - send them to the model
  - aggregate results into tables (often Excel).

**Why:**  
Most real-world data comes as video streams, not still images.

---

### 4. Immediate processing vs batch processing
Two execution styles are tested:
- **Immediate inference**
  - extract frames → call model → get results
- **Batch preparation**
  - extract frames → generate JSONL → submit to OpenAI Batch API

**Why:**  
Immediate processing is ideal for debugging and small jobs.  
Batch processing is required for **scale, async execution, and cost control**.

---

### 5. Direct scripts vs API wrapper
Some logic exists as:
- **standalone scripts** (hardcoded paths, fast iteration)
- **Flask API endpoints** wrapping the same logic

**Why:**  
Scripts are faster to experiment with.  
APIs are needed once this becomes a reusable service.

---

### 6. Model & SDK experiments
Different scripts test:
- `gpt-4o` vs `gpt-4o-mini`
- strict JSON schema enforcement
- typed parsing (e.g. Pydantic)
- token counting and cost estimation

**Why:**  
To understand reliability, cost, and developer ergonomics before locking choices.

---

## Why there are many scripts

Each script exists to answer **one specific question**, such as:
- Can the model reliably detect “feature mode”?
- Does strict schema reduce hallucinations?
- How many frames per request is optimal?
- Is batch processing worth the complexity?
- Can video be processed end-to-end without manual cleanup?

Nothing here is accidental duplication — it’s **deliberate exploration**.

---

## Current state

- Extraction logic works.
- Schema-based outputs are stable.
- Video → frame → structured data pipelines are validated.
- Batch and non-batch paths are proven.

What’s missing is **consolidation**, not capability.

---

## Potential upgrades / next steps

- Merge experiments into **one clean pipeline**:
  - configurable (image / video)
  - configurable (immediate / batch)
- Introduce:
  - confidence scores
  - frame-to-frame consistency checks
- Add:
  - async workers
  - queue-based ingestion
- Normalize outputs into:
  - database-ready schema
  - streaming-compatible format
- Replace Flask with FastAPI if productionized.
- Add monitoring for:
  - failed frames
  - ambiguous detections
  - cost per minute of video

---

## TL;DR

This repo is a **research & validation sandbox** for vision-based HUD extraction.  
Multiple scripts exist to **test approaches, not because of poor structure**.  
The winning patterns are already clear — the next step is consolidation into a single, clean system.
