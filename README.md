# Document Classification Framework

A Python framework for intelligent document processing and classification using rule-based algorithms and text extraction.

## Features

- 📄 **Multi-format Support**: PDF, Word documents, images (OCR), and text files
- 🏷️ **Smart Classification**: Automatically categorizes documents (financial, legal, HR, technical, general)
- 📊 **Batch Processing**: Process single files or entire directories
- 🤖 **CLI Interface**: Interactive mode and command-line arguments
- 📈 **Metadata Extraction**: File size, word count, summaries, and content previews

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Suhit17/document-classification-framework.git
cd document-classification-framework

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional, for enhanced NLP)
python -m spacy download en_core_web_sm
```

### Usage

```bash
# Interactive mode
python main.py

# Process single document
python main.py --file "path/to/document.pdf"

# Batch process directory
python main.py --batch "path/to/documents/"
```

## Examples

### Processing an Invoice
```bash
python main.py --file "data/input/sample_invoice.txt"
```

**Output:**
- Category: `financial`
- Word count: `78`
- Summary with key financial information

### Batch Processing
```bash
python main.py --batch "data/input/"
```

**Output:**
- Processes all supported files in directory
- Shows success/failure statistics
- Detailed results for each document

## Supported Formats

- **PDF** (.pdf) - Text extraction using PyPDF2
- **Word** (.doc, .docx) - Using python-docx
- **Images** (.jpg, .png, .jpeg) - OCR with pytesseract
- **Text** (.txt) - Direct reading

## Classification Categories

- **Financial**: Invoices, receipts, payments, budgets
- **Legal**: Contracts, agreements, policies, terms
- **HR**: Resumes, employment documents, payroll
- **Technical**: Manuals, specifications, documentation
- **General**: Other document types

## Project Structure

```
document-classification-framework/
├── main.py                 # CLI interface
├── simple_framework.py     # Core processing engine
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── data/
│   └── input/             # Test documents
│       ├── sample_invoice.txt
│       └── employment_contract.txt
└── README.md
```

## Dependencies

- PyPDF2 - PDF text extraction
- python-docx - Word document processing
- Pillow - Image processing
- pytesseract - OCR capabilities
- pathlib - File path handling

## Configuration

The framework uses environment variables for configuration. Copy `.env.example` to `.env` and update as needed:

```env
# Google Gemini API Configuration (optional)
GOOGLE_API_KEY=your_api_key_here

# Processing Configuration
BATCH_SIZE=50
MAX_WORKERS=4
CONFIDENCE_THRESHOLD=0.9
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and open-source libraries
- Designed for enterprise document processing workflows
- Optimized for batch processing and automation

---

🤖 **Generated with Claude Code** - AI-powered development assistant