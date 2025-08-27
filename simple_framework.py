"""Simplified Document Classification Framework"""
import os
import logging
from pathlib import Path
from typing import Dict, Any
import PyPDF2
from PIL import Image
import pytesseract
from docx import Document
import re

class DocumentClassificationFramework:
    """Simple document processing framework"""
    
    def __init__(self):
        """Initialize the framework"""
        self.setup_logging()
        print("Framework initialized successfully")
    
    def setup_logging(self):
        """Setup basic logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a single document"""
        try:
            print(f"Processing: {file_path}")
            
            # Check if file exists
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Extract text based on file type
            content = self.extract_text(path)
            
            if not content:
                return {"success": False, "error": "Could not extract text from document"}
            
            # Simple classification
            category = self.classify_document(content, path.name)
            
            # Generate summary
            summary = self.generate_summary(content, category)
            
            result = {
                "success": True,
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "word_count": len(content.split()),
                "category": category,
                "summary": summary,
                "content_preview": content[:200] + "..." if len(content) > 200 else content
            }
            
            print(f"Successfully processed: {path.name}")
            print(f"Category: {category}")
            print(f"Word count: {result['word_count']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Process all documents in a directory"""
        try:
            dir_path = Path(directory_path)
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {directory_path}"}
            
            # Find supported files
            supported_extensions = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png'}
            files = []
            
            for ext in supported_extensions:
                files.extend(dir_path.glob(f"*{ext}"))
                files.extend(dir_path.glob(f"*{ext.upper()}"))
            
            if not files:
                return {"success": False, "error": "No supported documents found"}
            
            results = []
            successful = 0
            failed = 0
            
            for file_path in files:
                result = self.process_document(str(file_path))
                results.append(result)
                
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
            
            return {
                "success": True,
                "total_files": len(files),
                "successful": successful,
                "failed": failed,
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.pdf':
                return self.extract_pdf_text(file_path)
            elif extension in ['.doc', '.docx']:
                return self.extract_word_text(file_path)
            elif extension in ['.jpg', '.jpeg', '.png']:
                return self.extract_image_text(file_path)
            elif extension == '.txt':
                return file_path.read_text(encoding='utf-8', errors='ignore')
            else:
                return ""
        except Exception as e:
            self.logger.error(f"Text extraction error for {file_path}: {str(e)}")
            return ""
    
    def extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"PDF extraction error: {str(e)}")
            return ""
    
    def extract_word_text(self, file_path: Path) -> str:
        """Extract text from Word documents"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            self.logger.error(f"Word extraction error: {str(e)}")
            return ""
    
    def extract_image_text(self, file_path: Path) -> str:
        """Extract text from images using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            self.logger.error(f"OCR extraction error: {str(e)}")
            return ""
    
    def classify_document(self, content: str, filename: str = "") -> str:
        """Simple rule-based document classification"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # Financial keywords
        financial_keywords = ['invoice', 'payment', 'receipt', 'budget', 'financial', 'cost', 'price', 'total', 'amount']
        if any(keyword in content_lower or keyword in filename_lower for keyword in financial_keywords):
            return "financial"
        
        # Legal keywords
        legal_keywords = ['contract', 'agreement', 'legal', 'terms', 'policy', 'clause', 'liability', 'copyright']
        if any(keyword in content_lower or keyword in filename_lower for keyword in legal_keywords):
            return "legal"
        
        # HR keywords
        hr_keywords = ['resume', 'cv', 'employee', 'hr', 'payroll', 'benefits', 'hiring', 'interview']
        if any(keyword in content_lower or keyword in filename_lower for keyword in hr_keywords):
            return "hr"
        
        # Technical keywords
        tech_keywords = ['technical', 'specification', 'manual', 'guide', 'documentation', 'api', 'software']
        if any(keyword in content_lower or keyword in filename_lower for keyword in tech_keywords):
            return "technical"
        
        return "general"
    
    def generate_summary(self, content: str, category: str) -> str:
        """Generate a simple summary of the document"""
        word_count = len(content.split())
        
        # Get first few sentences
        sentences = content.split('.')[:3]
        first_part = '. '.join(sentences).strip()
        if len(first_part) > 200:
            first_part = first_part[:200] + "..."
        
        summary = f"This is a {category} document with {word_count} words. "
        
        if first_part:
            summary += f"Content preview: {first_part}"
        
        return summary