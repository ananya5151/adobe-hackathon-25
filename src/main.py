import os
import glob
from .round_1a import generate_outline_from_pdf
from .round_1b import generate_ranked_sections_from_pdf

# Define the input and output directories relative to the project root
INPUT_DIR = "input"
OUTPUT_DIR = "output"

def main():
    """Main function to process all PDFs in the input directory."""
    # Check for the ADOBE_QUERY environment variable to decide which round to run
    query = os.environ.get("ADOBE_QUERY")

    if query:
        print("Starting Round 1B: Persona-Driven Intelligence...")
        print(f"Using query: {query}")
        run_round_1b(query)
    else:
        print("Starting Round 1A: PDF Outline Extraction...")
        run_round_1a()

def run_round_1a():
    """Executes the Round 1A workflow."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {INPUT_DIR}. Exiting.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.")

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

def run_round_1b(query):
    """Executes the Round 1B workflow."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {INPUT_DIR}. Exiting.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.")

    for pdf_path in pdf_files:
        process_pdf_for_1b(pdf_path, query)

    print("Round 1B processing complete.")

def process_pdf_for_1b(pdf_path, query):
    """Helper function to process a single PDF for Round 1B."""
    print(f"Processing {os.path.basename(pdf_path)} for Round 1B...")
    try:
        json_output = generate_ranked_sections_from_pdf(pdf_path, query)
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_filename = f"{base_filename}_ranked.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, 'w') as f:
            f.write(json_output)
        print(f"Successfully created ranked sections at {output_path}")
    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {e}")

if __name__ == "__main__":
    main()