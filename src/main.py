#!/usr/bin/env python3
"""
Adobe Hackathon 2025: "Connecting the Dots" - Final Orchestrator
"""
import json, logging
from pathlib import Path
# --- THIS IS THE FIX: Import the correct class name ---
from round_1a import PDFStructureExtractor
from round_1b import DocumentIntelligenceAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChallengeOrchestrator:
    def __init__(self, input_dir="/app/input", output_dir="/app/output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.structure_extractor = PDFStructureExtractor()
        # --- AND FIX THE INSTANTIATION HERE ---
        self.intelligence_analyzer = DocumentIntelligenceAnalyzer()

    def run_round_1a(self, folder_path: Path):
        logger.info(f"--- Running Round 1A on folder: {folder_path.name} ---")
        pdf_files = list(folder_path.glob("*.pdf"))
        if not pdf_files: return

        output_1a_dir = self.output_dir / folder_path.name
        output_1a_dir.mkdir(exist_ok=True)
        for pdf_file in pdf_files:
            try:
                result = self.structure_extractor.extract_pdf_outline(str(pdf_file))
                output_path = output_1a_dir / f"{pdf_file.stem}_outline.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                logger.info(f"Saved 1A outline to {output_path}")
            except Exception as e:
                logger.error(f"Error in Round 1A on {pdf_file.name}: {e}")

    def run_round_1b(self, config_path: Path):
        logger.info("--- Running Round 1B with AI Document Intelligence ---")
        try:
            with open(config_path, 'r', encoding='utf-8') as f: config = json.load(f)
            result = self.intelligence_analyzer.analyze_documents(
                documents=config.get('documents', []),
                persona=config.get('persona', {}),
                job_to_be_done=config.get('job_to_be_done', {}),
                input_dir=str(self.input_dir)
            )
            output_path = self.output_dir / "intelligence_analysis.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved 1B analysis to {output_path}")
        except Exception as e:
            logger.error(f"Critical error in Round 1B: {e}", exc_info=True)

    def run(self):
        logger.info("Starting Adobe Hackathon Submission Orchestrator")
        subfolders = [f for f in self.input_dir.iterdir() if f.is_dir()]
        for folder in subfolders:
            if '1a' in folder.name.lower(): self.run_round_1a(folder)
        
        config_path = self.input_dir / "config.json"
        if config_path.exists(): self.run_round_1b(config_path)
        logger.info("All tasks completed.")

if __name__ == "__main__":
    ChallengeOrchestrator().run()