import { useEffect, useState, useMemo } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import {
  getSummary,
  getYearlyTrend,
  getDomainDistribution,
  getTopicDistribution,
  getCitationAnalysis,
  getEmergingTopics,
  getTopCited,
  getPublications,
  getAllResearchers,
  getLocalData,
} from "./api";

import "./App.css";

// ============================================================
// COLOR PALETTE
// ============================================================

const COLORS = {
  blue: "#2563eb",
  green: "#10b981",
  purple: "#8b5cf6",
  orange: "#f97316",
  red: "#ef4444",
  teal: "#14b8a6",
  pink: "#ec4899",
  indigo: "#6366f1",
};

const PIE_COLORS = [
  COLORS.blue,
  COLORS.green,
  COLORS.purple,
  COLORS.orange,
  COLORS.teal,
  COLORS.pink,
  COLORS.red,
  COLORS.indigo,
];

// ============================================================
// HELPER FUNCTIONS
// ============================================================

const formatNumber = (n) => {
  if (n === null || n === undefined) return "0";
  return Number(n).toLocaleString();
};

const formatDecimal = (n) => {
  if (n === null || n === undefined) return "0";
  return Number(n).toLocaleString(undefined, { maximumFractionDigits: 2 });
};

const formatScore = (n) => {
  if (n === null || n === undefined) return "0.00";
  return Number(n).toFixed(2);
};

const getScoreColor = (score) => {
  if (score >= 60) return COLORS.green;
  if (score >= 40) return COLORS.blue;
  if (score >= 25) return COLORS.orange;
  return COLORS.red;
};

const getScoreLabel = (score) => {
  if (score >= 60) return "Strong";
  if (score >= 40) return "Moderate";
  if (score >= 25) return "Emerging";
  return "Limited";
};

const truncateLabel = (value) => {
  if (!value) return "";
  return value.length > 25 ? value.substring(0, 22) + "..." : value;
};

// ============================================================
// MAIN APP COMPONENT
// ============================================================

function App() {
  // Navigation - Two main modules
  const [activeModule, setActiveModule] = useState("Researcher Intelligence");
  const [activeTab, setActiveTab] = useState("Overview");

  // Publication Trend Analysis States
  const [summary, setSummary] = useState(null);
  const [yearlyTrend, setYearlyTrend] = useState([]);
  const [domains, setDomains] = useState([]);
  const [topics, setTopics] = useState([]);
  const [citation, setCitation] = useState(null);
  const [emergingTopics, setEmergingTopics] = useState([]);
  const [topCited, setTopCited] = useState([]);
  const [publications, setPublications] = useState([]);
  const [publicationsTotal, setPublicationsTotal] = useState(0);
  const [publicationsLimit] = useState(10);
  const [publicationsOffset, setPublicationsOffset] = useState(0);
  const [publicationsLoading, setPublicationsLoading] = useState(false);

  // Researcher Intelligence States
  const [researchers, setResearchers] = useState([]);
  const [selectedResearcher, setSelectedResearcher] = useState(null);
  const [compareIds, setCompareIds] = useState(["", ""]);

  // Common States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Load data on mount
  useEffect(() => {
    loadAllData();
  }, []);

  useEffect(() => {
    if (activeModule === "Publication Trends") {
      loadPublicationsData(publicationsOffset);
    }
  }, [publicationsOffset, activeModule]);

  const loadAllData = async () => {
    try {
      setLoading(true);
      setError("");

      // Load researcher intelligence data (always available)
      try {
        const researcherData = await getAllResearchers();
        setResearchers(researcherData.researchers || []);
      } catch {
        const local = getLocalData();
        setResearchers(local);
      }

      // Load publication trend data (requires MySQL)
      try {
        const [summaryData, yearlyData, domainData, topicData, citationData, emergingData, topCitedData] =
          await Promise.all([
            getSummary(),
            getYearlyTrend(),
            getDomainDistribution(),
            getTopicDistribution(),
            getCitationAnalysis(),
            getEmergingTopics(),
            getTopCited(),
          ]);

        setSummary(summaryData);
        setYearlyTrend(yearlyData.yearly_trend || []);
        setDomains(domainData.domain_distribution || []);
        setTopics(topicData.topics || []);
        setCitation(citationData);
        setEmergingTopics(emergingData.emerging_topics || []);
        setTopCited(topCitedData.top_cited_publications || []);
      } catch (pubErr) {
        console.log("Publication trend data not available (MySQL required):", pubErr.message);
      }
    } catch (err) {
      console.error("Data loading error:", err);
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  const loadPublicationsData = async (offset) => {
    try {
      setPublicationsLoading(true);
      const data = await getPublications(publicationsLimit, offset);
      setPublications(data.publications || []);
      setPublicationsTotal(data.total || 0);
    } catch (err) {
      console.log("Publications not available:", err.message);
    } finally {
      setPublicationsLoading(false);
    }
  };

  // ============================================================
  // COMPUTED DATA FOR CHARTS
  // ============================================================

  const summaryStats = useMemo(() => {
    if (researchers.length === 0) return null;
    const scores = researchers.map((r) => r.overall_researcher_score);
    return {
      total: researchers.length,
      avgOverall: scores.reduce((a, b) => a + b, 0) / scores.length,
      topScorer: researchers[0],
    };
  }, [researchers]);

  const scoreBarData = useMemo(() => {
    return researchers.map((r) => ({
      name: r.name.split(" ").slice(-1)[0],
      fullName: r.name,
      publication: r.publication_strength_score,
      patent: r.patent_strength_score,
      overall: r.overall_researcher_score,
    }));
  }, [researchers]);

  const expertiseAgg = useMemo(() => {
    const map = {};
    researchers.forEach((r) => {
      (r.top_expertise_areas || []).forEach((kw) => {
        map[kw] = (map[kw] || 0) + 1;
      });
    });
    return Object.entries(map)
      .map(([area, count]) => ({ area, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 12);
  }, [researchers]);

  const top10Domains = [...domains]
    .sort((a, b) => b.publication_count - a.publication_count)
    .slice(0, 10);

  const top15Topics = [...topics]
    .sort((a, b) => b.publication_count - a.publication_count)
    .slice(0, 15);

  const currentPage = Math.floor(publicationsOffset / publicationsLimit) + 1;
  const totalPages = Math.ceil(publicationsTotal / publicationsLimit) || 1;

  const handlePageChange = (direction) => {
    if (direction === "next" && publicationsOffset + publicationsLimit < publicationsTotal) {
      setPublicationsOffset(publicationsOffset + publicationsLimit);
    } else if (direction === "prev" && publicationsOffset - publicationsLimit >= 0) {
      setPublicationsOffset(publicationsOffset - publicationsLimit);
    }
  };

  // ============================================================
  // LOADING STATE
  // ============================================================

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <h2>Loading Research Intelligence Platform...</h2>
        <p>Analyzing publications, patents, and researcher profiles.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <div className="error-card">
          <h2>⚠ Dashboard Error</h2>
          <p>{error}</p>
          <button onClick={loadAllData}>Retry</button>
        </div>
      </div>
    );
  }

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="dashboard">
      {/* ========== HEADER ========== */}
      <header className="dashboard-header">
        <div className="header-title-section">
          <h1>RESEARCH INTELLIGENCE PLATFORM</h1>
          <p className="subtitle">
            Research Funding & Innovation Intelligence Platform
          </p>
        </div>
        <div className="header-status">
          <span className="status-dot"></span>
          {activeModule === "Researcher Intelligence"
            ? `${researchers.length} Researchers Analyzed`
            : "Publication Analytics"}
        </div>
      </header>

      {/* ========== MODULE SWITCHER ========== */}
      <nav className="module-nav">
        <button
          className={`module-btn ${activeModule === "Researcher Intelligence" ? "active" : ""}`}
          onClick={() => { setActiveModule("Researcher Intelligence"); setActiveTab("Overview"); setSelectedResearcher(null); }}
        >
          🧠 Researcher Intelligence
        </button>
        <button
          className={`module-btn ${activeModule === "Publication Trends" ? "active" : ""}`}
          onClick={() => { setActiveModule("Publication Trends"); setActiveTab("Overview"); }}
        >
          📊 Publication Trends
        </button>
      </nav>

      {/* ========== TAB NAVIGATION ========== */}
      <nav className="dashboard-nav">
        {activeModule === "Researcher Intelligence"
          ? ["Overview", "Rankings", "Score Analysis", "Expertise Map", "Compare"].map((tab) => (
              <button
                key={tab}
                className={`nav-item ${activeTab === tab ? "active" : ""}`}
                onClick={() => { setActiveTab(tab); setSelectedResearcher(null); }}
              >
                {tab}
              </button>
            ))
          : ["Overview", "Trends", "Domains", "Topics", "Citations", "Research Insights", "Publications"].map((tab) => (
              <button
                key={tab}
                className={`nav-item ${activeTab === tab ? "active" : ""}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))
        }
      </nav>

      {/* ========== MAIN CONTENT ========== */}
      <main className="dashboard-content">

        {/* ====================================================== */}
        {/* RESEARCHER INTELLIGENCE MODULE */}
        {/* ====================================================== */}
        {activeModule === "Researcher Intelligence" && activeTab === "Overview" && (
          <ResearcherOverview researchers={researchers} summaryStats={summaryStats} scoreBarData={scoreBarData} expertiseAgg={expertiseAgg} />
        )}

        {activeModule === "Researcher Intelligence" && activeTab === "Rankings" && !selectedResearcher && (
          <ResearcherRankings researchers={researchers} onSelect={setSelectedResearcher} />
        )}

        {activeModule === "Researcher Intelligence" && activeTab === "Rankings" && selectedResearcher && (
          <ResearcherDetail researcher={selectedResearcher} onBack={() => setSelectedResearcher(null)} />
        )}

        {activeModule === "Researcher Intelligence" && activeTab === "Score Analysis" && (
          <ScoreAnalysis researchers={researchers} scoreBarData={scoreBarData} />
        )}

        {activeModule === "Researcher Intelligence" && activeTab === "Expertise Map" && (
          <ExpertiseMap researchers={researchers} expertiseAgg={expertiseAgg} />
        )}

        {activeModule === "Researcher Intelligence" && activeTab === "Compare" && (
          <CompareView researchers={researchers} compareIds={compareIds} setCompareIds={setCompareIds} />
        )}

        {/* ====================================================== */}
        {/* PUBLICATION TRENDS MODULE */}
        {/* ====================================================== */}
        {activeModule === "Publication Trends" && activeTab === "Overview" && (
          <PubOverview summary={summary} />
        )}

        {activeModule === "Publication Trends" && activeTab === "Trends" && (
          <PubTrends yearlyTrend={yearlyTrend} />
        )}

        {activeModule === "Publication Trends" && activeTab === "Domains" && (
          <PubDomains top10Domains={top10Domains} />
        )}

        {activeModule === "Publication Trends" && activeTab === "Topics" && (
          <PubTopics top15Topics={top15Topics} />
        )}

        {activeModule === "Publication Trends" && activeTab === "Citations" && (
          <PubCitations citation={citation} yearlyTrend={yearlyTrend} topCited={topCited} />
        )}

        {activeModule === "Publication Trends" && activeTab === "Research Insights" && (
          <PubInsights emergingTopics={emergingTopics} />
        )}

        {activeModule === "Publication Trends" && activeTab === "Publications" && (
          <PubBrowser publications={publications} publicationsTotal={publicationsTotal} publicationsLoading={publicationsLoading} currentPage={currentPage} totalPages={totalPages} publicationsOffset={publicationsOffset} publicationsLimit={publicationsLimit} onPageChange={handlePageChange} />
        )}
      </main>

      {/* ========== FOOTER ========== */}
      <footer className="dashboard-footer">
        <p>Research Funding & Innovation Intelligence Platform</p>
        <span>50,000 OpenAlex Publications • 35,000 Indian Patents (2010) • 8 Researcher Profiles • TF-IDF Matching • FastAPI Backend</span>
      </footer>
    </div>
  );
}

// ============================================================
// RESEARCHER INTELLIGENCE COMPONENTS
// ============================================================

function ResearcherOverview({ researchers, summaryStats, scoreBarData, expertiseAgg }) {
  const scoreDistribution = useMemo(() => {
    const ranges = [
      { label: "Strong (60+)", count: 0 },
      { label: "Moderate (40-59)", count: 0 },
      { label: "Emerging (25-39)", count: 0 },
      { label: "Limited (<25)", count: 0 },
    ];
    researchers.forEach((r) => {
      const s = r.overall_researcher_score;
      if (s >= 60) ranges[0].count++;
      else if (s >= 40) ranges[1].count++;
      else if (s >= 25) ranges[2].count++;
      else ranges[3].count++;
    });
    return ranges.filter((r) => r.count > 0);
  }, [researchers]);

  return (
    <div className="tab-panel animate-fade-in">
      <section className="summary-grid four-col">
        <div className="summary-card blue">
          <div className="card-icon">👥</div>
          <div>
            <p>Researchers</p>
            <h2>{formatNumber(summaryStats?.total)}</h2>
            <span>Analyzed profiles</span>
          </div>
        </div>
        <div className="summary-card purple">
          <div className="card-icon">📊</div>
          <div>
            <p>Avg Overall Score</p>
            <h2>{formatScore(summaryStats?.avgOverall)}</h2>
            <span>Across all researchers</span>
          </div>
        </div>
        <div className="summary-card green">
          <div className="card-icon">🏆</div>
          <div>
            <p>Top Scorer</p>
            <h2 style={{ fontSize: "16px" }}>{summaryStats?.topScorer?.name?.split(" ").slice(-1)[0]}</h2>
            <span>Score: {formatScore(summaryStats?.topScorer?.overall_researcher_score)}</span>
          </div>
        </div>
        <div className="summary-card orange">
          <div className="card-icon">📝</div>
          <div>
            <p>Papers Matched</p>
            <h2>50,000</h2>
            <span>OpenAlex corpus</span>
          </div>
        </div>
      </section>

      <section className="chart-card">
        <h2>Researcher Score Comparison</h2>
        <p className="chart-description">Publication vs Patent vs Overall scores for each researcher.</p>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={scoreBarData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#475569" tick={{ fontSize: 12 }} />
              <YAxis stroke="#475569" domain={[0, 60]} />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} formatter={(value) => [formatScore(value), ""]} labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label} />
              <Legend />
              <Bar dataKey="publication" name="Publication Score" fill={COLORS.blue} radius={[4, 4, 0, 0]} barSize={18} />
              <Bar dataKey="patent" name="Patent Score" fill={COLORS.green} radius={[4, 4, 0, 0]} barSize={18} />
              <Bar dataKey="overall" name="Overall Score" fill={COLORS.purple} radius={[4, 4, 0, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="two-col-grid">
        <div className="chart-card">
          <h2>Score Distribution</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={scoreDistribution} cx="50%" cy="50%" outerRadius={100} dataKey="count" nameKey="label" label={({ label, count }) => `${label}: ${count}`} labelLine={true}>
                  {scoreDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="chart-card">
          <h2>Top Expertise Areas</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={expertiseAgg} layout="vertical" margin={{ top: 5, right: 30, left: 120, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" stroke="#475569" />
                <YAxis type="category" dataKey="area" stroke="#475569" tick={{ fontSize: 11, fill: "#334155" }} width={115} />
                <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
                <Bar dataKey="count" name="Researchers" fill={COLORS.teal} radius={[0, 6, 6, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="alert-card info">
        <strong>📋 Scope Limitations</strong>
        <p>Patent data is <strong>2010-only, India-only</strong> with no citation field. Researchers are matched via <strong>content-based TF-IDF similarity</strong>, not identity joins.</p>
      </section>
    </div>
  );
}

function ResearcherRankings({ researchers, onSelect }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Researcher Intelligence Rankings</h2>
        <p className="chart-description">All {researchers.length} researchers sorted by overall intelligence score. Click any row to view full detail.</p>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th style={{ width: "50px" }}>Rank</th>
                <th>Researcher</th>
                <th>Institution</th>
                <th>Publication Score</th>
                <th>Patent Score</th>
                <th>Overall Score</th>
                <th>Strength</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {researchers.map((r, idx) => (
                <tr key={r.researcher_id}>
                  <td><span className="rank-badge">#{idx + 1}</span></td>
                  <td className="paper-title">{r.name}</td>
                  <td>{r.institution}</td>
                  <td>
                    <span className="score-bar-inline">
                      <span className="score-bar-fill" style={{ width: `${Math.min(r.publication_strength_score * 1.5, 100)}%`, background: COLORS.blue }}></span>
                    </span>
                    <span className="score-text">{formatScore(r.publication_strength_score)}</span>
                  </td>
                  <td>
                    <span className="score-bar-inline">
                      <span className="score-bar-fill" style={{ width: `${Math.min(r.patent_strength_score * 1.5, 100)}%`, background: COLORS.green }}></span>
                    </span>
                    <span className="score-text">{formatScore(r.patent_strength_score)}</span>
                  </td>
                  <td>
                    <span className="overall-score-badge" style={{ background: getScoreColor(r.overall_researcher_score) }}>
                      {formatScore(r.overall_researcher_score)}
                    </span>
                  </td>
                  <td>
                    <span className="strength-tag" style={{ color: getScoreColor(r.overall_researcher_score) }}>
                      {getScoreLabel(r.overall_researcher_score)}
                    </span>
                  </td>
                  <td>
                    <button className="detail-btn" onClick={() => onSelect(r)}>View Details →</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function ResearcherDetail({ researcher, onBack }) {
  return (
    <div className="tab-panel animate-fade-in">
      <button className="back-btn" onClick={onBack}>← Back to Rankings</button>

      <section className="researcher-header-card">
        <div className="researcher-header-info">
          <h2>{researcher.name}</h2>
          <p className="researcher-institution">{researcher.institution}</p>
          <div className="researcher-tags">
            {(researcher.top_expertise_areas || []).slice(0, 5).map((kw, i) => (
              <span key={i} className="expertise-tag">{kw}</span>
            ))}
          </div>
        </div>
        <div className="researcher-score-display">
          <div className="big-score-circle" style={{ borderColor: getScoreColor(researcher.overall_researcher_score) }}>
            <span className="big-score-number">{formatScore(researcher.overall_researcher_score)}</span>
            <span className="big-score-label">Overall Score</span>
          </div>
        </div>
      </section>

      <section className="two-col-grid">
        <div className="score-breakdown-card">
          <h3>Score Breakdown</h3>
          <div className="breakdown-row">
            <span className="breakdown-label">Publication Strength</span>
            <div className="breakdown-bar-wrapper">
              <div className="breakdown-bar" style={{ width: `${Math.min(researcher.publication_strength_score * 1.67, 100)}%`, background: COLORS.blue }}></div>
            </div>
            <span className="breakdown-value">{formatScore(researcher.publication_strength_score)}</span>
          </div>
          <div className="breakdown-row">
            <span className="breakdown-label">Patent Strength</span>
            <div className="breakdown-bar-wrapper">
              <div className="breakdown-bar" style={{ width: `${Math.min(researcher.patent_strength_score * 1.67, 100)}%`, background: COLORS.green }}></div>
            </div>
            <span className="breakdown-value">{formatScore(researcher.patent_strength_score)}</span>
          </div>
          <div className="breakdown-row">
            <span className="breakdown-label">Overall (60% pub + 40% patent)</span>
            <div className="breakdown-bar-wrapper">
              <div className="breakdown-bar overall" style={{ width: `${Math.min(researcher.overall_researcher_score * 1.67, 100)}%`, background: getScoreColor(researcher.overall_researcher_score) }}></div>
            </div>
            <span className="breakdown-value">{formatScore(researcher.overall_researcher_score)}</span>
          </div>
        </div>
        <div className="explanation-card">
          <h3>Explainability</h3>
          <p>{researcher.explanation}</p>
        </div>
      </section>

      <section className="chart-card">
        <h2>📚 Top Matched Publications ({researcher.matched_publications_sample?.length || 0})</h2>
        <div className="table-container">
          <table>
            <thead><tr><th>#</th><th>Publication Title</th><th>Similarity</th><th>Citations</th></tr></thead>
            <tbody>
              {(researcher.matched_publications_sample || []).map((pub, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td className="paper-title">{pub.title}</td>
                  <td><span className="similarity-badge">{(pub.similarity * 100).toFixed(1)}%</span></td>
                  <td><span className="citation-badge orange">{formatNumber(pub.cited_by_count)}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="chart-card">
        <h2>💡 Top Matched Patents ({researcher.matched_patents_sample?.length || 0})</h2>
        <div className="table-container">
          <table>
            <thead><tr><th>#</th><th>Patent Title</th><th>Similarity</th><th>Status</th><th>Weight</th></tr></thead>
            <tbody>
              {(researcher.matched_patents_sample || []).map((pat, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td className="paper-title">{pat.title}</td>
                  <td><span className="similarity-badge">{(pat.similarity * 100).toFixed(1)}%</span></td>
                  <td><span className={`patent-status-badge ${pat.status_weight >= 0.8 ? "granted" : pat.status_weight >= 0.3 ? "pending" : "refused"}`}>{pat.status?.substring(0, 40)}</span></td>
                  <td><span className="weight-indicator">{pat.status_weight}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function ScoreAnalysis({ researchers, scoreBarData }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Publication vs Patent Score Comparison</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={scoreBarData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" stroke="#475569" tick={{ fontSize: 11 }} />
              <YAxis stroke="#475569" domain={[0, 60]} />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} formatter={(value) => [formatScore(value), ""]} labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName || label} />
              <Legend />
              <Bar dataKey="publication" name="Publication Score" fill={COLORS.blue} radius={[4, 4, 0, 0]} barSize={28} />
              <Bar dataKey="patent" name="Patent Score" fill={COLORS.green} radius={[4, 4, 0, 0]} barSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="chart-card">
        <h2>Detailed Score Comparison Table</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Researcher</th><th>Pub Score</th><th>Patent Score</th><th>Overall</th><th>Balance</th></tr>
            </thead>
            <tbody>
              {researchers.map((r) => {
                const balance = Math.abs(r.publication_strength_score - r.patent_strength_score);
                return (
                  <tr key={r.researcher_id}>
                    <td className="paper-title">{r.name}</td>
                    <td><span className="score-pill" style={{ background: COLORS.blue + "20", color: COLORS.blue }}>{formatScore(r.publication_strength_score)}</span></td>
                    <td><span className="score-pill" style={{ background: COLORS.green + "20", color: COLORS.green }}>{formatScore(r.patent_strength_score)}</span></td>
                    <td><span className="overall-score-badge" style={{ background: getScoreColor(r.overall_researcher_score) }}>{formatScore(r.overall_researcher_score)}</span></td>
                    <td><span className="balance-indicator" style={{ color: balance < 5 ? COLORS.green : balance < 15 ? COLORS.orange : COLORS.red }}>Δ {formatScore(balance)}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function ExpertiseMap({ researchers, expertiseAgg }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Expertise Keyword Distribution</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={expertiseAgg} margin={{ top: 10, right: 30, left: 140, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" stroke="#475569" />
              <YAxis type="category" dataKey="area" stroke="#475569" tick={{ fontSize: 12, fill: "#334155" }} width={135} />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
              <Bar dataKey="count" name="Researchers" fill={COLORS.indigo} radius={[0, 6, 6, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="expertise-cards-grid">
        {researchers.map((r) => (
          <div key={r.researcher_id} className="expertise-card">
            <div className="expertise-card-header">
              <h3>{r.name}</h3>
              <span className="mini-score" style={{ background: getScoreColor(r.overall_researcher_score) }}>{formatScore(r.overall_researcher_score)}</span>
            </div>
            <p className="expertise-card-institution">{r.institution}</p>
            <div className="expertise-keywords">
              {(r.top_expertise_areas || []).map((kw, i) => (
                <span key={i} className="keyword-chip" style={{ borderColor: PIE_COLORS[i % PIE_COLORS.length], color: PIE_COLORS[i % PIE_COLORS.length] }}>{kw}</span>
              ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

function CompareView({ researchers, compareIds, setCompareIds }) {
  const researcherA = researchers.find((r) => r.researcher_id === compareIds[0]);
  const researcherB = researchers.find((r) => r.researcher_id === compareIds[1]);

  return (
    <div className="tab-panel animate-fade-in">
      <section className="overview-intro-card">
        <h2>Researcher Comparison</h2>
        <p>Select two researchers to compare their intelligence profiles side by side.</p>
      </section>

      <section className="compare-selectors">
        <div className="compare-selector">
          <label>Researcher A</label>
          <select value={compareIds[0]} onChange={(e) => setCompareIds([e.target.value, compareIds[1]])}>
            <option value="">Select researcher...</option>
            {researchers.map((r) => (
              <option key={r.researcher_id} value={r.researcher_id}>{r.name} ({r.institution})</option>
            ))}
          </select>
        </div>
        <div className="compare-vs">VS</div>
        <div className="compare-selector">
          <label>Researcher B</label>
          <select value={compareIds[1]} onChange={(e) => setCompareIds([compareIds[0], e.target.value])}>
            <option value="">Select researcher...</option>
            {researchers.map((r) => (
              <option key={r.researcher_id} value={r.researcher_id}>{r.name} ({r.institution})</option>
            ))}
          </select>
        </div>
      </section>

      {compareIds[0] && compareIds[1] && researcherA && researcherB && (
        <CompareResult researcherA={researcherA} researcherB={researcherB} />
      )}
    </div>
  );
}

function CompareResult({ researcherA, researcherB }) {
  const kwA = new Set(researcherA.top_expertise_areas || []);
  const kwB = new Set(researcherB.top_expertise_areas || []);
  const shared = [...kwA].filter((k) => kwB.has(k));
  const uniqueA = [...kwA].filter((k) => !kwB.has(k));
  const uniqueB = [...kwB].filter((k) => !kwA.has(k));

  const compBarData = [
    { metric: "Publication", [researcherA.name.split(" ").slice(-1)[0]]: researcherA.publication_strength_score, [researcherB.name.split(" ").slice(-1)[0]]: researcherB.publication_strength_score },
    { metric: "Patent", [researcherA.name.split(" ").slice(-1)[0]]: researcherA.patent_strength_score, [researcherB.name.split(" ").slice(-1)[0]]: researcherB.patent_strength_score },
    { metric: "Overall", [researcherA.name.split(" ").slice(-1)[0]]: researcherA.overall_researcher_score, [researcherB.name.split(" ").slice(-1)[0]]: researcherB.overall_researcher_score },
  ];

  const nameA = researcherA.name.split(" ").slice(-1)[0];
  const nameB = researcherB.name.split(" ").slice(-1)[0];

  return (
    <div className="compare-result animate-fade-in">
      <section className="compare-cards-row">
        <div className="compare-profile-card">
          <h3>{researcherA.name}</h3>
          <p>{researcherA.institution}</p>
          <div className="big-score-circle small" style={{ borderColor: getScoreColor(researcherA.overall_researcher_score) }}>
            <span className="big-score-number">{formatScore(researcherA.overall_researcher_score)}</span>
          </div>
          <div className="compare-keywords">
            {uniqueA.map((kw, i) => (<span key={i} className="keyword-chip unique-a">{kw}</span>))}
          </div>
        </div>
        <div className="compare-profile-card">
          <h3>{researcherB.name}</h3>
          <p>{researcherB.institution}</p>
          <div className="big-score-circle small" style={{ borderColor: getScoreColor(researcherB.overall_researcher_score) }}>
            <span className="big-score-number">{formatScore(researcherB.overall_researcher_score)}</span>
          </div>
          <div className="compare-keywords">
            {uniqueB.map((kw, i) => (<span key={i} className="keyword-chip unique-b">{kw}</span>))}
          </div>
        </div>
      </section>

      {shared.length > 0 && (
        <section className="chart-card">
          <h2>🤝 Shared Expertise Areas ({shared.length})</h2>
          <div className="shared-keywords">
            {shared.map((kw, i) => (<span key={i} className="keyword-chip shared">{kw}</span>))}
          </div>
        </section>
      )}

      <section className="chart-card">
        <h2>Score Comparison</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={compBarData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="metric" stroke="#475569" />
              <YAxis stroke="#475569" domain={[0, 60]} />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} formatter={(value) => [formatScore(value), ""]} />
              <Legend />
              <Bar dataKey={nameA} fill={COLORS.blue} radius={[4, 4, 0, 0]} barSize={40} />
              <Bar dataKey={nameB} fill={COLORS.green} radius={[4, 4, 0, 0]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="two-col-grid">
        <div className="chart-card">
          <h2>📚 {nameA}'s Top Publications</h2>
          <div className="table-container">
            <table>
              <thead><tr><th>Title</th><th>Sim</th></tr></thead>
              <tbody>
                {(researcherA.matched_publications_sample || []).slice(0, 3).map((pub, i) => (
                  <tr key={i}><td className="paper-title" style={{ maxWidth: "300px" }}>{pub.title}</td><td>{(pub.similarity * 100).toFixed(1)}%</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="chart-card">
          <h2>📚 {nameB}'s Top Publications</h2>
          <div className="table-container">
            <table>
              <thead><tr><th>Title</th><th>Sim</th></tr></thead>
              <tbody>
                {(researcherB.matched_publications_sample || []).slice(0, 3).map((pub, i) => (
                  <tr key={i}><td className="paper-title" style={{ maxWidth: "300px" }}>{pub.title}</td><td>{(pub.similarity * 100).toFixed(1)}%</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="two-col-grid">
        <div className="explanation-card"><h3>📝 {nameA}'s Explanation</h3><p>{researcherA.explanation}</p></div>
        <div className="explanation-card"><h3>📝 {nameB}'s Explanation</h3><p>{researcherB.explanation}</p></div>
      </section>
    </div>
  );
}

// ============================================================
// PUBLICATION TRENDS COMPONENTS
// ============================================================

function PubOverview({ summary }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="summary-grid">
        <div className="summary-card blue">
          <div className="card-icon">📚</div>
          <div><p>Total Publications</p><h2>{formatNumber(summary?.total_publications)}</h2><span>In clean dataset</span></div>
        </div>
        <div className="summary-card purple">
          <div className="card-icon">📈</div>
          <div><p>Total Citations</p><h2>{formatNumber(summary?.total_citations)}</h2><span>Cumulative impact</span></div>
        </div>
        <div className="summary-card green">
          <div className="card-icon">⭐</div>
          <div><p>Average Citations</p><h2>{formatDecimal(summary?.average_citations)}</h2><span>Per publication</span></div>
        </div>
        <div className="summary-card orange">
          <div className="card-icon">🔓</div>
          <div><p>Open Access Ratio</p><h2>{formatDecimal((summary?.open_access_publications / summary?.total_publications) * 100)}%</h2><span>{formatNumber(summary?.open_access_publications)} open works</span></div>
        </div>
        <div className="summary-card red">
          <div className="card-icon">⚠</div>
          <div><p>Retracted Papers</p><h2>{formatNumber(summary?.retracted_publications)}</h2><span>Flags in dataset</span></div>
        </div>
      </section>
    </div>
  );
}

function PubTrends({ yearlyTrend }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Publication Count by Year</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yearlyTrend} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="publication_year" stroke="#475569" />
              <YAxis stroke="#475569" />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
              <Legend />
              <Line type="monotone" dataKey="publication_count" name="Publication Count" stroke="#2563eb" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section className="chart-card">
        <h2>Average Citations by Year</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yearlyTrend} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="publication_year" stroke="#475569" />
              <YAxis stroke="#475569" />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
              <Legend />
              <Line type="monotone" dataKey="average_citations" name="Average Citations" stroke="#059669" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}

function PubDomains({ top10Domains }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Research Domain Distribution</h2>
        <div className="chart-container horizontal-bars">
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={top10Domains} layout="vertical" margin={{ top: 10, right: 40, left: 180, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" stroke="#475569" />
              <YAxis type="category" dataKey="domain" stroke="#475569" tickFormatter={truncateLabel} tick={{ fontSize: 12, fill: "#334155" }} width={170} />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
              <Legend />
              <Bar dataKey="publication_count" name="Publications" fill="#7c3aed" radius={[0, 6, 6, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}

function PubTopics({ top15Topics }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Top 15 Research Topics</h2>
        <div className="chart-container horizontal-bars">
          <ResponsiveContainer width="100%" height={600}>
            <BarChart data={top15Topics} layout="vertical" margin={{ top: 10, right: 40, left: 240, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" stroke="#475569" />
              <YAxis type="category" dataKey="topic" stroke="#475569" tickFormatter={truncateLabel} tick={{ fontSize: 12, fill: "#334155" }} width={230} />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
              <Legend />
              <Bar dataKey="publication_count" name="Publications" fill="#059669" radius={[0, 6, 6, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}

function PubCitations({ citation, yearlyTrend, topCited }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="citation-stats-cards">
        <div className="stat-value-card"><span>Total Citations</span><strong>{formatNumber(citation?.total_citations)}</strong></div>
        <div className="stat-value-card"><span>Average Per Paper</span><strong>{formatDecimal(citation?.average_citations)}</strong></div>
        <div className="stat-value-card"><span>Highest Cited</span><strong>{formatNumber(citation?.maximum_citations)}</strong></div>
        <div className="stat-value-card"><span>Minimum Citations</span><strong>{formatNumber(citation?.minimum_citations)}</strong></div>
      </section>
      <section className="chart-card">
        <h2>Total Yearly Citations</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yearlyTrend} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="publication_year" stroke="#475569" />
              <YAxis stroke="#475569" />
              <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
              <Legend />
              <Line type="monotone" dataKey="total_citations" name="Total Citations" stroke="#ea580c" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section className="chart-card">
        <h2>Most Cited Publications (Top 10)</h2>
        <div className="table-container">
          <table>
            <thead><tr><th>Rank</th><th>Title</th><th>Year</th><th>Citations</th><th>DOI</th></tr></thead>
            <tbody>
              {topCited.slice(0, 10).map((paper, index) => (
                <tr key={paper.id || index}>
                  <td>{index + 1}</td>
                  <td className="paper-title">{paper.title}</td>
                  <td>{paper.publication_year}</td>
                  <td><span className="citation-badge orange">{formatNumber(paper.cited_by_count)}</span></td>
                  <td>{paper.doi ? <a href={paper.doi} target="_blank" rel="noreferrer" className="action-url">Link ↗</a> : <span className="text-gray-400">N/A</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function PubInsights({ emergingTopics }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="overview-intro-card">
        <h2>Emerging Research Topics</h2>
        <p>Topics flagged as emerging if they show significant growth in publication volume.</p>
      </section>
      <section className="chart-card">
        <h2>Top Emerging Research Topics</h2>
        <div className="table-container">
          <table>
            <thead><tr><th>Rank</th><th>Topic</th><th>Latest</th><th>Previous</th><th>Growth</th><th>Status</th></tr></thead>
            <tbody>
              {emergingTopics.map((item, index) => (
                <tr key={index}>
                  <td>{index + 1}</td>
                  <td className="paper-title">{item.topic}</td>
                  <td><strong>{item.latest_publications}</strong></td>
                  <td>{item.previous_publications}</td>
                  <td><span className="growth-text positive">+{formatDecimal(item.growth_percentage)}%</span></td>
                  <td><span className="trend-status-tracker positive-up">🔥 Emerging</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function PubBrowser({ publications, publicationsTotal, publicationsLoading, currentPage, totalPages, publicationsOffset, publicationsLimit, onPageChange }) {
  return (
    <div className="tab-panel animate-fade-in">
      <section className="chart-card">
        <h2>Publications Database Browser</h2>
        <p className="chart-description">Total: <strong>{formatNumber(publicationsTotal)}</strong> records</p>
        {publicationsLoading ? (
          <div className="table-loader-box"><div className="small-loader"></div><p>Loading...</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead><tr><th>Title</th><th>Year</th><th>Type</th><th>Citations</th><th>OA</th><th>DOI</th></tr></thead>
              <tbody>
                {publications.map((item) => (
                  <tr key={item.id}>
                    <td className="paper-title">{item.title || "Untitled"}</td>
                    <td>{item.publication_year}</td>
                    <td><span className="type-badge-style">{item.type || "unknown"}</span></td>
                    <td><span className="citation-badge min-width">{formatNumber(item.cited_by_count)}</span></td>
                    <td><span className={`oa-badge ${item.open_access ? "yes" : "no"}`}>{item.open_access ? "🔓 OA" : "🔒 Paid"}</span></td>
                    <td>{item.doi ? <a href={item.doi} target="_blank" rel="noreferrer" className="action-url">View ↗</a> : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="pagination-bar-wrapper">
          <button onClick={() => onPageChange("prev")} disabled={currentPage === 1 || publicationsLoading} className="page-nav-btn">◀ Previous</button>
          <span className="page-status-indicator">Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong></span>
          <button onClick={() => onPageChange("next")} disabled={currentPage === totalPages || publicationsLoading} className="page-nav-btn">Next ▶</button>
        </div>
      </section>
    </div>
  );
}

export default App;
