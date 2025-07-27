# Adobe Hackathon 2025: Connecting the Dots

This project is a solution for the Adobe Hackathon, designed to intelligently process PDF documents. It features a hybrid system that performs two main tasks: multilingual structure extraction (Round 1A) and AI-powered document intelligence (Round 1B), all orchestrated to run offline within a Docker container.

---

## Approach

The solution is driven by a central orchestrator that routes tasks based on the input folder structure, allowing for both types of analysis in a single run.

### Round 1A: Multilingual Structure Extraction

The goal of Round 1A is to extract a structured outline (Title and Headings) from any PDF, regardless of the language. 

**This approach is specifically designed to fulfill the multilingual bonus requirement. It successfully generates accurate outlines for documents in languages like Hindi and Japanese because it does not rely solely on font sizes.**

The method uses a **multi-factor heuristic scoring system** for high accuracy:

1.  **Line Property Extraction**: The process begins by using `pdfplumber` to extract all text lines from the PDF. This includes crucial metadata for each line, such as its font size, font weight (bold), and position on the page.

2.  **Document Style Analysis**: To establish a baseline, the script performs a global analysis of all extracted lines to find the most common (mode) font size. This is robustly identified as the document's primary **body text** style.

3.  **Heuristic Scoring**: Each line is assigned a "heading score" based on how much it deviates from the body text. This score is calculated using multiple language-agnostic signals:
    * **Font Size**: Lines with a font size significantly larger than the body text receive a high score.
    * **Font Weight**: Bolded text receives a score bonus.
    * **Text Patterns**: Common patterns (e.g., "Chapter 1", "2.1.3") are given a high score.
    * **Conciseness**: Shorter lines, which are typical for headings, receive a score bonus.

4.  **Title and Heading Classification**: The document's title is identified as the highest-scoring line on the first page. The remaining lines that pass a score threshold are first checked against numbering patterns for definitive classification. If no pattern matches, the script falls back to ranking them into levels (H1, H2, H3) by sorting their unique font sizes in descending order.

### Round 1B: AI-Powered Document Intelligence

Round 1B uses an on-device AI model to understand and rank document sections based on their semantic relevance to a user's specific goal.

1.  **Orchestration and Configuration**: The `main.py` orchestrator identifies all subfolders not marked as `1a` as part of the Round 1B document collection. The entire process is driven by a central `input/config.json` file, which defines the document set, the user `persona`, and their `job_to_be_done`.

2.  **Structural Sectioning**: To get clean, meaningful sections, the script first runs an internal analysis (similar to the advanced Round 1A logic) to identify the document's actual headings. The text between one heading and the next is treated as a single, coherent section. This provides accurate section titles and content for analysis.

3.  **Semantic Embeddings**: The `Sentence-Transformers` library is used with the `all-MiniLM-L6-v2` model. This lightweight (~86MB) but powerful model converts both the user's query (persona + job) and the text content of each section into numerical vectors (embeddings) that capture their semantic meaning.

4.  **Cosine Similarity and Ranking**: To measure relevance, the cosine similarity between the user's query vector and each section's vector is calculated. A higher score (closer to 1.0) indicates a stronger semantic match. The sections are then sorted in descending order based on this score to produce the final importance ranking.

---

## Models and Libraries Used

* **Programming Language**: Python 3.10
* **PDF Parsing**: `pdfplumber`, `PyPDF2`
* **AI / NLP Model**: `Sentence-Transformers` with the `all-MiniLM-L6-v2` on-device model.
* **Core Libraries**: `torch` (CPU version), `numpy`, `scikit-learn`, `nltk`.

---

## How to Build and Run Your Solution

This solution is fully containerized with Docker for easy and reproducible execution.

### Prerequisites

* Docker Desktop installed and running.
* Python installed locally (for the one-time model download).

### 1. (One-Time) Download AI Model

The AI model must be downloaded before building the Docker image.

```powershell
# (Optional) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate

# Install dependencies required for the download
pip install -r requirements.txt

# Run the download script
python download_model.py

### 1. Build the Docker Image

Navigate to the project's root directory in your terminal and run the following command:

```bash
docker build --platform linux/amd64 -t adobe-solution:latest .
```

### 2. Run the Solution


The orchestrator handles both rounds in a single command. Prepare your input folder as needed, then run the container.

```bash
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" adobe-hackathon-app
```

The script will automatically process all configured tests and place the results in the output directory, following the execution flow specified in the hackathon challenge document.

