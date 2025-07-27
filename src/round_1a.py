#!/usr/bin/env python3
"""
Round 1a: PDF Structure Extraction
Extract structured outlines (title, headings) from PDF documents.
"""
import re
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

try:
    import pdfplumber
    from PyPDF2 import PdfReader
except ImportError as e:
    logging.error(f"Required libraries not installed for Round 1A: {e}")
    raise

logger = logging.getLogger(__name__)

class PDFStructureExtractor:
    def __init__(self):
        self.heading_patterns = [
            r'^\d+\.\s+[A-Z]',          # e.g., "1. Introduction"
            r'^[A-Z][A-Z\s]{5,}[A-Z]$',  # ALL CAPS HEADING
            r'^\d+\.\d+\.?\s+',         # e.g., "1.1 Background"
            r'^\d+\.\d+\.\d+\.?\s+',     # e.g., "1.1.1 Details"
        ]

    def extract_pdf_outline(self, pdf_path: str) -> Dict[str, Any]:
        """Main function to extract structured outline from PDF."""
        try:
            logger.info(f"Starting extraction for {Path(pdf_path).name}")
            title = self._extract_title(pdf_path)
            headings = self._extract_headings(pdf_path)
            return self._generate_outline_json(title, headings)
        except Exception as e:
            logger.error(f"Error extracting from {Path(pdf_path).name}: {e}")
            return {"title": "", "outline": [], "error": str(e)}

    def _extract_title(self, pdf_path: str) -> str:
        """Extract document title from metadata or first page."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                if pdf_reader.metadata and pdf_reader.metadata.title:
                    title = pdf_reader.metadata.title.strip()
                    if len(title) > 5: return title
        except Exception:
            pass # Fallback to text extraction

        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                words = first_page.extract_words(keep_blank_chars=False, use_text_flow=True)
                # Assume the line with the largest font size on the top half of the page is the title
                top_half_words = [w for w in words if w['top'] < first_page.height / 2]
                if not top_half_words: return "Untitled Document"
                
                max_size = max(w['size'] for w in top_half_words)
                title_words = [w['text'] for w in top_half_words if w['size'] > max_size * 0.9]
                return " ".join(title_words) if title_words else "Untitled Document"
        except Exception:
            return "Untitled Document"

    def _extract_headings(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract headings with their levels and page numbers."""
        headings = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                logger.debug(f"Processing page {i+1}/{len(pdf.pages)} for headings...")
                lines = page.extract_text_lines(layout=True, strip=True)
                for line in lines:
                    text = line['text']
                    if len(text) < 4 or len(text) > 200: continue
                    
                    level = self._determine_heading_level(text)
                    if level:
                        headings.append({
                            "level": level,
                            "text": text,
                            "page": i + 1,
                        })
        
        # Post-process to remove duplicates and limit size
        seen = set()
        unique_headings = []
        for h in headings:
            key = (h['text'], h['page'])
            if key not in seen:
                seen.add(key)
                unique_headings.append(h)
        
        logger.info(f"Found {len(unique_headings)} unique headings in {Path(pdf_path).name}.")
        return unique_headings[:150] # Limit to 150 headings

    def _determine_heading_level(self, text: str) -> str:
        """Determines heading level based on patterns."""
        if re.match(r'^\d+\.\s', text): return "H1"
        if re.match(r'^\d+\.\d+\.?\s', text): return "H2"
        if re.match(r'^\d+\.\d+\.\d+\.?\s', text): return "H3"
        if text.isupper() and len(text.split()) < 7: return "H1"
        if text.istitle() and len(text.split()) < 10 and not text.endswith('.'): return "H2"
        return "" # Not a heading

    def _generate_outline_json(self, title: str, headings: List[Dict]) -> Dict[str, Any]:
        """Generates the final JSON structure."""
        return {
            "title": title,
            "outline": headings,
            "extraction_timestamp": datetime.now().isoformat(),
            "total_headings": len(headings)
        }