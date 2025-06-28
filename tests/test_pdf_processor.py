import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.pdf_processor import extract_text_from_pdf

class TestPdfProcessor(unittest.TestCase):
    @patch('pdfplumber.open')
    def test_extract_text_success(self, mock_open):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text"
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf
        
        result = extract_text_from_pdf(Path("dummy.pdf"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], "Sample text")

if __name__ == '__main__':
    unittest.main()