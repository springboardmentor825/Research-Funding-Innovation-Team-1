import axios from "axios";

// ============================================================
// API CONFIGURATION
// ============================================================
// Primary: FastAPI backend at localhost:8000
// Fallback: Local JSON file (pre-generated for researcher intelligence)

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

// ============================================================
// LOCAL JSON FALLBACK (pre-generated researcher data)
// ============================================================

import researcherData from "./data/researcher_intelligence.json";

// ============================================================
// RESEARCHER INTELLIGENCE API
// ============================================================

/**
 * Fetch all researchers sorted by overall score.
 * Falls back to local JSON if backend is unreachable.
 */
export const getAllResearchers = async () => {
  try {
    const response = await api.get("/api/researcher-intelligence");
    return response.data;
  } catch (error) {
    console.warn("Backend unavailable, using local JSON data:", error.message);
    const sorted = [...researcherData].sort(
      (a, b) => b.overall_researcher_score - a.overall_researcher_score
    );
    return {
      total_researchers: sorted.length,
      researchers: sorted,
    };
  }
};

/**
 * Fetch a single researcher by ID.
 */
export const getResearcherById = async (id) => {
  try {
    const response = await api.get(`/api/researcher-intelligence/${id}`);
    return response.data;
  } catch (error) {
    console.warn("Backend unavailable, using local JSON data:", error.message);
    return researcherData.find((r) => r.researcher_id === id) || null;
  }
};

/**
 * Get local data directly (no network call).
 */
export const getLocalData = () => {
  return [...researcherData].sort(
    (a, b) => b.overall_researcher_score - a.overall_researcher_score
  );
};

// ============================================================
// PUBLICATION TREND ANALYSIS API (requires MySQL)
// ============================================================

/**
 * Fetch publication summary statistics.
 * Returns null if backend/database unavailable.
 */
export const getSummary = async () => {
  try {
    const response = await api.get("/api/analytics/summary");
    return response.data;
  } catch (error) {
    console.warn("Publication analytics unavailable:", error.message);
    return null;
  }
};

/**
 * Fetch yearly publication trend data.
 */
export const getYearlyTrend = async () => {
  try {
    const response = await api.get("/api/analytics/yearly-trend");
    return response.data;
  } catch (error) {
    console.warn("Yearly trend unavailable:", error.message);
    return { yearly_trend: [] };
  }
};

/**
 * Fetch domain distribution data.
 */
export const getDomainDistribution = async () => {
  try {
    const response = await api.get("/api/analytics/domain-distribution");
    return response.data;
  } catch (error) {
    console.warn("Domain distribution unavailable:", error.message);
    return { domain_distribution: [] };
  }
};

/**
 * Fetch topic distribution data.
 */
export const getTopicDistribution = async () => {
  try {
    const response = await api.get("/api/analytics/topic-distribution");
    return response.data;
  } catch (error) {
    console.warn("Topic distribution unavailable:", error.message);
    return { topics: [] };
  }
};

/**
 * Fetch citation analysis data.
 */
export const getCitationAnalysis = async () => {
  try {
    const response = await api.get("/api/analytics/citation-analysis");
    return response.data;
  } catch (error) {
    console.warn("Citation analysis unavailable:", error.message);
    return null;
  }
};

/**
 * Fetch emerging topics data.
 */
export const getEmergingTopics = async () => {
  try {
    const response = await api.get("/api/analytics/emerging-topics");
    return response.data;
  } catch (error) {
    console.warn("Emerging topics unavailable:", error.message);
    return { emerging_topics: [] };
  }
};

/**
 * Fetch top cited publications.
 */
export const getTopCited = async () => {
  try {
    const response = await api.get("/api/analytics/top-cited");
    return response.data;
  } catch (error) {
    console.warn("Top cited unavailable:", error.message);
    return { top_cited_publications: [] };
  }
};

/**
 * Fetch publications with pagination.
 */
export const getPublications = async (limit = 20, offset = 0) => {
  try {
    const response = await api.get("/api/publications/", {
      params: { limit, offset },
    });
    return response.data;
  } catch (error) {
    console.warn("Publications unavailable:", error.message);
    return { publications: [], total: 0 };
  }
};

export default api;
