"""
Analytics & Visualization Module
Generates interactive Plotly figures for candidate match reporting,
radar skill coverage, and recruiter leaderboard comparisons.
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def create_gauge_chart(score: float, title: str = "Overall Match Score") -> go.Figure:
    """
    Creates an interactive gauge meter showing the composite match score.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': '#1E293B', 'family': 'Arial, sans-serif'}},
        number={'suffix': "%", 'font': {'size': 44, 'color': '#0F172A', 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#2563EB", 'thickness': 0.28},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 40], 'color': '#FEE2E2'},
                {'range': [40, 70], 'color': '#FEF3C7'},
                {'range': [70, 100], 'color': '#DCFCE7'}
            ],
            'threshold': {
                'line': {'color': "#059669", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=25, r=25, t=50, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif")
    )
    return fig


def create_radar_chart(candidate_categorized: Dict[str, List[str]], job_categorized: Dict[str, List[str]]) -> go.Figure:
    """
    Generates a radar chart comparing skill counts between candidate and job across categories.
    """
    categories = [
        "Programming Languages",
        "Data Science, ML & AI",
        "Data Engineering & Databases",
        "Cloud & DevOps",
        "Web & Backend Frameworks",
        "Soft Skills"
    ]
    
    cand_counts = []
    job_counts = []
    
    for cat in categories:
        cand_skills = candidate_categorized.get(cat, [])
        job_skills = job_categorized.get(cat, [])
        cand_counts.append(len(cand_skills))
        job_counts.append(len(job_skills))
        
    # Close radar loop
    radar_categories = categories + [categories[0]]
    cand_counts = cand_counts + [cand_counts[0]]
    job_counts = job_counts + [job_counts[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=job_counts,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(239, 68, 68, 0.2)',
        line=dict(color='#EF4444', width=2),
        name='Job Requirements'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=cand_counts,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.25)',
        line=dict(color='#2563EB', width=2.5),
        name='Candidate Profile'
    ))
    
    max_val = max(max(cand_counts), max(job_counts), 3)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val + 1])
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=340,
        margin=dict(l=35, r=35, t=30, b=50),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_leaderboard_chart(ranked_results: List[Dict[str, Any]]) -> go.Figure:
    """
    Creates a horizontal comparative bar chart for batch recruiter ranking.
    """
    if not ranked_results:
        return go.Figure()
        
    top_candidates = ranked_results[:10][::-1]  # Reverse for ascending bottom-to-top layout
    
    names = [f"#{c['rank']} {c['metadata']['name']} ({c['filename']})" for c in top_candidates]
    composite_scores = [c['composite_score'] for c in top_candidates]
    skill_scores = [c['scores']['skill_match'] for c in top_candidates]
    tfidf_scores = [c['scores']['tfidf_similarity'] for c in top_candidates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=names,
        x=composite_scores,
        name='Composite Match',
        orientation='h',
        marker=dict(color='#2563EB'),
        text=[f"{s}%" for s in composite_scores],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        y=names,
        x=skill_scores,
        name='Skill Match',
        orientation='h',
        marker=dict(color='#10B981'),
        visible='legendonly'
    ))
    
    fig.add_trace(go.Bar(
        y=names,
        x=tfidf_scores,
        name='TF-IDF Cosine Similarity',
        orientation='h',
        marker=dict(color='#8B5CF6'),
        visible='legendonly'
    ))
    
    fig.update_layout(
        barmode='group',
        xaxis=dict(range=[0, 105], title="Score (%)"),
        height=max(360, len(top_candidates) * 45),
        margin=dict(l=20, r=20, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig
