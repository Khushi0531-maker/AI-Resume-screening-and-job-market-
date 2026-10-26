"""
Matcher Module
Implements the Hybrid NLP Job-Matching Engine:
- TF-IDF + Cosine Similarity (with unigram & bigram representation)
- Ontology-based Skill Overlap & Gap Analysis
- Composite Multi-factor Matching Score
- Actionable Feedback & ATS recommendations
"""

import math
from typing import Dict, Any, List, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.nlp_preprocessor import preprocess_text
from src.skill_extractor import extract_skills_from_text
from src.entity_parser import parse_resume_metadata


def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """
    Computes TF-IDF Cosine Similarity between resume and job description.
    Uses unigrams and bigrams with sublinear term frequency scaling.
    """
    clean_resume = preprocess_text(resume_text)
    clean_job = preprocess_text(job_text)
    
    if not clean_resume or not clean_job:
        return 0.0
        
    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_job])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Return scaled 0 - 100 percentage
        return round(float(sim) * 100.0, 2)
    except Exception:
        return 0.0


def extract_top_job_keywords(job_text: str, top_n: int = 15) -> List[Tuple[str, float]]:
    """
    Extracts the highest-weighted TF-IDF terms from the job description.
    """
    clean_job = preprocess_text(job_text)
    if not clean_job:
        return []
    try:
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=100)
        matrix = vec.fit_transform([clean_job])
        feature_names = vec.get_feature_names_out()
        scores = matrix.toarray()[0]
        sorted_indices = np.argsort(scores)[::-1][:top_n]
        return [(feature_names[i], round(float(scores[i]), 3)) for i in sorted_indices]
    except Exception:
        return []


def match_resume_to_job(
    resume_text: str,
    job_text: str,
    skill_weight: float = 0.55,
    tfidf_weight: float = 0.35,
    keyword_weight: float = 0.10
) -> Dict[str, Any]:
    """
    Performs comprehensive hybrid matching between a single resume and job description.
    """
    # 1. Profile metadata
    metadata = parse_resume_metadata(resume_text)
    
    # 2. Extract skills from both documents
    resume_skills_data = extract_skills_from_text(resume_text)
    job_skills_data = extract_skills_from_text(job_text)
    
    resume_skills_set = set(resume_skills_data["flat_skills"])
    job_skills_set = set(job_skills_data["flat_skills"])
    
    # Calculate skill overlaps
    matched_skills = sorted(list(resume_skills_set.intersection(job_skills_set)))
    missing_skills = sorted(list(job_skills_set.difference(resume_skills_set)))
    additional_skills = sorted(list(resume_skills_set.difference(job_skills_set)))
    
    if len(job_skills_set) > 0:
        skill_match_percentage = round((len(matched_skills) / len(job_skills_set)) * 100.0, 2)
    else:
        # If no specific taxonomy skills in JD, neutral baseline
        skill_match_percentage = 60.0
        
    # 3. TF-IDF Cosine Similarity
    tfidf_score = compute_tfidf_similarity(resume_text, job_text)
    
    # 4. Keyword presence score
    top_keywords = extract_top_job_keywords(job_text, top_n=15)
    clean_resume_text = preprocess_text(resume_text)
    if top_keywords:
        found_kw_count = sum(1 for kw, _ in top_keywords if kw in clean_resume_text)
        keyword_match_percentage = round((found_kw_count / len(top_keywords)) * 100.0, 2)
    else:
        keyword_match_percentage = tfidf_score
        
    # 5. Composite Score Calculation
    composite_score = round(
        (skill_weight * skill_match_percentage) +
        (tfidf_weight * tfidf_score) +
        (keyword_weight * keyword_match_percentage),
        2
    )
    composite_score = min(max(composite_score, 0.0), 100.0)
    
    # 6. Evaluation Tier & Recommendations
    if composite_score >= 80.0:
        tier = "High Match (Recommended)"
        tier_color = "#10B981"  # Emerald green
    elif composite_score >= 60.0:
        tier = "Moderate Match (Potential)"
        tier_color = "#F59E0B"  # Amber
    elif composite_score >= 40.0:
        tier = "Low Match (Needs Improvement)"
        tier_color = "#F97316"  # Orange
    else:
        tier = "Poor Match (Unqualified)"
        tier_color = "#EF4444"  # Red
        
    # Actionable advice
    recommendations = []
    if missing_skills:
        recommendations.append(
            f"Add missing required skills: {', '.join(missing_skills[:6])}."
        )
    if tfidf_score < 40.0:
        recommendations.append(
            "Incorporate more domain terminology and phrasing from the job description into your experience bullet points."
        )
    if len(resume_skills_data["flat_skills"]) < 5:
        recommendations.append(
            "Explicitly list your core technologies and frameworks in a dedicated 'Skills' section."
        )
    if not metadata.get("email"):
        recommendations.append("Ensure your contact email is clearly visible in standard text format.")
        
    return {
        "metadata": metadata,
        "composite_score": composite_score,
        "tier": tier,
        "tier_color": tier_color,
        "scores": {
            "composite": composite_score,
            "skill_match": skill_match_percentage,
            "tfidf_similarity": tfidf_score,
            "keyword_match": keyword_match_percentage,
        },
        "skills": {
            "matched": matched_skills,
            "missing": missing_skills,
            "additional": additional_skills,
            "candidate_skills": sorted(list(resume_skills_set)),
            "job_skills": sorted(list(job_skills_set)),
            "candidate_categorized": resume_skills_data["categorized"],
            "job_categorized": job_skills_data["categorized"],
        },
        "recommendations": recommendations,
        "top_job_keywords": top_keywords,
    }


def batch_match_resumes(
    resumes: List[Dict[str, Any]],
    job_text: str
) -> List[Dict[str, Any]]:
    """
    Ranks a list of candidate resumes against a single job description.
    Each resume item in `resumes` should be a dict with {'filename': str, 'text': str}.
    Returns a sorted list of matches ranked from highest to lowest composite score.
    """
    results = []
    for idx, res in enumerate(resumes):
        match_result = match_resume_to_job(res["text"], job_text)
        match_result["filename"] = res.get("filename", f"Resume_{idx+1}")
        match_result["candidate_id"] = idx + 1
        results.append(match_result)
        
    # Sort descending by composite score
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # Assign ranks
    for rank, item in enumerate(results, start=1):
        item["rank"] = rank
        
    return results
