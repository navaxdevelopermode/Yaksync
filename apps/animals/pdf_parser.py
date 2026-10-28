import os
import re
import datetime
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Fallback data matching the PDF content exactly
FALLBACK_DATA = [
    {
        "yak_id": "Yak 697",
        "name": "Tinkar Namu",
        "date_of_birth": "2018-05-17",
        "dam": "431",
        "sire": "335",
        "breeding_method": "Artificial Insemination",
        "vulva_length": 5.0,
        "vaginal_depth": 21.5,
        "distance_to_cervix": 16.0,
        "vaginal_diameter": 15.0,
        "parity": 3,
        "body_weight": 246.0,
        "description": "White Hoop in back and in legs",
        "vagina_temperature": 38.32
    },
    {
        "yak_id": "Cow 806",
        "name": "Kyanamu",
        "date_of_birth": "2020-08-02",
        "dam": "543",
        "sire": "455",
        "breeding_method": "Natural",
        "vulva_length": 5.0,
        "vaginal_depth": 19.5,
        "distance_to_cervix": 16.5,
        "vaginal_diameter": 14.0,
        "parity": 2,
        "body_weight": 190.0,
        "description": "Only Grey hair around the mouth area",
        "vagina_temperature": 37.56
    },
    {
        "yak_id": "Cow 842",
        "name": "Kankar Kyamo",
        "date_of_birth": "2021-07-17",
        "dam": "662",
        "sire": "631",
        "breeding_method": "Natural",
        "vulva_length": 5.0,
        "vaginal_depth": 20.0,
        "distance_to_cervix": 17.0,
        "vaginal_diameter": 15.0,
        "parity": 1,
        "body_weight": 166.0,
        "description": "Little white/gray surrounding the mouth, white hind legs, white tail, white spots up to the hump, and white under the body/stomach.",
        "vagina_temperature": 39.35
    },
    {
        "yak_id": "Buf 875",
        "name": "Not Recorded",
        "date_of_birth": "2021-08-31",
        "dam": "711",
        "sire": "621",
        "breeding_method": "Natural",
        "vulva_length": 5.0,
        "vaginal_depth": 15.4,
        "distance_to_cervix": 16.0,
        "vaginal_diameter": 17.0,
        "parity": 3,
        "body_weight": 294.0,
        "description": "White Spot at forehead, hump, tail. Grey hair around the mouth, chest and back legs and lower part of the abdomen is white",
        "vagina_temperature": 39.32
    },
    {
        "yak_id": "Buf 870",
        "name": "Not Recorded",
        "date_of_birth": "2021-08-25",
        "dam": "625",
        "sire": "631",
        "breeding_method": "Natural",
        "vulva_length": 5.0,
        "vaginal_depth": 15.25,
        "distance_to_cervix": 14.0,
        "vaginal_diameter": 17.0,
        "parity": 2,
        "body_weight": 186.0,
        "description": "Without horn, Grey hair in mouth area, white colour in hump, white tail, white colour in both part of the chest, white colour in both part of the lower legs",
        "vagina_temperature": 37.36
    },
    {
        "yak_id": "Cow 751",
        "name": "Not Recorded",
        "date_of_birth": "2019-06-02",
        "dam": "527",
        "sire": "335",
        "breeding_method": "Artificial Insemination",
        "vulva_length": 5.0,
        "vaginal_depth": 21.5,
        "distance_to_cervix": 15.5,
        "vaginal_diameter": 16.0,
        "parity": 2,
        "body_weight": 232.0,
        "description": "Complete black with a little white spot on the forehead",
        "vagina_temperature": 38.56
    },
    {
        "yak_id": "Yak 729",
        "name": "Not Recorded",
        "date_of_birth": "2018-11-17",
        "dam": "569",
        "sire": "631",
        "breeding_method": "Natural",
        "vulva_length": 4.5,
        "vaginal_depth": 23.0,
        "distance_to_cervix": 17.0,
        "vaginal_diameter": 16.0,
        "parity": 3,
        "body_weight": 284.0,
        "description": "whole body black, face is white and right nose is black.",
        "vagina_temperature": 32.66
    },
    {
        "yak_id": "Yak 527",
        "name": "Not Recorded",
        "date_of_birth": "2012-09-10",
        "dam": "93",
        "sire": "379",
        "breeding_method": "Natural",
        "vulva_length": 5.5,
        "vaginal_depth": 23.0,
        "distance_to_cervix": 17.0,
        "vaginal_diameter": 15.0,
        "parity": 6,
        "body_weight": 249.0,
        "description": "complete black",
        "vagina_temperature": 38.17
    },
    {
        "yak_id": "Buf 862",
        "name": "Not Recorded",
        "date_of_birth": "2021-08-09",
        "dam": "678",
        "sire": "631",
        "breeding_method": "Natural",
        "vulva_length": 4.5,
        "vaginal_depth": 23.5,
        "distance_to_cervix": 17.0,
        "vaginal_diameter": 17.0,
        "parity": 1,
        "body_weight": 240.0,
        "description": "full black, white face, right nose black",
        "vagina_temperature": 38.47
    },
    {
        "yak_id": "Cow 796",
        "name": "Kyanzangmu",
        "date_of_birth": "2020-06-11",
        "dam": "609",
        "sire": "522",
        "breeding_method": "Natural",
        "vulva_length": 4.5,
        "vaginal_depth": 21.5,
        "distance_to_cervix": 17.0,
        "vaginal_diameter": 16.0,
        "parity": 2,
        "body_weight": 178.0,
        "description": "small white spot in face, grey around the mouth",
        "vagina_temperature": 39.31
    },
    {
        "yak_id": "Buf 887",
        "name": "Not Recorded",
        "date_of_birth": "2022-01-24",
        "dam": "533",
        "sire": "718",
        "breeding_method": "Natural",
        "vulva_length": 4.5,
        "vaginal_depth": 18.0,
        "distance_to_cervix": 13.5,
        "vaginal_diameter": 18.0,
        "parity": 2,
        "body_weight": 175.0,
        "description": "complete black and no horn",
        "vagina_temperature": 38.62
    },
    {
        "yak_id": "Yak 834",
        "name": "Gaptamu",
        "date_of_birth": "2020-10-04",
        "dam": "574",
        "sire": "631",
        "breeding_method": "Natural",
        "vulva_length": 5.0,
        "vaginal_depth": 16.5,
        "distance_to_cervix": 16.5,
        "vaginal_diameter": 18.0,
        "parity": 1,
        "body_weight": 225.0,
        "description": "whole body black, face is partially white with more white on the right side. white tail",
        "vagina_temperature": 37.38
    }
]

def attempt_pypdf_install():
    try:
        import pypdf
        return pypdf
    except ImportError:
        logger.info("pypdf is not installed. Attempting dynamic installation...")
        import subprocess
        import sys
        try:
            # We run in a shell or using subprocess execution
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pypdf"])
            import pypdf
            logger.info("pypdf successfully installed dynamically.")
            return pypdf
        except Exception as e:
            logger.warning(f"Could not install pypdf dynamically: {e}")
            return None

class PDFAnalyticsService:
    @staticmethod
    def find_pdf_file():
        """Searches BASE_DIR and common project subdirectories for the PDF file."""
        candidates = [
            os.path.join(settings.BASE_DIR, "Yak Details - Sheet1.pdf"),
            os.path.join(settings.BASE_DIR, "media", "Yak Details - Sheet1.pdf"),
            os.path.join(settings.BASE_DIR, "apps", "animals", "Yak Details - Sheet1.pdf"),
        ]
        # Look for any PDF with "Yak Details" in the name in BASE_DIR
        try:
            for root, dirs, files in os.walk(settings.BASE_DIR):
                # Avoid looking inside venv, .git, node_modules etc.
                if any(x in root for x in ['venv', '.git', '.kiro', '__pycache__', 'staticfiles']):
                    continue
                for f in files:
                    if f.endswith('.pdf') and 'yak' in f.lower() and 'detail' in f.lower():
                        candidates.append(os.path.join(root, f))
        except Exception:
            pass

        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    @classmethod
    def clean_numeric(cls, value):
        """Cleans measurement values (e.g., '21.5 cm' -> 21.5, '246 kg' -> 246) and converts to float/int."""
        if value is None:
            return None
        val_str = str(value).strip()
        if val_str.lower() in ('not specified', 'not recorded', 'nan', 'null', 'none', '', '-'):
            return None
        # Remove units like cm, kg, °c
        cleaned = re.sub(r'(?i)\s*(cm|kg|°c|c)?', '', val_str).strip()
        try:
            if '.' in cleaned:
                return float(cleaned)
            return int(cleaned)
        except ValueError:
            return None

    @classmethod
    def clean_name(cls, name):
        """Normalizes animal name, substituting 'Not Recorded' for 'Not specified'."""
        if not name:
            return "Not Recorded"
        name_str = str(name).strip()
        if name_str.lower() in ('not specified', 'not recorded', '-', 'none', 'null'):
            return "Not Recorded"
        return name_str

    @classmethod
    def parse_date(cls, date_str):
        """Parses date string into YYYY-MM-DD string format."""
        if not date_str:
            return None
        date_str = str(date_str).strip()
        if date_str.lower() in ('not specified', 'not recorded', '-', 'none', 'null', ''):
            return None
        
        # Test standard formats
        for fmt in ('%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d'):
            try:
                dt = datetime.datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # Manual parse for variations
        parts = re.split(r'[-/]', date_str)
        if len(parts) == 3:
            try:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
                if year < 100:
                    year += 2000
                return datetime.date(year, month, day).strftime('%Y-%m-%d')
            except ValueError:
                pass
        return None

    @classmethod
    def extract_from_pdf(cls, pdf_path):
        """Extracts yaks data from PDF using pypdf."""
        pypdf = attempt_pypdf_install()
        if not pypdf:
            logger.warning("pypdf is unavailable. Using fallback OCR data.")
            return []

        try:
            reader = pypdf.PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text_content = page.extract_text()
                if text_content:
                    text += text_content + "\n"
            
            lines = text.split('\n')
            results = []
            
            # Row match regex
            row_regex = re.compile(
                r'^Yak\s+(\d+)\s+(.*?)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\s+(\d+)\s+(\d+)\s+(Artificial\s+Insemination|Natural)\s+([\d.]+(?:\s*cm)?)\s+([\d.]+(?:\s*cm)?)\s+([\d.]+(?:\s*cm)?)\s+(\d+)\s+(\d+)\s+(\d+(?:\s*kg)?)\s+(.*?)\s+(\d+\.\d+)$',
                re.IGNORECASE
            )
            
            for line in lines:
                line = line.strip()
                if not line.startswith("Yak"):
                    continue
                match = row_regex.match(line)
                if match:
                    groups = match.groups()
                    results.append({
                        "yak_id": f"Yak {groups[0]}",
                        "name": cls.clean_name(groups[1]),
                        "date_of_birth": cls.parse_date(groups[2]),
                        "dam": groups[3],
                        "sire": groups[4],
                        "breeding_method": groups[5],
                        "vulva_length": cls.clean_numeric(groups[6]),
                        "vaginal_depth": cls.clean_numeric(groups[7]),
                        "distance_to_cervix": cls.clean_numeric(groups[8]),
                        "vaginal_diameter": cls.clean_numeric(groups[9]),
                        "parity": cls.clean_numeric(groups[10]),
                        "body_weight": cls.clean_numeric(groups[11]),
                        "description": groups[12].strip(),
                        "vagina_temperature": cls.clean_numeric(groups[13])
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error parsing PDF file: {e}")
            return []

    @classmethod
    def get_analytics_data(cls):
        """Main method to load, clean, and validate data."""
        pdf_path = cls.find_pdf_file()
        if pdf_path:
            logger.info(f"Found PDF file: {pdf_path}")
            data = cls.extract_from_pdf(pdf_path)
            if data and len(data) > 0:
                logger.info(f"Extracted {len(data)} records from PDF successfully.")
                return data
            else:
                logger.warning("PDF parsing yielded 0 records. Using fallback OCR data.")
        else:
            logger.warning("PDF file not found in candidates. Using fallback OCR data.")
            
        return FALLBACK_DATA
