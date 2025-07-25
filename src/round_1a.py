import fitz  # PyMuPDF
import json
from collections import Counter

def extract_text_blocks(pdf_path):
    """Extracts text blocks with metadata from a PDF file."""
    doc = fitz.open(pdf_path)
    blocks_data = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l["spans"]:
                    if s["text"].strip():
                        blocks_data.append({
                            "text": s["text"].strip(),
                            "font_size": s["size"],
                            "font_name": s["font"],
                            "page": page_num + 1
                        })
    return blocks_data

def get_body_text_style(blocks_data):
    """Determines the most common font size and name from the text blocks."""
    if not blocks_data:
        return None, None
    font_sizes = [block['font_size'] for block in blocks_data]
    font_names = [block['font_name'] for block in blocks_data]
    most_common_size = Counter(font_sizes).most_common(1)[0][0]
    most_common_name = Counter(font_names).most_common(1)[0][0]
    return most_common_size, most_common_name

def identify_and_classify_headings(blocks_data, body_size, body_name):
    """Identifies and classifies headings from text blocks based on heuristics."""
    if not blocks_data:
        return [], None
    heading_candidates = []
    for block in blocks_data:
        is_larger = block['font_size'] > body_size
        is_bold = "bold" in block['font_name'].lower()
        is_short = len(block['text'].split()) < 20
        no_period_end = not block['text'].endswith('.')
        if is_larger and (is_bold or no_period_end) and is_short:
            heading_candidates.append(block)
    if not heading_candidates:
        return [], None
    title_info = None
    first_page_blocks = [b for b in heading_candidates if b['page'] == 1]
    if first_page_blocks:
        title_candidate = max(first_page_blocks, key=lambda x: x['font_size'])
        title_info = {"text": title_candidate["text"], "page": title_candidate["page"]}
        heading_candidates.remove(title_candidate)
    unique_heading_sizes = sorted(list(set(h['font_size'] for h in heading_candidates)), reverse=True)
    size_to_level_map = {size: f"h{i + 1}" for i, size in enumerate(unique_heading_sizes)}
    headings = []
    for head in heading_candidates:
        headings.append({
            "text": head["text"],
            "level": size_to_level_map.get(head["font_size"], "unknown"),
            "page": head["page"]
        })
    headings.sort(key=lambda x: x['page'])
    return headings, title_info

def generate_outline_from_pdf(pdf_path):
    """Generates a structured JSON outline from a PDF file."""
    blocks_data = extract_text_blocks(pdf_path)
    if not blocks_data:
        return json.dumps({"title": "", "outline": []}, indent=4)

    body_size, body_name = get_body_text_style(blocks_data)
    if not body_size or not body_name:
        return json.dumps({"title": "", "outline": []}, indent=4)

    headings, title_info = identify_and_classify_headings(blocks_data, body_size, body_name)

    # Format the final JSON output to match the required schema
    formatted_headings = [
        {"level": h['level'].upper(), "text": h['text'], "page": h['page']}
        for h in headings
    ]

    output_json = {
        "title": title_info["text"] if title_info else "",
        "outline": formatted_headings
    }
    return json.dumps(output_json, indent=4)