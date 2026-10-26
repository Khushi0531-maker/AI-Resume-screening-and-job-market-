"""
Skill Extractor Module
Extracts technical, cloud, data science, web, and soft skills using
spaCy PhraseMatcher and regex-based token verification against a curated taxonomy.
"""

import re
from typing import Dict, List, Set, Any
import spacy
from spacy.matcher import PhraseMatcher

# Structured taxonomy of skills across multiple industry domains
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "c", "javascript", "typescript", "golang", "go",
        "rust", "ruby", "php", "sql", "r", "swift", "kotlin", "bash", "scala",
        "matlab", "dart", "html", "css", "shell", "powershell"
    ],
    "Data Science, ML & AI": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "scikit-learn", "tensorflow", "pytorch", "keras",
        "huggingface", "transformers", "llm", "llms", "large language models",
        "langchain", "opencv", "spacy", "nltk", "xgboost", "lightgbm", "catboost",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "statsmodels",
        "feature engineering", "neural networks", "supervised learning",
        "unsupervised learning", "reinforcement learning", "generative ai",
        "rag", "retrieval augmented generation", "fine-tuning", "bert", "gpt",
        "data mining", "sentiment analysis", "predictive modeling", "time series"
    ],
    "Data Engineering & Databases": [
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
        "cassandra", "dynamodb", "snowflake", "bigquery", "redshift", "databricks",
        "apache spark", "spark", "pyspark", "hadoop", "kafka", "airflow",
        "etl", "elt", "data pipeline", "elasticsearch", "neo4j", "hive", "dbt"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "microsoft azure", "gcp",
        "google cloud platform", "docker", "kubernetes", "k8s", "ci/cd", "ci cd",
        "jenkins", "github actions", "gitlab ci", "terraform", "ansible",
        "linux", "unix", "nginx", "apache", "prometheus", "grafana",
        "helm", "cloudformation", "serverless", "lambda"
    ],
    "Web & Backend Frameworks": [
        "react", "react.js", "angular", "angular.js", "vue", "vue.js", "next.js",
        "node.js", "nodejs", "express", "express.js", "django", "flask", "fastapi",
        "spring boot", "spring", "asp.net", ".net", "dotnet", "rest api", "restful api",
        "graphql", "microservices", "websockets", "tailwind css", "bootstrap",
        "html5", "css3", "redux"
    ],
    "Tools, Methodologies & Quality": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "unit testing", "pytest", "jest",
        "tdd", "test driven development", "ci/cd", "system design",
        "object oriented programming", "oop", "tableau", "power bi", "excel",
        "postman", "swagger", "openapi"
    ],
    "Soft Skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "collaboration", "adaptability", "time management",
        "analytical skills", "project management", "mentoring", "client management",
        "decision making", "conflict resolution", "negotiation", "creative thinking"
    ]
}

# Flattened lookup for canonical naming
CANONICAL_SKILL_MAP = {
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "scikit-learn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "rest api": "REST API",
    "restful api": "REST API",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "react.js": "React",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "git": "Git",
    "github": "GitHub",
    "c++": "C++",
    "c#": "C#",
    ".net": ".NET",
    "dotnet": ".NET",
    "power bi": "Power BI",
    "tableau": "Tableau",
}


class SkillExtractor:
    """
    Skill extraction engine leveraging spaCy PhraseMatcher and regex patterns.
    """
    def __init__(self, spacy_model="en_core_web_sm"):
        try:
            self.nlp = spacy.load(spacy_model)
        except Exception:
            self.nlp = spacy.blank("en")
        
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.all_phrases: Set[str] = set()
        
        # Build phrase patterns
        patterns = []
        for category, skills in SKILL_TAXONOMY.items():
            for skill in skills:
                clean_skill = skill.strip().lower()
                self.all_phrases.add(clean_skill)
                # Multi-token patterns for phrase matcher
                patterns.append(self.nlp.make_doc(clean_skill))
        
        self.matcher.add("SKILLS", patterns)

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extracts matched skills categorized by domain and as a consolidated set.
        """
        if not text:
            return {"flat_skills": set(), "categorized": {}, "count": 0}
            
        doc = self.nlp(text[:100000])  # limit length for safety
        matches = self.matcher(doc)
        
        detected_raw: Set[str] = set()
        for match_id, start, end in matches:
            span = doc[start:end]
            matched_text = span.text.strip().lower()
            detected_raw.add(matched_text)
            
        # Regex check for short / symbol-based tokens that spaCy tokenizer might split
        short_tokens = ["c++", "c#", ".net", "r", "c", "sql", "git", "aws", "gcp", "k8s"]
        for token in short_tokens:
            pattern = r'(?i)(?:\b|(?<=[^a-zA-Z0-9]))' + re.escape(token) + r'(?:\b|(?=[^a-zA-Z0-9]))'
            if re.search(pattern, text):
                detected_raw.add(token.lower())
                
        # Group into taxonomy categories and canonicalize names
        categorized: Dict[str, List[str]] = {}
        canonical_flat: Set[str] = set()
        
        for category, skills in SKILL_TAXONOMY.items():
            cat_matches = []
            for skill in skills:
                if skill.lower() in detected_raw:
                    canon_name = CANONICAL_SKILL_MAP.get(skill.lower(), skill.title())
                    cat_matches.append(canon_name)
                    canonical_flat.add(canon_name)
            if cat_matches:
                categorized[category] = sorted(list(set(cat_matches)))
                
        return {
            "flat_skills": sorted(list(canonical_flat)),
            "categorized": categorized,
            "count": len(canonical_flat)
        }


# Global singleton instance for efficient reuse across requests
_EXTRACTOR_INSTANCE = None

def get_skill_extractor() -> SkillExtractor:
    global _EXTRACTOR_INSTANCE
    if _EXTRACTOR_INSTANCE is None:
        _EXTRACTOR_INSTANCE = SkillExtractor()
    return _EXTRACTOR_INSTANCE

def extract_skills_from_text(text: str) -> Dict[str, Any]:
    """Helper functional wrapper for skill extraction."""
    extractor = get_skill_extractor()
    return extractor.extract_skills(text)
