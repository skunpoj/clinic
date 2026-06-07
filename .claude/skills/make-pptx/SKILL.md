# /make-pptx

Generate (or regenerate) the Clinical Note Retrieval System presentation as a `.pptx` file and deliver it to the user.

## Usage

```
/make-pptx
/make-pptx --title "My Custom Title"
```

## What this skill does

1. Runs `scripts/make_pptx.py` to build a 10-slide PowerPoint presentation covering:
   - Problem statement & clinical motivation
   - System architecture (5-step pipeline)
   - Embedding model selection & justification
   - Retrieval pipeline (FAISS + cosine similarity)
   - LLM summarisation layer (Claude API)
   - REST API design & request/response examples
   - Evaluation results (Precision@k, keyword recall, score spread)
   - Semantic-vs-keyword proof (paraphrased query experiments)
   - Fine-tuning roadmap & model comparison table
2. Saves the file as `Clinical_Note_Retrieval_System.pptx` in the repo root.
3. Delivers the file to the user.
4. Commits and pushes the updated PPTX to the active branch.

## Instructions

When the user invokes `/make-pptx`:

1. Ensure `python-pptx` is installed:
   ```bash
   pip install python-pptx --quiet
   ```
2. Run the generator:
   ```bash
   python3 scripts/make_pptx.py
   ```
3. Confirm the file was created and report its size.
4. Send the file to the user using the file delivery tool.
5. Commit and push:
   ```bash
   git add Clinical_Note_Retrieval_System.pptx
   git commit -m "Regenerate presentation PPTX"
   git push
   ```
6. Report success with the file name, slide count (10), and branch pushed to.

## Output format

```
Generated Clinical_Note_Retrieval_System.pptx (10 slides, ~50 KB)
Pushed to branch: <current branch>
```

Then deliver the `.pptx` file directly.
