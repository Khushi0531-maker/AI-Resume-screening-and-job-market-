"""
Entity Parser Module
Extracts candidate metadata including Name, Email, Phone, Social Profiles,
Education history, and Years of Experience using regex and spaCy NER.
"""

import re
from typing import Dict, Any, List, Optional
import spacy

try:
    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None

# Degree keywords
DEGREE_PATTERNS = [
    r"\bph\.?d\b", r"\bdoctorate\b", r"\bm\.?tech\b", r"\bm\.?s\.?\b",
    r"\bmaster(?:'s)?\b", r"\bmba\b", r"\bmca\b", r"\bb\.?tech\b",
    r"\bb\.?e\.?\b", r"\bb\.?s\.?\b", r"\bbachelor(?:'s)?\b",
    r"\bbca\b", r"\bbsc\b", r"\bmsc\b", r"\bdiploma\b", r"\bassociate(?:'s)?\b"
]

# Field of study
MAJOR_PATTERNS = [
    "computer science", "information technology", "data science",
    "artificial intelligence", "software engineering", "electrical engineering",
    "mechanical engineering", "electronics", "cyber security", "mathematics",
    "statistics", "business administration", "physics"
]


def extract_email(text: str) -> Optional[str]:
    """Extracts first valid email address from text."""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extracts first valid phone number from text."""
    # Matches formats like: +1 123-456-7890, (123) 456-7890, +91-9876543210, 9876543210
    pattern = r'(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b)'
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None


def extract_links(text: str) -> Dict[str, Optional[str]]:
    """Extracts LinkedIn and GitHub URLs from text."""
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', text, re.IGNORECASE)
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+', text, re.IGNORECASE)
    
    return {
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None
    }


def extract_name(text: str) -> str:
    """
    Extracts candidate name using spaCy NER and header line heuristics.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Candidate"
        
    # Heuristic 1: Inspect first 3 non-empty lines for a clear 2-3 word name
    ignored_headers = {
        "resume", "curriculum vitae", "cv", "profile", "contact",
        "summary", "experience", "education", "skills", "projects",
        "work experience", "about me", "objective"
    }
    
    for line in lines[:4]:
        clean_line = line.strip()
        if clean_line.lower() in ignored_headers:
            continue
        # If line contains email or phone, skip it
        if "@" in clean_line or re.search(r'\d{5,}', clean_line):
            continue
        # If 2 to 4 capitalized words and reasonable length
        words = clean_line.split()
        if 1 <= len(words) <= 4 and len(clean_line) <= 40:
            if all(w[0].isupper() or w.isupper() for w in words if w.isalpha()):
                return clean_line
                
    # Heuristic 2: spaCy PERSON entity on the top 600 characters
    if _NLP is not None:
        header_text = "\n".join(lines[:6])
        doc = _NLP(header_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                cand_name = ent.text.strip()
                if cand_name.lower() not in ignored_headers and len(cand_name.split()) in [2, 3, 4]:
                    return cand_name
                    
    # Fallback to first line if reasonably short
    return lines[0][:40] if lines else "Candidate"


def extract_education(text: str) -> List[Dict[str, str]]:
    """
    Identifies degree and major mentions within resume text.
    """
    found_degrees = set()
    for pattern in DEGREE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            found_degrees.add(m.strip().upper())
            
    found_majors = set()
    text_lower = text.lower()
    for major in MAJOR_PATTERNS:
        if major in text_lower:
            found_majors.add(major.title())
            
    return {
        "degrees": sorted(list(found_degrees)),
        "majors": sorted(list(found_majors))
    }


def extract_experience_years(text: str) -> float:
    """
    Estimates total years of experience from phrases like '5+ years experience'
    or ranges like '2018 - 2023'.
    """
    # Look for explicit statements e.g. "5+ years of experience" or "3 years in software"
    exp_patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*years?(?:\s+of)?\s+(?:experience|work\s+experience)',
        r'(?:experience|worked for)\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*years?'
    ]
    
    explicit_years = []
    for pat in exp_patterns:
        for match in re.findall(pat, text, re.IGNORECASE):
            try:
                explicit_years.append(float(match))
            except ValueError:
                pass
                
    if explicit_years:
        return max(explicit_years)
        
    # Heuristic: Detect year ranges (e.g., 2019 - 2024 or 2018 - Present)
    current_year = 2026
    year_ranges = re.findall(r'\b(20\d{2}|19\d{2})\s*(?:-|to|–)\s*(20\d{2}|present|current)\b', text, re.IGNORECASE)
    
    total_estimated = 0.0
    for start_yr, end_yr in year_ranges:
        try:
            s = int(start_yr)
            e = current_year if end_yr.lower() in ["present", "current"] else int(end_yr)
            if 0 <= (e - s) <= 30:  # reasonable single-job duration
                total_estimated += (e - s)
        except Exception:
            continue
            
    return min(total_estimated, 35.0)  # capped at 35 years


def parse_resume_metadata(text: str) -> Dict[str, Any]:
    """
    Aggregates all parsed candidate profile metadata into a structured dictionary.
    """
    links = extract_links(text)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": links.get("linkedin"),
        "github": links.get("github"),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text)
    }
