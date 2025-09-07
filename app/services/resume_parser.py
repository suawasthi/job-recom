import os
import tempfile
from typing import Dict, Any, Optional
import PyPDF2
from docx import Document
from app.services.nlp_service import nlp_service, ExtractedInfo
from app.utils.file_handler import FileHandler

class ResumeParserService:
    def __init__(self):
        self.file_handler = FileHandler()
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}")

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {str(e)}")

    def extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text based on file extension"""
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    async def parse_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Main resume parsing method

        Args:
            file_content: Binary content of the uploaded file
            filename: Original filename with extension

        Returns:
            Dictionary containing parsed resume data
        """
        # Validate file format
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}")

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Extract text from file
            extracted_text = self.extract_text_from_file(temp_file_path, filename)

            if not extracted_text.strip():
                raise ValueError("No text could be extracted from the file")

            # Use NLP service to extract structured information
            extracted_info: ExtractedInfo = nlp_service.extract_all_info(extracted_text)

            # Format the response
            parsed_data = {
                "extracted_text": extracted_text,
                "parsed_name": extracted_info.name,
                "parsed_email": extracted_info.email,
                "parsed_phone": extracted_info.phone,
                "skills": extracted_info.skills or [],
                "experience_years": extracted_info.experience_years,
                "education": extracted_info.education or [],
                "work_experience": extracted_info.work_experience or [],
                "projects": extracted_info.projects or [],
                "parsing_status": "success",
                "confidence_score": self._calculate_parsing_confidence(extracted_info)
            }

            return parsed_data

        except Exception as e:
            raise ValueError(f"Error parsing resume: {str(e)}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def _calculate_parsing_confidence(self, extracted_info: ExtractedInfo) -> float:
        """Calculate confidence score for parsing quality"""
        score = 0.0

        if extracted_info.name:
            score += 0.2
        if extracted_info.email:
            score += 0.2
        if extracted_info.phone:
            score += 0.1
        if extracted_info.skills:
            score += 0.2
        if extracted_info.experience_years is not None:
            score += 0.1
        if extracted_info.education:
            score += 0.1
        if extracted_info.work_experience:
            score += 0.1

        return min(score, 1.0)

    def get_fallback_fields(self, parsed_data: Dict[str, Any]) -> Dict[str, bool]:
        """Identify which fields need manual input"""
        fallback_needed = {
            "name": not parsed_data.get("parsed_name"),
            "email": not parsed_data.get("parsed_email"),
            "phone": not parsed_data.get("parsed_phone"),
            "skills": not parsed_data.get("skills"),
            "experience": parsed_data.get("experience_years") is None,
            "education": not parsed_data.get("education"),
            "work_experience": not parsed_data.get("work_experience")
        }
        return fallback_needed

# Singleton instance
resume_parser = ResumeParserService()
