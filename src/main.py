import os
import glob
from .round_1a import generate_outline_from_pdf
from .round_1b import generate_ranked_sections_from_pdf

# Define the input and output directories relative to the project root
INPUT_DIR = "input"
OUTPUT_DIR = "output"

def main():
    """Main function to process all PDFs in the input directory."""
    # Check for persona and job environment variables to decide which round to run
    persona = os.environ.get("ADOBE_PERSONA")
    job = os.environ.get("ADOBE_JOB")

    if persona and job:
        print("Starting Round 1B: Persona-Driven Document Intelligence...")
        print(f"Persona: {persona}")
        print(f"Job: {job}")
        run_round_1b(persona, job)
    else:
        print("Starting Round 1A: PDF Outline Extraction...")
        run_round_1a()

def run_round_1a():
    """Executes the Round 1A workflow."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    round_1a_dir = os.path.join(INPUT_DIR, "1a")
    pdf_files = glob.glob(os.path.join(round_1a_dir, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {round_1a_dir}. Exiting.")
        return

    for pdf_path in pdf_files:
        process_pdf_for_1a(pdf_path)
    
    print("Round 1A processing complete.")

def process_pdf_for_1a(pdf_path):
    """Helper function to process a single PDF for Round 1A."""
    print(f"Processing {os.path.basename(pdf_path)} for Round 1A...")
    try:
        json_output = generate_outline_from_pdf(pdf_path)
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{base_filename}_outline.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, 'w') as f:
            f.write(json_output)
        print(f"Successfully created outline at {output_path}")
    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {e}")

def run_round_1b(persona, job):
    """Executes the Round 1B workflow for a collection of PDFs."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all PDFs recursively
    all_pdf_files = glob.glob(os.path.join(INPUT_DIR, "**", "*.pdf"), recursive=True)
    
    # Exclude files from the '1a' directory
    round_1a_dir_path = os.path.abspath(os.path.join(INPUT_DIR, "1a"))
    pdf_files = [f for f in all_pdf_files if not os.path.abspath(f).startswith(round_1a_dir_path)]

    if not pdf_files:
        print(f"No PDF files for Round 1B found in {INPUT_DIR} subdirectories. Exiting.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process for Round 1B.")

    try:
        # Round 1B processes all PDFs together
        json_output = generate_ranked_sections_from_pdf(pdf_files, persona, job)
        output_filename = "round_1b_analysis.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, 'w') as f:
            f.write(json_output)
        print(f"Successfully created Round 1B analysis at {output_path}")
    except Exception as e:
        print(f"Error during Round 1B processing: {e}")

if __name__ == "__main__":
    main()