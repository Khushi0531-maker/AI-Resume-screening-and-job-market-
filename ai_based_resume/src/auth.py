"""
Authentication & User Preferences Module
Manages user authentication, registration, session profiles,
and personalized job preferences persisted in JSON storage.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional

USER_DB_FILE = "data/users.json"


def _hash_password(password: str) -> str:
    """Hashes a password with SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _load_users() -> Dict[str, Any]:
    """Loads existing user database or initializes default demo accounts."""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Default seed accounts
    default_users = {
        "candidate@jobseeker.com": {
            "name": "Alex Morgan",
            "email": "candidate@jobseeker.com",
            "password_hash": _hash_password("user123"),
            "role": "Candidate / Job Seeker",
            "preferences": {
                "preferred_roles": ["Data Scientist", "Machine Learning Engineer"],
                "experience_level": "Mid-Level (3-5 years)",
                "work_mode": "Hybrid",
                "target_location": "Remote / Hybrid",
                "core_skills": ["Python", "PyTorch", "Scikit-Learn", "SQL", "Docker"]
            }
        },
        "recruiter@company.com": {
            "name": "Sarah Recruiter",
            "email": "recruiter@company.com",
            "password_hash": _hash_password("admin123"),
            "role": "Recruiter / Hiring Manager",
            "preferences": {
                "preferred_roles": ["Senior Data Scientist", "Full Stack Software Engineer"],
                "experience_level": "Senior Level (5+ years)",
                "work_mode": "Remote",
                "target_location": "Worldwide",
                "core_skills": ["Python", "React", "AWS", "PostgreSQL"]
            }
        }
    }
    _save_users(default_users)
    return default_users


def _save_users(users: Dict[str, Any]) -> None:
    """Persists user dictionary to JSON file."""
    os.makedirs(os.path.dirname(USER_DB_FILE), exist_ok=True)
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Validates user credentials. Returns user dict on success, None on failure.
    """
    email_clean = email.strip().lower()
    users = _load_users()
    if email_clean in users:
        user = users[email_clean]
        if user["password_hash"] == _hash_password(password):
            return user
    return None


def register_user(name: str, email: str, password: str, role: str) -> bool:
    """
    Registers a new user account. Returns True if created, False if email already exists.
    """
    email_clean = email.strip().lower()
    users = _load_users()
    if email_clean in users:
        return False
        
    users[email_clean] = {
        "name": name.strip(),
        "email": email_clean,
        "password_hash": _hash_password(password),
        "role": role,
        "preferences": {
            "preferred_roles": ["Data Scientist"] if "Candidate" in role else ["Senior Software Engineer"],
            "experience_level": "Mid-Level (3-5 years)",
            "work_mode": "Remote",
            "target_location": "Remote / Hybrid",
            "core_skills": ["Python", "SQL"]
        }
    }
    _save_users(users)
    return True


def update_user_preferences(email: str, preferences: Dict[str, Any]) -> bool:
    """Updates stored job preferences for a given user."""
    email_clean = email.strip().lower()
    users = _load_users()
    if email_clean in users:
        users[email_clean]["preferences"] = preferences
        _save_users(users)
        return True
    return False
