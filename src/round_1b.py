#!/usr/bin/env python3
"""
Round 1B: Persona-Driven Document Intelligence (Final Failsafe Version)
"""
import re, logging
from pathlib import Path
from datetime import datetime
try:
    import pdfplumber, nltk
    from sentence_transformers import SentenceTransformer, util
except ImportError: raise

logger = logging.getLogger(__name__)
try: nltk.data.find('tokenizers/punkt')
except LookupError: nltk.download('punkt', quiet=True)

class DocumentIntelligenceAnalyzer:
    def __init__(self, model_path='/app/models/all-MiniLM-L6-v2'):
        logger.info("Loading AI model...")
        self.model = SentenceTransformer(model_path)
        logger.info("AI model loaded.")

    def analyze_documents(self, documents: list, persona: dict, job_to_be_done: dict, input_dir: str) -> dict:
        try:
            query = f"{persona.get('role', '')}: {job_to_be_done.get('task', '')}"
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            
            all_sections = []
            for doc in documents:
                pdf_path = Path(input_dir) / doc.get('filename', '')
                if not pdf_path.exists(): continue
                
                logger.info(f"Analyzing: {pdf_path.name}")
                # FAILSAFE: Extract content by paragraph to ensure sections are found
                structured_content = self._extract_content_by_paragraph(pdf_path)
                
                section_texts = [s['content'] for s in structured_content]
                if not section_texts: continue

                section_embeddings = self.model.encode(section_texts, convert_to_tensor=True)
                cosine_scores = util.cos_sim(query_embedding, section_embeddings)
                
                for i, section in enumerate(structured_content):
                    section.update({'document': doc.get('filename'), 'relevance_score': cosine_scores[0][i].item()})
                    all_sections.append(section)

            ranked_sections = sorted(all_sections, key=lambda x: x['relevance_score'], reverse=True)
            for rank, section in enumerate(ranked_sections, 1):
                section['importance_rank'] = rank
            return self._generate_intelligence_json(documents, persona, job_to_be_done, ranked_sections)
        except Exception as e:
            return self._generate_error_response(str(e))

    def _extract_content_by_paragraph(self, pdf_path: Path) -> list:
        """Failsafe method that splits pages into paragraphs to ensure content is found."""
        sections = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                # Split by double newline, a common paragraph delimiter
                paragraphs = page_text.split('\n\n')
                for para in paragraphs:
                    cleaned_para = para.strip().replace('\n', ' ')
                    if len(cleaned_para) > 50: # Filter for substantial paragraphs
                        title = self._find_title_for_paragraph(cleaned_para, page_text)
                        sections.append({
                            "section_title": title,
                            "content": cleaned_para,
                            "page_number": page.page_number
                        })
        return sections

    def _find_title_for_paragraph(self, paragraph: str, full_page_text: str) -> str:
        """Finds the line of text immediately preceding a paragraph."""
        try:
            # Find the paragraph's position in the full page text
            para_start_index = full_page_text.find(paragraph[:50]) # Match the start of the para
            if para_start_index < 1:
                return ' '.join(paragraph.split()[:8]) + "..."

            # Get the text before the paragraph
            preceding_text = full_page_text[:para_start_index].strip()
            
            # The title is likely the last non-empty line
            title = preceding_text.split('\n')[-1].strip()
            
            # A simple check to ensure it's a plausible title
            if 2 < len(title) < 100 and not title.endswith(('.', ',')):
                return title
        except Exception:
            pass
        # Fallback if no clean title can be found
        return ' '.join(paragraph.split()[:8]) + "..."

    def _generate_intelligence_json(self, documents: list, persona: dict, job: dict, sections: list) -> dict:
        """Formats the final JSON output."""
        def get_first_paragraph(text):
            paragraphs = [p for p in text.split('\n\n') if p.strip()]
            return paragraphs[0] if paragraphs else text

        return {
            "metadata": {
                "input_documents": [d.get('filename') for d in documents],
                "persona": persona.get('role', ''),
                "job_to_be_done": job.get('task', ''),
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [{
                "document": s['document'], "page_number": s['page_number'],
                "section_title": s['section_title'], "importance_rank": s['importance_rank']
            } for s in sections[:35]],
            "subsection_analysis": [{
                "document": s['document'],
                "refined_text": get_first_paragraph(s['content']),
                "page_number": s['page_number']
            } for s in sections[:10]]
        }
    
    def _generate_error_response(self, error_msg: str) -> dict:
        return {"error": "Failed to process Round 1B", "details": error_msg}