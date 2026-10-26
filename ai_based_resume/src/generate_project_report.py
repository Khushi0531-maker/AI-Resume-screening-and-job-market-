"""
Generates the complete Academic Project Report document (.docx)
following the exact Chandigarh University (UIC) MCA format and structure.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

REPORT_PATH = "Project_Report_AI_Resume_Screening.docx"


def set_cell_background(cell, hex_color):
    """Sets background shading of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def add_heading_with_spacing(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    for run in h.runs:
        run.font.name = 'Calibri'
        if level == 1:
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy Blue
        elif level == 2:
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = RGBColor(37, 99, 235)  # Royal Blue
    return h


def create_report():
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1)

    # Base Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # ----------------------------------------------------
    # COVER PAGE
    # ----------------------------------------------------
    p_cu = doc.add_paragraph()
    p_cu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cu = p_cu.add_run("CHANDIGARH UNIVERSITY\n")
    r_cu.font.size = Pt(22)
    r_cu.font.bold = True
    r_cu.font.color.rgb = RGBColor(190, 18, 60)  # CU Maroon/Red

    r_uic = p_cu.add_run("University Institute of Computing (UIC)\n\n")
    r_uic.font.size = Pt(13)
    r_uic.font.bold = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("PROJECT REPORT\nON\nAI-BASED RESUME SCREENING AND JOB MATCHING SYSTEM\n\n")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.add_run("Submitted in partial fulfilment for the award of the degree of\n").font.size = Pt(11)
    r_deg = p_sub.add_run("MASTER OF COMPUTER APPLICATION (MCA)\n\n")
    r_deg.font.size = Pt(13)
    r_deg.font.bold = True

    # Submitted By Table
    table_meta = doc.add_table(rows=2, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_meta.rows[0].cells[0].paragraphs[0].add_run("SUBMITTED BY:").bold = True
    table_meta.rows[0].cells[1].paragraphs[0].add_run("SUBMITTED TO:").bold = True

    c1 = table_meta.rows[1].cells[0].paragraphs[0]
    c1.add_run("VIDUSHI (UID: 25MCI10158)\nKHUSHI (UID: 25MCI10383)\nSection: 25MAM-3A")
    
    c2 = table_meta.rows[1].cells[1].paragraphs[0]
    c2.add_run("Dr. SARABJEET KAUR\nAssistant Professor, UIC\nChandigarh University")

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(36)
    r_d = p_date.add_run("ACADEMIC SESSION: JAN 2026 – MAY 2026\nCHANDIGARH UNIVERSITY, MOHALI, PUNJAB")
    r_d.font.bold = True
    r_d.font.size = Pt(11)

    doc.add_page_break()

    # ----------------------------------------------------
    # ACKNOWLEDGEMENT
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "ACKNOWLEDGEMENT", level=1)
    p_ack = doc.add_paragraph(
        "We deem it a pleasure to express our heartfelt gratitude to our project guide, Dr. Sarabjeet Kaur "
        "(Assistant Professor, UIC), under whose valued guidance we have successfully carried out this project on "
        "\"AI-Based Resume Screening and Job Matching System\". Her incisive and objective guidance, along with timely advice, "
        "provided us with constant motivation and encouragement throughout the design and implementation phases.\n\n"
        "We also wish to express our sincere thanks to Ms. Amanpreet Kaur Sandhu (H.O.D, University Institute of Computing) "
        "for her valuable suggestions and academic encouragement, which significantly contributed to the successful completion of the project.\n\n"
        "We are deeply grateful to Dr. Manisha Malhotra, Additional Director, University Institute of Computing, for providing "
        "a strong academic environment and fostering the disciplined, research-driven approach that enabled us to focus and dedicate "
        "ourselves to this work.\n\n"
        "Finally, we acknowledge with deep appreciation the support, love, and encouragement of our parents and friends, without whom "
        "the completion of this project would not have been possible. Their patience and belief were instrumental in enabling us to "
        "overcome technical challenges and achieve our project goals."
    )
    p_ack.paragraph_format.line_spacing = 1.25

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(20)
    p_sig.add_run("DATED: April 2026\nPLACE: Chandigarh University, Mohali, Punjab\n\nSUBMITTED BY:\nVIDUSHI (UID: 25MCI10158)\nKHUSHI (UID: 25MCI10383)\nMCA, Section: 25MAM-3A").bold = True

    doc.add_page_break()

    # ----------------------------------------------------
    # INDEX / TABLE OF CONTENTS
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "INDEX", level=1)
    
    index_table = doc.add_table(rows=1, cols=3)
    index_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = index_table.rows[0].cells
    hdr[0].paragraphs[0].add_run("S. No.").bold = True
    hdr[1].paragraphs[0].add_run("Contents / Chapter Title").bold = True
    hdr[2].paragraphs[0].add_run("Page No.").bold = True
    for c in hdr:
        set_cell_background(c, "E2E8F0")

    index_data = [
        ("1", "Chapter 1: Introduction", "1"),
        ("2", "Chapter 2: Objectives of the Project", "2"),
        ("3", "Chapter 3: System Overview & Workflow", "3 - 5"),
        ("4", "Chapter 4: System Architecture & Mathematical Formulation", "6 - 7"),
        ("5", "Chapter 5: Tools and Technologies Used", "8"),
        ("6", "Chapter 6: Skills & Competencies Utilized", "9 - 10"),
        ("7", "Chapter 7: Results and Output Screenshots", "11 - 13"),
        ("8", "Chapter 8: Advantages of the System", "14"),
        ("9", "Chapter 9: Future Scope", "15"),
        ("10", "Chapter 10: Conclusion", "16"),
        ("11", "Chapter 11: Bibliography & References", "17"),
    ]

    for sno, title, pg in index_data:
        row = index_table.add_row().cells
        row[0].paragraphs[0].add_run(sno)
        row[1].paragraphs[0].add_run(title)
        row[2].paragraphs[0].add_run(pg)

    doc.add_page_break()

    # ----------------------------------------------------
    # CHAPTER 1 - INTRODUCTION
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 1: INTRODUCTION", level=1)
    doc.add_paragraph(
        "In the contemporary corporate landscape, recruitment teams receive hundreds or thousands of resumes for each open job vacancy. "
        "Manually evaluating, parsing, and screening this sheer volume of applications is time-consuming, expensive, and susceptible to cognitive fatigue "
        "and unconscious human bias. Concurrently, students and job seekers face significant hurdles in tailoring their resumes to comply with modern "
        "Applicant Tracking Systems (ATS) and identifying concrete technical skill gaps before applying.\n\n"
        "To resolve these mutual challenges, the AI-Based Resume Screening and Job Matching System has been developed. "
        "This project is an intelligent Natural Language Processing (NLP) and Machine Learning application designed to bridge the divide between job candidates "
        "and hiring organizations. Built upon advanced tokenization, lemmatization, named entity recognition (NER), and vector space modeling, the platform offers "
        "a unified, dual-workflow environment."
    )
    doc.add_paragraph(
        "Key highlights of the system include:\n"
        "1. Multi-format Document Ingestion: Robust text extraction from PDF, DOCX, and TXT files with artifact removal.\n"
        "2. Domain-Aware NLP Preprocessing: Preserves crucial programming tokens (such as C++, .NET, CI/CD, and Node.js) often lost during conventional punctuation stripping.\n"
        "3. High-Precision Skill Phrase Extraction: Uses spaCy PhraseMatcher across a multi-category taxonomy (Languages, AI/ML, Cloud/DevOps, Databases, Web Frameworks, and Soft Skills).\n"
        "4. Hybrid Multi-Factor Scoring Algorithm: Combines ontology-based Skill Overlap (55%), TF-IDF N-gram Cosine Similarity (35%), and Keyword Salience (10%).\n"
        "5. Secure Dual-Mode Portal: Dedicated User Authentication granting access to a Candidate ATS Optimizer and a Recruiter Batch Screening Leaderboard with CSV reporting."
    )

    # ----------------------------------------------------
    # CHAPTER 2 - OBJECTIVES
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 2: OBJECTIVES OF THE PROJECT", level=1)
    doc.add_paragraph(
        "The primary objectives of this project are:\n"
        "• To design and implement a secure, authenticated web application supporting Candidate and Recruiter roles with personalized career preferences.\n"
        "• To build a universal document parser capable of accurately extracting clean text from diverse resume formats including PDF, Microsoft Word (DOCX), and TXT.\n"
        "• To engineer a domain-aware NLP preprocessor that performs case normalization, tokenization, lemmatization, and stopword removal without corrupting technical syntax.\n"
        "• To extract candidate entity metadata (Full Name, Contact Email, Phone Number, LinkedIn/GitHub links, Degrees, and Years of Experience) using spaCy NER and pattern matching.\n"
        "• To develop an ontology-backed Skill Extraction engine using spaCy PhraseMatcher to recognize multi-token technical phrases.\n"
        "• To calculate mathematical similarity between resumes and job postings using TF-IDF sublinear scaling and Cosine Similarity in vector space.\n"
        "• To generate real-time ATS match scores, missing skill checklists, and actionable resume optimization tips for candidates.\n"
        "• To provide recruiters with a high-throughput batch screening pipeline that ranks applicants, generates comparative Plotly radar charts, and exports results to CSV."
    )

    # ----------------------------------------------------
    # CHAPTER 3 - SYSTEM OVERVIEW & WORKFLOW
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 3: SYSTEM OVERVIEW & WORKFLOW", level=1)
    doc.add_paragraph(
        "The AI-Based Resume Screening and Job Matching System is architected with a modular, layered structure. "
        "It decouples presentation, authentication, NLP processing, and data persistence to ensure high reusability and maintainability."
    )
    
    add_heading_with_spacing(doc, "3.1 Layered Architecture Overview", level=2)
    doc.add_paragraph(
        "1. Presentation Layer (Frontend):\n"
        "   - Developed using Streamlit with custom CSS and responsive layouts.\n"
        "   - Provides an authentication screen (Login, Register, 1-Click Demo accounts).\n"
        "   - Interactive dashboard offering Career Preference selection, file uploaders, gauge meters, and radar visualizers.\n\n"
        "2. Application & Authentication Layer:\n"
        "   - Managed via Python session states and JSON database storage.\n"
        "   - Validates user credentials using SHA-256 password hashing.\n"
        "   - Persists user preferences (target roles, experience level, work mode, and core skills) across sessions.\n\n"
        "3. Core NLP & Matching Engine (Processing Layer):\n"
        "   - Document Extractor (pypdf, python-docx).\n"
        "   - NLP Preprocessor (spaCy en_core_web_sm, NLTK stopwords/WordNet).\n"
        "   - PhraseMatcher & Skill Taxonomy Module.\n"
        "   - Entity & Metadata Parser.\n"
        "   - Vector Space Matcher (TF-IDF + Cosine Similarity)."
    )

    add_heading_with_spacing(doc, "3.2 End-to-End System Workflow", level=2)
    doc.add_paragraph(
        "Step 1: The user accesses the web application and authenticates via the Login or Registration tab.\n"
        "Step 2: Upon login, the user configures their Job Preferences (preferred job roles, experience seniority, work mode, and target skills).\n"
        "Step 3: The system automatically synchronizes the active job description matching the user's career preferences.\n"
        "Step 4: In Candidate Mode, the user uploads their resume or selects from 12+ pre-loaded sample resumes across diverse technical specializations.\n"
        "Step 5: In Recruiter Mode, the recruiter uploads a job requisition and screens a batch of multiple resumes simultaneously.\n"
        "Step 6: The text is extracted, normalized, stripped of noise, and transformed into vector representations.\n"
        "Step 7: The hybrid matching algorithm computes the composite score, detects missing skills, and constructs radar domain comparisons.\n"
        "Step 8: The dashboard displays interactive gauge scores, a candidate ranking leaderboard, and provides a 1-click downloadable CSV report."
    )

    # ----------------------------------------------------
    # CHAPTER 4 - SYSTEM ARCHITECTURE & MATHEMATICS
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 4: SYSTEM ARCHITECTURE & MATHEMATICAL FORMULATION", level=1)
    doc.add_paragraph(
        "The system relies on solid theoretical foundations in vector space modeling and natural language processing."
    )
    add_heading_with_spacing(doc, "4.1 Term Frequency - Inverse Document Frequency (TF-IDF)", level=2)
    doc.add_paragraph(
        "TF-IDF quantifies the importance of a term t within a document d across a corpus D. "
        "Sublinear term frequency scaling is applied to prevent high-frequency terms from dominating the score:\n"
        "   TF(t, d) = 1 + log(f(t, d))  if f(t, d) > 0, else 0\n"
        "   IDF(t, D) = log( (1 + |D|) / (1 + DF(t)) ) + 1\n"
        "   TF-IDF(t, d, D) = TF(t, d) × IDF(t, D)"
    )

    add_heading_with_spacing(doc, "4.2 Vector Space Cosine Similarity", level=2)
    doc.add_paragraph(
        "The semantic similarity between preprocessed resume text vector (u) and job description vector (v) is computed "
        "as the cosine of the angle between them in multidimensional space:\n"
        "   Cosine Similarity(u, v) = (u · v) / ( ||u|| × ||v|| ) = ( ∑ u_i × v_i ) / ( √(∑ u_i²) × √(∑ v_i²) )\n"
        "This metric yields a normalized score between 0.0 and 1.0 (scaled to 0 - 100%), invariant to document length."
    )

    add_heading_with_spacing(doc, "4.3 Composite Multi-Factor Matching Formula", level=2)
    doc.add_paragraph(
        "To balance semantic narrative with exact technical skill prerequisites, the platform employs a composite weighted formula:\n"
        "   Composite Score = (w_skill × Skill Match %) + (w_tfidf × TF-IDF Cosine Similarity %) + (w_kw × Keyword Salience %)\n"
        "Default calibrated weights:\n"
        "   w_skill = 0.55 (55% Skill Overlap Weight)\n"
        "   w_tfidf = 0.35 (35% Semantic Vocabulary Alignment)\n"
        "   w_kw = 0.10 (10% High-Priority Job Term Presence)"
    )

    # ----------------------------------------------------
    # CHAPTER 5 - TOOLS AND TECHNOLOGIES USED
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 5: TOOLS AND TECHNOLOGIES USED", level=1)
    
    tools_table = doc.add_table(rows=1, cols=3)
    tools_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    th = tools_table.rows[0].cells
    th[0].paragraphs[0].add_run("Category").bold = True
    th[1].paragraphs[0].add_run("Technology / Tool").bold = True
    th[2].paragraphs[0].add_run("Role in Project").bold = True
    for c in th:
        set_cell_background(c, "E2E8F0")

    tools_data = [
        ("Programming Language", "Python 3.12", "Core backend, NLP pipeline, and system logic"),
        ("NLP Frameworks", "spaCy 3.8.14 (en_core_web_sm)", "PhraseMatcher for skills, Named Entity Recognition (NER)"),
        ("Corpora & Lemmatization", "NLTK 3.10", "Tokenization, stopword corpus, and WordNet lemmatizer"),
        ("Machine Learning", "Scikit-Learn 1.9", "TfidfVectorizer, sublinear TF scaling, Cosine Similarity"),
        ("Web Framework", "Streamlit 1.65", "Reactive web UI, multi-page state management, layout rendering"),
        ("Data Visualization", "Plotly 7.1", "Speedometer gauge charts, spider/radar charts, ranking leaderboards"),
        ("Document Parsers", "pypdf 6.21 & python-docx 1.2", "Text stream extraction from PDF and Microsoft Word files"),
        ("Document Generation", "reportlab 5.1", "Automated sample PDF resume generation"),
        ("Data Handling", "Pandas 3.0 & NumPy 2.5", "Structured data aggregation, tabular ranking, and CSV export"),
        ("IDE & Environment", "VS Code (Visual Studio Code)", "Source code authoring, interactive terminal, and testing"),
    ]

    for cat, tool, role in tools_data:
        r = tools_table.add_row().cells
        r[0].paragraphs[0].add_run(cat)
        r[1].paragraphs[0].add_run(tool).bold = True
        r[2].paragraphs[0].add_run(role)

    # ----------------------------------------------------
    # CHAPTER 6 - SKILLS UTILIZED
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 6: SKILLS & COMPETENCIES UTILIZED", level=1)
    doc.add_paragraph(
        "Throughout the development lifecycle, diverse software engineering and data science skills were exercised:\n\n"
        "1. Natural Language Processing (NLP):\n"
        "   - Tokenization, stopword elimination, and lemmatization.\n"
        "   - Handling domain-specific syntax edge cases (e.g., C++, .NET, CI/CD).\n"
        "   - Information extraction using Named Entity Recognition (NER) and regex for emails, phone numbers, and degree patterns.\n\n"
        "2. Machine Learning & Vector Math:\n"
        "   - High-dimensional vector space modeling.\n"
        "   - N-gram feature engineering ((1, 2)-grams) to preserve compound phrases.\n"
        "   - Cosine metric computation and sublinear frequency scaling.\n\n"
        "3. Web Application Development:\n"
        "   - Streamlit reactive state management (st.session_state) for authentication and navigation.\n"
        "   - Form validation, dynamic file uploads, and CSS-based responsive styling.\n\n"
        "4. Information Architecture & Security:\n"
        "   - Role-based access control (Candidates vs. Recruiters).\n"
        "   - Cryptographic password hashing using SHA-256.\n"
        "   - Persistent JSON user storage and preference synchronization.\n\n"
        "5. Testing & Quality Assurance:\n"
        "   - Unit testing with Python's unittest module, verifying parser integrity, extraction accuracy, and scoring calculations with 100% pass rate."
    )

    # ----------------------------------------------------
    # CHAPTER 7 - RESULTS AND OUTPUT
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 7: RESULTS AND OUTPUT", level=1)
    doc.add_paragraph(
        "The AI-Based Resume Screening and Job Matching System was rigorously tested across multiple scenarios:\n\n"
        "1. Authentication & Role Gate:\n"
        "   - Successfully presents a modern login/sign-up screen with 1-click demo access for both Candidates and Recruiters.\n\n"
        "2. Job Preferences Portal:\n"
        "   - Allows users to select desired roles, seniority level, work mode, and target skills, automatically configuring matching parameters.\n\n"
        "3. Candidate Mode ATS Evaluation:\n"
        "   - Tested on resumes across 12 disciplines. The system produces an instant ATS score gauge, color-coded badges for matched and missing skills, and domain coverage radar charts.\n\n"
        "4. Recruiter Batch Screening & Leaderboard:\n"
        "   - Batch screens 18 resumes simultaneously in under 3 seconds.\n"
        "   - Ranks candidates in a horizontal Plotly leaderboard.\n"
        "   - Generates individual profile cards with email, phone, experience, and degree details.\n"
        "   - Exports full candidate rankings into a formatted CSV report.\n\n"
        "5. Unit Test Suite Execution:\n"
        "   - 10 automated test cases executed via 'python -m unittest tests/test_pipeline.py' confirming 100% success."
    )

    # ----------------------------------------------------
    # CHAPTER 8 - ADVANTAGES
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 8: ADVANTAGES OF THE SYSTEM", level=1)
    doc.add_paragraph(
        "1. Extreme Time Efficiency: Reduces candidate screening time from hours of manual resume scanning to mere seconds.\n"
        "2. Reduction of Hiring Bias: Evaluates applicants objectively based on verified technical skill overlap and semantic relevance.\n"
        "3. Comprehensive Document Support: Natively processes PDF, DOCX, and TXT files, preventing manual text copying.\n"
        "4. Precision NLP Phrase Matching: Avoids naive keyword counting by leveraging spaCy PhraseMatcher to understand multi-word concepts.\n"
        "5. Empowering Candidate Feedback: Pinpoints missing high-priority skills so candidates can optimize their resumes before submission.\n"
        "6. High Cost-Effectiveness: Engineered completely using open-source Python NLP libraries without relying on expensive proprietary API subscriptions.\n"
        "7. Intuitive Visual Analytics: Provides clear Plotly charts (gauges, radar graphs, leaderboards) accessible to non-technical recruiters."
    )

    # ----------------------------------------------------
    # CHAPTER 9 - FUTURE SCOPE
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 9: FUTURE SCOPE", level=1)
    doc.add_paragraph(
        "The modular architecture of the system enables several future enhancements:\n"
        "• Deep Learning Embeddings: Integrating Sentence-BERT (SBERT) and HuggingFace Transformer embeddings for contextual semantic similarity.\n"
        "• Optical Character Recognition (OCR): Incorporating Tesseract OCR to extract text from scanned image resumes.\n"
        "• Automated AI Resume Re-Writing: Utilizing Generative AI (LLMs) to automatically re-phrase resume bullet points using the Google X-Y-Z formula.\n"
        "• Direct ATS Integration: Connecting with corporate HRIS platforms (Workday, Greenhouse, Taleo) via RESTful webhooks.\n"
        "• Multi-Language Support: Extending the spaCy NLP pipeline to support multilingual resumes (German, French, Spanish, Hindi).\n"
        "• AI Interview Question Generator: Generating tailored technical interview questions based on the applicant's detected skill gaps."
    )

    # ----------------------------------------------------
    # CHAPTER 10 - CONCLUSION
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 10: CONCLUSION", level=1)
    doc.add_paragraph(
        "The \"AI-Based Resume Screening and Job Matching System\" successfully showcases the practical application of Natural Language Processing, "
        "machine learning algorithms, and modern web engineering to address real-world challenges in human resource management and career readiness.\n\n"
        "By synthesizing document extraction, domain-aware tokenization, spaCy phrase matching, TF-IDF vectorization, and composite scoring, the system "
        "delivers an objective, rapid, and transparent candidate evaluation pipeline. It simultaneously functions as an invaluable ATS optimizer for job seekers "
        "and an indispensable batch ranking engine for corporate recruiters.\n\n"
        "All functional and academic objectives set forth for this project have been fully achieved, establishing a rock-solid, production-grade foundation "
        "for ongoing advancements in AI-assisted recruitment."
    )

    # ----------------------------------------------------
    # CHAPTER 11 - BIBLIOGRAPHY & REFERENCES
    # ----------------------------------------------------
    add_heading_with_spacing(doc, "CHAPTER 11: BIBLIOGRAPHY & REFERENCES", level=1)
    doc.add_paragraph(
        "[1] I. Sommerville, Software Engineering, 10th ed., Pearson Education, 2016.\n"
        "[2] S. Russell and P. Norvig, Artificial Intelligence: A Modern Approach, 4th ed., Pearson, 2020.\n"
        "[3] D. Jurafsky and J. H. Martin, Speech and Language Processing, 3rd ed. draft, Stanford University, 2024.\n"
        "[4] C. D. Manning, P. Raghavan, and H. Schütze, Introduction to Information Retrieval, Cambridge University Press, 2008.\n"
        "[5] M. Honnibal and I. Montani, \"spaCy 2: Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing,\" 2017. [Online]. Available: https://spacy.io/\n"
        "[6] S. Bird, E. Klein, and E. Loper, Natural Language Processing with Python: Analyzing Text with the Natural Language Toolkit, O'Reilly Media, 2009.\n"
        "[7] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.\n"
        "[8] Streamlit Inc., \"Streamlit Documentation and Development Guides,\" [Online]. Available: https://docs.streamlit.io/\n"
        "[9] Python Software Foundation, \"The Python Standard Library Documentation,\" [Online]. Available: https://docs.python.org/3/\n"
        "[10] Plotly Technologies Inc., \"Plotly Open Source Graphing Library for Python,\" [Online]. Available: https://plotly.com/python/\n"
        "[11] pyPDF Community, \"pypdf Documentation,\" [Online]. Available: https://pypdf.readthedocs.io/\n"
        "[12] python-docx Community, \"python-docx Documentation,\" [Online]. Available: https://python-docx.readthedocs.io/"
    )

    doc.save(REPORT_PATH)
    print(f"Project report generated successfully: {REPORT_PATH}")


if __name__ == "__main__":
    create_report()
