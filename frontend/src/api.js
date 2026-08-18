import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getSummary = async () => {
  const response = await api.get("/api/analytics/summary");
  return response.data;
};

export const getYearlyTrend = async () => {
  const response = await api.get("/api/analytics/yearly-trend");
  return response.data;
};

export const getDomainDistribution = async () => {
  const response = await api.get("/api/analytics/domain-distribution");
  return response.data;
};

export const getTopicDistribution = async () => {
  const response = await api.get("/api/analytics/topic-distribution");
  return response.data;
};

export const getCitationAnalysis = async () => {
  const response = await api.get("/api/analytics/citation-analysis");
  return response.data;
};

export const getEmergingTopics = async () => {
  const response = await api.get("/api/analytics/emerging-topics");
  return response.data;
};

export const getTopCited = async () => {
  const response = await api.get("/api/analytics/top-cited");
  return response.data;
};

export const getPublications = async (limit = 20, offset = 0) => {
  const response = await api.get("/api/publications/", {
    params: {
      limit,
      offset,
    },
  });

  return response.data;
};

export default api;
