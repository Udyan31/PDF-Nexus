import fitz  # PyMuPDF
import json
import os
from pathlib import Path
from collections import Counter
import re

def get_style_baseline(doc):
    """
    Analyzes the document to establish a baseline for body text and identify
    potential heading font sizes.
    """
    font_sizes = Counter()
    for page_num in range(min(5, doc.page_count)):  # Analyze first 5 pages for efficiency
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:  # Text blocks
                for l in b["lines"]:
                    for s in l["spans"]:
                        font_sizes[round(s["size"])] += 1
    
    if not font_sizes:
        return 12, {} # Default if no text found

    # Most common font size is likely the body text
    body_size = font_sizes.most_common(1)[0][0]

    # Any font size larger than body text is a potential heading
    heading_sizes = sorted([size for size in font_sizes if size > body_size + 1], reverse=True)
    
    # Map the top 3 largest sizes to H1, H2, H3
    level_map = {size: f"H{i+1}" for i, size in enumerate(heading_sizes[:3])}
    
    return body_size, level_map

def calculate_heading_score(span, body_size):
    """
    Calculates a score indicating the likelihood of a text span being a heading.
    """
    score = 0
    font_size = round(span['size'])

    # Score for larger font size
    score += (font_size - body_size)

    # Score for bold font
    if "bold" in span['font'].lower():
        score += 5

    # Score for being a numbered list item (e.g., "1.", "2.1", "A.")
    if re.match(r'^\s*(\d+(\.\d+)*|[A-Z])\.\s+', span['text']):
        score += 5

    return score

def process_pdfs():
    """
    Main function to process all PDFs in the input directory.
    """
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in input_dir.glob("*.pdf"):
        try:
            doc = fitz.open(pdf_path)
            body_size, level_map = get_style_baseline(doc)
            
            outline = []
            title = ""
            max_title_score = -1

            for page_num, page in enumerate(doc):
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if b['type'] == 0:
                        for l in b["lines"]:
                            # A line is considered a single potential heading
                            # We use the first span to represent the style of the line
                            first_span = l['spans'][0]
                            font_size = round(first_span['size'])
                            
                            if font_size in level_map:
                                score = calculate_heading_score(first_span, body_size)
                                line_text = "".join(s['text'] for s in l['spans']).strip()

                                # Heuristic: short, high-scoring lines are headings
                                if score > 5 and len(line_text) < 150:
                                    outline.append({
                                        "level": level_map[font_size],
                                        "text": line_text,
                                        "page": page_num + 1 # Page numbers are 1-indexed
                                    })
                                    
                                    # Check for title (highest scoring H1 on first page)
                                    if page_num == 0 and level_map.get(font_size) == 'H1':
                                        if score > max_title_score:
                                            max_title_score = score
                                            title = line_text

            # Fallback for title if not found on first page
            if not title and outline:
                h1s = [item['text'] for item in outline if item['level'] == 'H1']
                title = h1s[0] if h1s else outline[0]['text']

            # Final fallback to filename
            if not title:
                title = pdf_path.stem.replace('_', ' ').title()

            output_data = {
                "title": title,
                "outline": outline
            }

            output_file = output_dir / f"{pdf_path.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4)

        except Exception as e:
            print(f"Failed to process {pdf_path.name}: {e}")

if __name__ == "__main__":
    process_pdfs()
