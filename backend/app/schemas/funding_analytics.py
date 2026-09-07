# backend/app/schemas/funding_analytics.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ScoreDistributionBucket(BaseModel):
    range: str
    min_score: int
    max_score: int
    count: int
    percentage: float

class LandscapeAnalytics(BaseModel):
    total_opportunities: int
    active_opportunities: int
    expired_opportunities: int
    closed_opportunities: int
    upcoming_deadlines_7d: int
    upcoming_deadlines_30d: int
    upcoming_deadlines_60d: int
    upcoming_deadlines_90d: int
    domain_distribution: Dict[str, int]
    technology_distribution: Dict[str, int]
    funder_distribution: Dict[str, int]
    funding_type_distribution: Dict[str, int]
    average_amount: Optional[float] = None
    median_amount: Optional[float] = None
    total_funding_amount: Optional[float] = None

class ScoreAnalytics(BaseModel):
    total_recommendations: int
    average_score: float
    median_score: float
    highest_score: float
    lowest_score: float
    excellent_match_count: int
    strong_match_count: int
    moderate_match_count: int
    weak_match_count: int
    poor_match_count: int
    score_distribution: List[ScoreDistributionBucket]

class DomainAnalyticsItem(BaseModel):
    domain: str
    recommendation_count: int
    average_score: float
    percentage: float
    positive_feedback_count: int
    negative_feedback_count: int

class FunderAnalyticsItem(BaseModel):
    funder: str
    opportunity_count: int
    average_score: float
    saves: int
    applications: int

class DeadlineAnalytics(BaseModel):
    within_7_days: int
    within_30_days: int
    within_60_days: int
    within_90_days: int
    expired: int
    no_deadline: int
    priority_recommendations: List[Dict[str, Any]] = []

class ActivityAnalytics(BaseModel):
    total_recommendations: int
    views: int
    saves: int
    dismissals: int
    relevant_feedback: int
    not_relevant_feedback: int
    applications: int
    feedback_coverage: float
    positive_feedback_rate: float
    negative_feedback_rate: float
    view_rate: float
    save_rate: float
    dismiss_rate: float
    application_rate: float

class TopKPrecisionItem(BaseModel):
    top_k: int
    evaluated_items: int
    relevant_count: int
    not_relevant_count: int
    precision: Optional[float] = None
    status: str

class PersonalizationPerformance(BaseModel):
    average_adjustment: float
    max_adjustment: float
    min_adjustment: float
    saved_items_count: int
    applied_items_count: int
    dismissed_items_count: int
    positive_signal_domains: List[str]
    negative_signal_domains: List[str]

class DiagnosticItem(BaseModel):
    check_name: str
    passed: bool
    details: str
    affected_count: int = 0

class DiagnosticsResult(BaseModel):
    valid_score_consistency_count: int
    invalid_score_consistency_count: int
    score_validation_rate: float
    evidence_complete_count: int
    evidence_incomplete_count: int
    evidence_validation_rate: float
    diagnostics_list: List[DiagnosticItem]

class HealthScore(BaseModel):
    score: int
    status: str
    strengths: List[str]
    warnings: List[str]
    calculation_breakdown: Dict[str, float]

class ResearcherFundingProfile(BaseModel):
    user_id: int
    full_name: str
    research_domain: str
    technology_areas: List[str]
    research_interests: List[str]
    funding_preferences: List[str]
    top_funding_domains: List[str]
    average_match_score: float
    strong_match_percentage: float
    application_activity: int

class GlobalAnalyticsResponse(BaseModel):
    funding_landscape: LandscapeAnalytics
    score_analytics: ScoreAnalytics
    domain_analytics: List[DomainAnalyticsItem]
    funder_analytics: List[FunderAnalyticsItem]
    deadline_analytics: DeadlineAnalytics
    recommendation_activity: ActivityAnalytics
    insights: List[str]

class ResearcherAnalyticsResponse(BaseModel):
    user_id: int
    researcher_funding_profile: ResearcherFundingProfile
    recommendation_summary: ScoreAnalytics
    score_distribution: List[ScoreDistributionBucket]
    top_recommendations: List[Dict[str, Any]]
    domain_analysis: List[DomainAnalyticsItem]
    deadline_analysis: DeadlineAnalytics
    activity_analysis: ActivityAnalytics
    personalization_analysis: PersonalizationPerformance
    evaluation: Dict[str, TopKPrecisionItem]
    diagnostics: DiagnosticsResult
    health_score: HealthScore
    insights: List[str]

class PerformanceResponse(BaseModel):
    user_id: int
    top_k_evaluation: Dict[str, TopKPrecisionItem]
    activity_metrics: ActivityAnalytics
    score_statistics: Dict[str, float]
    diagnostics: DiagnosticsResult
    health_score: HealthScore

class DashboardSummaryResponse(BaseModel):
    user_id: int
    kpis: Dict[str, Any]
    top_recommendations: List[Dict[str, Any]]
    upcoming_deadlines: List[Dict[str, Any]]
    domain_distribution: List[Dict[str, Any]]
    score_distribution: List[ScoreDistributionBucket]
    feedback_summary: ActivityAnalytics
    health_score: HealthScore
    alerts: List[str]
