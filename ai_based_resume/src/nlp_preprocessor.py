"""
NLP Preprocessor Module
Provides text normalization, tokenization, lemmatization, and specialized cleaning
preserving technical and programming tokens (e.g., C++, .NET, CI/CD, Node.js).
"""

import re
import string
from typing import List, Set
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Load spaCy pipeline once
try:
    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None

# Load NLTK stopwords and lemmatizer
try:
    _STOPWORDS = set(stopwords.words("english"))
except Exception:
    _STOPWORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
        "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
        "what", "which", "who", "whom", "this", "that", "these", "those", "am",
        "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
        "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or",
        "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
        "against", "between", "into", "through", "during", "before", "after", "above",
        "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under"
    }

_LEMMATIZER = WordNetLemmatizer()

# Preserve tech terms mapping (temporary token placeholders during punctuation stripping)
TECH_TOKEN_MAP = {
    r'\bc\+\+': 'cplusplus',
    r'\bc\#': 'csharp',
    r'\.net\b': 'dotnet',
    r'\bnode\.js\b': 'nodejs',
    r'\breact\.js\b': 'reactjs',
    r'\bvue\.js\b': 'vuejs',
    r'\bangular\.js\b': 'angularjs',
    r'\bci\/cd\b': 'cicd',
    r'\btcp\/ip\b': 'tcpip',
    r'\bpower\s+bi\b': 'powerbi',
    r'\bscikit-learn\b': 'scikitlearn',
    r'\bnext\.js\b': 'nextjs',
}

REVERSE_TECH_MAP = {v: k.replace(r'\b', '').replace('\\', '').replace('+', '+').replace('#', '#') for k, v in TECH_TOKEN_MAP.items()}


def protect_tech_tokens(text: str) -> str:
    """Protects composite tech tokens from regex splitting."""
    for pattern, placeholder in TECH_TOKEN_MAP.items():
        text = re.sub(pattern, placeholder, text, flags=re.IGNORECASE)
    return text


def clean_text_for_nlp(text: str) -> str:
    """
    Standard text normalization:
    - Removes emails, phone numbers, and URLs
    - Normalizes case and punctuation while protecting tech tokens
    - Strips non-alphanumeric noise
    """
    if not text:
        return ""
    
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text)
    # Remove phone numbers
    text = re.sub(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', ' ', text)
    
    # Protect specialized programming terms
    text = protect_tech_tokens(text)
    
    # Replace punctuation characters with spaces, except hyphens inside words
    text = re.sub(r'[^\w\s-]', ' ', text)
    text = re.sub(r'(?<!\w)-|-(?!\w)', ' ', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess_text(text: str, remove_stop: bool = True, lemmatize: bool = True) -> str:
    """
    Complete NLP preprocessing pipeline:
    1. Specialized cleaning
    2. Tokenization
    3. Stopword removal (optional)
    4. Lemmatization (optional)
    Returns: cleaned and normalized text string suitable for TF-IDF / vectorization.
    """
    cleaned = clean_text_for_nlp(text)
    if not cleaned:
        return ""
    
    if _NLP is not None:
        doc = _NLP(cleaned)
        tokens = []
        for token in doc:
            if remove_stop and (token.is_stop or token.text in _STOPWORDS):
                continue
            if token.is_punct or token.is_space:
                continue
            word = token.lemma_ if lemmatize else token.text
            if len(word) > 1 or word in {"c", "r"}:  # retain single-letter tech languages like C, R
                tokens.append(word)
        return " ".join(tokens)
    else:
        # Fallback using NLTK
        raw_tokens = word_tokenize(cleaned)
        tokens = []
        for tok in raw_tokens:
            if remove_stop and tok in _STOPWORDS:
                continue
            word = _LEMMATIZER.lemmatize(tok) if lemmatize else tok
            if len(word) > 1 or word in {"c", "r"}:
                tokens.append(word)
        return " ".join(tokens)


def get_tokens(text: str) -> List[str]:
    """Helper to return a list of preprocessed tokens."""
    preprocessed = preprocess_text(text)
    return preprocessed.split() if preprocessed else []
