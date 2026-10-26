"""
Unit Tests for AI Resume Screening and Job Matching System
Tests data extraction, NLP preprocessing, skill extraction, entity parsing, and matching logic.
"""

import os
import unittest
from src.data_extractor import extract_text, extract_text_from_docx, extract_text_from_txt
from src.nlp_preprocessor import preprocess_text, clean_text_for_nlp
from src.skill_extractor import extract_skills_from_text, get_skill_extractor
from src.entity_parser import parse_resume_metadata, extract_email, extract_phone
from src.matcher import compute_tfidf_similarity, match_resume_to_job, batch_match_resumes
from src.analytics import create_gauge_chart, create_radar_chart, create_leaderboard_chart
from src.auth import authenticate_user, register_user, update_user_preferences


class TestResumeScreeningPipeline(unittest.TestCase):

    def setUp(self):
        self.sample_resume = """
        Alex Morgan
        alex.morgan@email.com | (555) 234-5678
        linkedin.com/in/alexmorgan-ai
        
        Senior Data Scientist with 4+ years of experience in Machine Learning and NLP.
        Proficient in Python, PyTorch, Scikit-Learn, SQL, and Docker on AWS.
        Master of Science in Computer Science.
        """
        self.sample_job = """
        Looking for a Senior Data Scientist with 3+ years experience.
        Must have strong skills in Python, Scikit-Learn, PyTorch, NLP, SQL, and AWS.
        Bachelor or Master degree in Computer Science required.
        """

    def test_text_cleaning_and_tech_tokens(self):
        raw_text = "I have 3 years of C++, .NET, and CI/CD experience with Node.js."
        cleaned = clean_text_for_nlp(raw_text)
        self.assertIn("cplusplus", cleaned)
        self.assertIn("dotnet", cleaned)
        self.assertIn("cicd", cleaned)
        self.assertIn("nodejs", cleaned)

    def test_nlp_preprocessor(self):
        processed = preprocess_text("Developing modern machine learning and deep learning models in Python!")
        self.assertIsInstance(processed, str)
        self.assertIn("machine", processed)
        self.assertIn("learning", processed)

    def test_skill_extraction(self):
        skills_data = extract_skills_from_text(self.sample_resume)
        skills = skills_data["flat_skills"]
        self.assertIn("Python", skills)
        self.assertIn("PyTorch", skills)
        self.assertIn("Scikit-Learn", skills)
        self.assertIn("SQL", skills)
        self.assertIn("Docker", skills)
        self.assertIn("AWS", skills)
        self.assertTrue(len(skills_data["categorized"]) > 0)

    def test_entity_parser(self):
        metadata = parse_resume_metadata(self.sample_resume)
        self.assertEqual(metadata["email"], "alex.morgan@email.com")
        self.assertIn("555", metadata["phone"])
        self.assertIn("alex", metadata["name"].lower())
        self.assertIn("morgan", metadata["name"].lower())
        self.assertGreaterEqual(metadata["experience_years"], 4.0)

    def test_tfidf_similarity(self):
        sim = compute_tfidf_similarity(self.sample_resume, self.sample_job)
        self.assertGreater(sim, 15.0)
        self.assertLessEqual(sim, 100.0)

    def test_matcher_output(self):
        result = match_resume_to_job(self.sample_resume, self.sample_job)
        self.assertIn("composite_score", result)
        self.assertIn("scores", result)
        self.assertIn("skills", result)
        self.assertGreater(result["composite_score"], 60.0)
        self.assertIn("Python", result["skills"]["matched"])

    def test_batch_matching(self):
        resumes = [
            {"filename": "alex.txt", "text": self.sample_resume},
            {"filename": "irrelevant.txt", "text": "Chef with culinary experience in Italian baking and pastries."}
        ]
        ranked = batch_match_resumes(resumes, self.sample_job)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["filename"], "alex.txt")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertGreater(ranked[0]["composite_score"], ranked[1]["composite_score"])

    def test_docx_extraction(self):
        docx_path = "data/sample_resumes/alex_morgan_sample.docx"
        if os.path.exists(docx_path):
            text = extract_text_from_docx(docx_path)
            self.assertIn("Alex Morgan", text)
            self.assertIn("Python", text)

    def test_analytics_generation(self):
        gauge = create_gauge_chart(85.5)
        self.assertIsNotNone(gauge)
        radar = create_radar_chart({"Programming Languages": ["Python"]}, {"Programming Languages": ["Python", "C++"]})
        self.assertIsNotNone(radar)

    def test_auth_and_preferences(self):
        user = authenticate_user("candidate@jobseeker.com", "user123")
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Alex Morgan")
        
        # Test update preferences
        new_prefs = {"preferred_roles": ["Machine Learning Engineer"], "work_mode": "Remote"}
        updated = update_user_preferences("candidate@jobseeker.com", new_prefs)
        self.assertTrue(updated)
        
        # Re-fetch user
        user_updated = authenticate_user("candidate@jobseeker.com", "user123")
        self.assertEqual(user_updated["preferences"]["preferred_roles"], ["Machine Learning Engineer"])


if __name__ == "__main__":
    unittest.main()
