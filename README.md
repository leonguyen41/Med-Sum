🧪 Med-Sum — LLM Summarization Prototype for Clinical Notes

Med-Sum is a lightweight prototype exploring how LLMs and NLP preprocessing can summarize de-identified clinical notes from the MIMIC-IV-Note dataset.
The goal is to test feasibility, evaluate model behavior, and design a simple pipeline for generating readable patient-history summaries.

⚠️ This is a research prototype — not a production-ready system and does not contain real patient data.

🔧 Features

Extract and clean de-identified clinical notes (text preprocessing, normalization, noise removal).

Apply LLM and transformer-based models to generate concise medical summaries.

Evaluate summarization quality for readability and information retention.

Experiment with different prompting strategies and model configurations.

🧠 Models Used

LLMs via API (BART model from Hugging Face)

Transformer-based summarization baselines

Custom prompting patterns for structured summaries

📌 Notes

All data is de-identified; no sensitive patient information is included.

This project focuses on feasibility testing, prompting, and pipeline sketching—not deploying a clinical system.

📬 Author

Quoc Hoang Luan Nguyen (leonguyen41)
Prototype developed as part of personal research into LLM summarization workflows.
