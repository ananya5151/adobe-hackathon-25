# d:\Placement\RESUME\GitHub\Adobe_Hackathon\src\round_1b.py

import json
import os
import datetime
from sentence_transformers import SentenceTransformer, util
import torch
from . import round_1a
from .round_1a import (
    extract_text_blocks,
    get_body_text_style,
    identify_and_classify_headings,
    group_text_into_sections,
)

# Define the path to the local model
MODEL_PATH = 'models/all-MiniLM-L6-v2'

def load_model():
    """Loads the Sentence-Transformers model from the local path."""
    print(f"Loading model from {MODEL_PATH}...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer(MODEL_PATH, device=device)
    print(f"Model loaded successfully on {device}.")
    return model

def rank_sections_by_relevance(model, query, sections):
    """Ranks document sections based on semantic similarity to a query."""
    if not sections or not query:
        return []

    section_texts = [section['content'] for section in sections]
    print(f"Generating embeddings for {len(section_texts)} sections...")
    query_embedding = model.encode(query, convert_to_tensor=True)
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)
    print("Embeddings generated.")

    cosine_scores = util.cos_sim(query_embedding, section_embeddings)

    for i, section in enumerate(sections):
        section['relevance'] = cosine_scores[0][i].item()

    ranked_sections = sorted(sections, key=lambda x: x['relevance'], reverse=True)
    return ranked_sections

def generate_ranked_sections_from_pdf(pdf_paths, persona, job):
    """Orchestrates the Round 1B process for a collection of documents."""
    model = load_model()
    
    # Combine persona and job for a rich query
    query = f"Persona: {persona}. Job: {job}"

    # Step 1: Extract sections from all documents
    all_sections = []
    for pdf_path in pdf_paths:
        doc_name = os.path.basename(pdf_path)
        print(f"Extracting sections from {doc_name}...")
        blocks = extract_text_blocks(pdf_path)
        if not blocks:
            continue
        body_size, body_name = get_body_text_style(blocks)
        headings, _ = identify_and_classify_headings(blocks, body_size, body_name)
        sections = group_text_into_sections(blocks, headings)
        for section in sections:
            section['document'] = doc_name  # Tag section with its source document
        all_sections.extend(sections)

    # Step 2: Rank all sections from all documents (Pass 1)
    print("Ranking sections across all documents...")
    ranked_sections = rank_sections_by_relevance(model, query, all_sections)

    # Step 3: Placeholder for Sub-section Analysis (Pass 2)
    # This will be implemented in the next step.
    sub_section_analysis = []

    # Step 4: Format the final JSON output
    output_json = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in pdf_paths],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_section": [
            {
                "document": s['document'],
                "page_number": s['page'],
                "section_title": s['heading_text'],
                "importance_rank": i + 1
            }
            for i, s in enumerate(ranked_sections)
        ],
        "sub-section_analysis": sub_section_analysis # Placeholder
    }

    return json.dumps(output_json, indent=4)
