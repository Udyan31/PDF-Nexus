# PDF-Nexus

This project is a high-performance solution for Challenge 1a of the Adobe India Hackathon. It intelligently extracts a document's title and hierarchical headings (H1, H2, H3) from PDF files, producing a structured JSON output. The solution is built to be fast, accurate, and language-agnostic, running entirely offline within a Docker container.

## ✨ Features

* **High-Speed Processing**: Utilizes the performance of the `PyMuPDF` library to process a 50-page PDF in well under 10 seconds.
* **High-Accuracy Heading Detection**: Employs a multi-feature heuristic scoring system that goes beyond simple font-size checks to accurately identify headings.
* **🌐 Multilingual Support**: The core logic is language-agnostic, capable of processing documents in various languages. It includes specific enhancements for recognizing different numbering styles, earning bonus points.
* **Offline Execution**: The container is self-contained and requires no internet access to function, adhering to a critical constraint.
* **Constraint Compliant**: Fully compliant with all challenge constraints, including execution time, model size (0MB), and CPU-only runtime.

---
## ⚙️ Approach and Methodology

The solution avoids large ML models in favor of a fast and sophisticated heuristic algorithm.

1.  **Baseline Analysis**: The script first analyzes the document to determine the font size and style of the main body text. This creates a dynamic baseline for accurately identifying what constitutes a heading.
2.  **Multi-Feature Scoring**: Each line of text is analyzed and assigned a "heading score" based on a weighted combination of features:
    * **Font Size & Weight**: How much larger and bolder is the text than the body?
    * **Positional Cues**: Is it centered or located high on the page?
    * **Textual Patterns**: Does it start with a numbering pattern (e.g., "1.", "A.", "I.")?
3.  **Hierarchy Determination**: After identifying headings, they are classified into H1, H2, and H3 levels based on their font sizes in descending order. This creates a reliable and accurate document outline.
4.  **Title Extraction**: The document title is identified as the highest-scoring heading on the first page. A fallback mechanism uses the filename if no clear title is found.

---
## 🌐 Multilingual Support

A key feature of this solution is its ability to handle documents in multiple languages, including those with non-Latin scripts like Japanese. This is achieved in two ways:

1.  **Language-Agnostic Heuristics**: The primary heading detection logic relies on visual and structural cues (font size, weight, position) rather than the text's content or language. These cues are nearly universal across all written languages for structuring documents.
2.  **Unicode-Aware Pattern Matching**: The logic for detecting numbered or lettered lists has been enhanced to be Unicode-aware. This allows it to recognize not only standard Western patterns (`1.`, `a.`) but also patterns from other languages, helping it earn the multilingual handling bonus.

---
## 🛠️ How to Build and Run

The solution is containerized with Docker.

1.  **Build the Docker image**:
    ```bash
    docker build --platform linux/amd64 -t pdf-nexus .
    ```
    This command is specified in the challenge guidelines.

2.  **Run the container**:
    Place your PDFs in a local `input` directory and create an `output` directory. Then, run the following command:
    ```bash
    docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none pdf-nexus
    ```
    This command mounts the local directories into the container and runs the processing script. The container will automatically process all PDFs from the `/app/input` directory and place the resulting `.json` files in the `/app/output` directory.

---
## ✅ Meeting Critical Constraints

| Constraint | Requirement | Status |
| :--- | :--- | :--- |
| **Execution Time** | ≤ 10 seconds for a 50-page PDF | **Met**. `PyMuPDF`'s high-speed C++ backend ensures fast parsing. |
| **Model Size** | ≤ 200MB (if using ML models) | **Met**. This solution uses a heuristic algorithm, resulting in a 0MB model size. |
| **Network** | No internet access allowed | **Met**. The container is fully self-contained. |
| **Runtime** | Must run on CPU (amd64) with 8 CPUs and 16 GB RAM | **Met**. The Dockerfile specifies the `linux/amd64` platform and uses no GPU dependencies. |
