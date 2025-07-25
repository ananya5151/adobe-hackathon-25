import fitz  # PyMuPDF
import json
import statistics
from collections import Counter
import re

def extract_text_blocks(doc, page_limit=None):
    """Extracts all text blocks from a PDF with metadata."""
    blocks_data = []
    pages_to_process = range(len(doc))
    if page_limit is not None:
        pages_to_process = range(min(len(doc), page_limit))

    for page_num in pages_to_process:
        page = doc[page_num]
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if not text:
                        continue
                    blocks_data.append({
                        "text": text,
                        "font_size": s["size"],
                        "font_name": s["font"],
                        "page": page_num + 1,
                        "y_pos": s["bbox"][1]
                    })
    return blocks_data

def get_body_text_style(blocks):
    """Determines the most common font size and name, likely the body text."""
    if not blocks:
        return 12, "default"
    # Filter out very large fonts to prevent titles from skewing the body text calculation
    font_sizes = [b['font_size'] for b in blocks if b['font_size'] < 20]
    if not font_sizes:
        font_sizes = [b['font_size'] for b in blocks] # Fallback if all fonts are large
        
    try:
        body_size = statistics.mode(font_sizes)
    except statistics.StatisticsError:
        body_size = sorted(Counter(font_sizes).items(), key=lambda x: x[1], reverse=True)[0][0]
    return body_size, "" # Font name is less reliable, focus on size

def identify_and_classify_headings(blocks, body_size):
    """Identifies headings using a scoring system and classifies them."""
    headings = []
    title_info = None

    # --- Find Title ---
    first_page_blocks = [b for b in blocks if b['page'] == 1]
    if first_page_blocks:
        max_font_size = max(b['font_size'] for b in first_page_blocks)
        # The title is often the first occurrence of the largest font size
        for b in first_page_blocks:
            if b['font_size'] == max_font_size:
                title_info = {'text': b['text'], 'page': 1}
                break

    # --- Smart Heading Identification using a Scoring System ---
    heading_candidates = []
    # Regex to find patterns like 1. 1.1. A. etc.
    heading_pattern = re.compile(r'^\s*(\d+(\.\d+)*\.?|[A-Z]\.)\s+')

    for b in blocks:
        text = b['text']
        font_size = b['font_size']
        font_name = b['font_name'].lower()
        
        # Skip the title itself
        if title_info and text == title_info['text'] and b['page'] == 1:
            continue

        score = 0
        # Criterion 1: Font size is larger than body text
        if font_size > body_size + 1:
            score += 2
        # Criterion 2: Font is bold
        if 'bold' in font_name:
            score += 1
        # Criterion 3: Starts with a numbering pattern
        if heading_pattern.match(text):
            score += 5 # This is a very strong indicator
        # Criterion 4: It's short (likely not a full paragraph)
        if len(text.split()) < 15:
            score += 1
        # Criterion 5: All caps (but not too short, to avoid single letters)
        if text.isupper() and len(text) > 2:
            score += 1

        if score >= 4: # Tune this threshold as needed
             heading_candidates.append(b)

    # --- Classify Cleaned Headings ---
    if not heading_candidates:
        return [], title_info

    # Use font sizes to determine H1, H2, H3 levels from the clean candidates
    heading_styles = sorted(list(set(b['font_size'] for b in heading_candidates)), reverse=True)
    style_map = {style: f"H{i+1}" for i, style in enumerate(heading_styles[:3])}

    for b in heading_candidates:
        if b['font_size'] in style_map:
            headings.append({
                "level": style_map[b['font_size']],
                "text": b['text'],
                "page": b['page'],
                "y_pos": b['y_pos']
            })

    return sorted(headings, key=lambda x: (x['page'], x['y_pos'])), title_info


def group_text_into_sections(blocks, headings):
    """Groups raw text blocks under the most recent heading."""
    sections = []
    if not headings: return []

    for i, heading in enumerate(headings):
        start_page = heading['page']
        start_y = heading['y_pos']
        
        # Determine the boundary of the section
        end_page = headings[i+1]['page'] if i + 1 < len(headings) else float('inf')
        end_y = headings[i+1]['y_pos'] if i + 1 < len(headings) else float('inf')

        content = ""
        for block in blocks:
            is_after_start = block['page'] > start_page or (block['page'] == start_page and block['y_pos'] > start_y)
            is_before_end = block['page'] < end_page or (block['page'] == end_page and block['y_pos'] < end_y)
            
            # Ensure the block is not another heading
            is_heading = any(h['text'] == block['text'] and h['page'] == block['page'] for h in headings)
            
            if is_after_start and is_before_end and not is_heading:
                content += block['text'] + "\n"
        
        sections.append({
            'heading_text': heading['text'],
            'heading_level': heading['level'],
            'page': heading['page'],
            'content': content.strip()
        })
    return sections


def generate_outline_from_pdf(pdf_path):
    """Main function for Round 1A to generate a structured JSON outline."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return json.dumps({"error": f"Could not open PDF: {e}"})

    blocks = extract_text_blocks(doc)
    doc.close()
    if not blocks: return json.dumps({"title": "", "outline": []})

    body_size, _ = get_body_text_style(blocks)
    headings, title_info = identify_and_classify_headings(blocks, body_size)
    
    title = title_info['text'] if title_info else "Untitled"
    
    outline = [{"level": h['level'], "text": h['text'], "page": h['page']} for h in headings]
    
    output_json = {"title": title, "outline": outline}
    return json.dumps(output_json, indent=4)