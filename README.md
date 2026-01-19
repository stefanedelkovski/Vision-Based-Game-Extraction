# Vision-Based Game HUD Extraction - Experiments

This repository is a **sandbox of experiments**, not a single finished product.

The goal across all scripts is simple:
> Extract structured HUD data (game name, credit, bet, win, free spins, feature state) from **images and videos** using vision models.

Everything here explores *how* to do that using LLMs.

---

## What the scripts are testing

### Image vs video
- Some scripts work on **single images**
- Others extract **frames from videos** and process those

Reason: real data comes from video, but images are faster to test prompts and accuracy.

---

### Loose output vs strict output
- Some scripts allow free-form / CSV-like text
- Others force **strict JSON schemas**

Reason: loose output is fast for testing, strict output is safer for production.

---

### Direct scripts vs API
- Standalone scripts = fast iteration
- Flask API = reusable service

Reason: prove the logic first, wrap it later.

---

### Immediate processing vs batch jobs
- Immediate: extract → infer → return results
- Batch: extract → JSONL → OpenAI Batch API

Reason: batch is needed for scale, async runs, and cost control.

---

### Model & SDK variations
- `gpt-4o` vs `gpt-4o-mini`
- Different request sizes
- Typed parsing vs manual parsing

Reason: find the best balance between accuracy, cost, and reliability.

---

## Why there are many files

Each script answers **one question**:
- Does strict schema reduce errors?
- How many frames per request works best?
- Is batch worth the overhead?
- Can video be processed end-to-end cleanly?

They are experiments by design.

---

## Current state

- HUD extraction works
- Video → frames → structured output is proven
- Batch and non-batch flows both validated

What’s missing is **consolidation**, not functionality.

---

## Next logical upgrades

- Merge into one configurable pipeline
- Add confidence scoring and validation
- Add async workers / queues
- Store results in a DB instead of files
- Production-grade API (FastAPI)

---

**TL;DR**  
This repo exists to *prove approaches*, not to look clean.  
The clean version comes after the experiments.
