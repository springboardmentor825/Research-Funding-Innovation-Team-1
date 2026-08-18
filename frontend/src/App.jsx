import { useEffect, useState } from "react";
import {
  getSummary,
  getYearlyTrend,
  getDomainDistribution,
  getTopicDistribution,
  getCitationAnalysis,
  getEmergingTopics,
  getTopCited,
  getPublications,
} from "./api";

import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import "./App.css";

function App() {
  // Navigation State
  const [activeTab, setActiveTab] = useState("Overview");

  // Analytics Data States
  const [summary, setSummary] = useState(null);
  const [yearlyTrend, setYearlyTrend] = useState([]);
  const [domains, setDomains] = useState([]);
  const [topics, setTopics] = useState([]);
  const [citation, setCitation] = useState(null);
  const [emergingTopics, setEmergingTopics] = useState([]);
  const [topCited, setTopCited] = useState([]);

  // Publications Pagination States
  const [publications, setPublications] = useState([]);
  const [publicationsTotal, setPublicationsTotal] = useState(0);
  const [publicationsLimit] = useState(10);
  const [publicationsOffset, setPublicationsOffset] = useState(0);
  const [publicationsLoading, setPublicationsLoading] = useState(false);

  // App Loading & Error States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Load all initial analytical data on mount
  useEffect(() => {
    loadDashboard();
  }, []);

  // Fetch publications whenever the offset/page changes
  useEffect(() => {
    loadPublicationsData(publicationsOffset);
  }, [publicationsOffset]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        summaryData,
        yearlyData,
        domainData,
        topicData,
        citationData,
        emergingData,
        topCitedData,
      ] = await Promise.all([
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
    } catch (err) {
      console.error("Dashboard loading error:", err);
      setError(
        "Unable to load dashboard data. Please make sure the FastAPI backend is running and the database is accessible."
      );
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
      console.error("Publications loading error:", err);
    } finally {
      setPublicationsLoading(false);
    }
  };

  const formatNumber = (number) => {
    if (number === null || number === undefined) {
      return "0";
    }
    return Number(number).toLocaleString();
  };

  const formatDecimal = (number) => {
    if (number === null || number === undefined) {
      return "0";
    }
    return Number(number).toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
  };

  // Helper for pagination controls
  const handlePageChange = (direction) => {
    if (direction === "next") {
      if (publicationsOffset + publicationsLimit < publicationsTotal) {
        setPublicationsOffset(publicationsOffset + publicationsLimit);
      }
    } else if (direction === "prev") {
      if (publicationsOffset - publicationsLimit >= 0) {
        setPublicationsOffset(publicationsOffset - publicationsLimit);
      }
    }
  };

  const currentPage = Math.floor(publicationsOffset / publicationsLimit) + 1;
  const totalPages = Math.ceil(publicationsTotal / publicationsLimit) || 1;

  // Process data for charts
  // Top 10 domains sorted by publication count
  const top10Domains = [...domains]
    .sort((a, b) => b.publication_count - a.publication_count)
    .slice(0, 10);

  // Top 15 topics sorted by publication count
  const top15Topics = [...topics]
    .sort((a, b) => b.publication_count - a.publication_count)
    .slice(0, 15);

  // Truncate long labels for Recharts axes to improve readability
  const truncateLabel = (value) => {
    if (!value) return "";
    return value.length > 25 ? value.substring(0, 22) + "..." : value;
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <h2>Loading Publication Analytics...</h2>
        <p>Fetching research publication data from MySQL database via FastAPI.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <div className="error-card">
          <h2>⚠ Dashboard Error</h2>
          <p>{error}</p>
          <button onClick={loadDashboard}>Retry Connection</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* HEADER SECTION WITH NAVIGATION */}
      <header className="dashboard-header">
        <div className="header-title-section">
          <h1>PUBLICATION TREND ANALYSIS</h1>
          <p className="subtitle">OpenAlex Research Publication Analytics System</p>
        </div>
        <div className="header-status">
          <span className="status-dot"></span>
          Connected to MySQL
        </div>
      </header>

      {/* TOP NAVIGATION HEADER */}
      <nav className="dashboard-nav">
        {[
          "Overview",
          "Trends",
          "Domains",
          "Topics",
          "Citations",
          "Research Insights",
          "Publications",
        ].map((tab) => (
          <button
            key={tab}
            className={`nav-item ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      {/* MAIN CONTENT AREA CONTAINER */}
      <main className="dashboard-content">
        {/* ============================================================ */}
        {/* OVERVIEW TAB */}
        {/* ============================================================ */}
        {activeTab === "Overview" && (
          <div className="tab-panel animate-fade-in">
            <section className="summary-grid">
              <div className="summary-card blue">
                <div className="card-icon">📚</div>
                <div>
                  <p>Total Publications</p>
                  <h2>{formatNumber(summary?.total_publications)}</h2>
                  <span>In clean dataset</span>
                </div>
              </div>

              <div className="summary-card purple">
                <div className="card-icon">📈</div>
                <div>
                  <p>Total Citations</p>
                  <h2>{formatNumber(summary?.total_citations)}</h2>
                  <span>Cumulative impact</span>
                </div>
              </div>

              <div className="summary-card green">
                <div className="card-icon">⭐</div>
                <div>
                  <p>Average Citations</p>
                  <h2>{formatDecimal(summary?.average_citations)}</h2>
                  <span>Per publication</span>
                </div>
              </div>

              <div className="summary-card orange">
                <div className="card-icon">🔓</div>
                <div>
                  <p>Open Access Ratio</p>
                  <h2>
                    {formatDecimal(
                      (summary?.open_access_publications /
                        summary?.total_publications) *
                      100
                    )}
                    %
                  </h2>
                  <span>{formatNumber(summary?.open_access_publications)} open works</span>
                </div>
              </div>

              <div className="summary-card red">
                <div className="card-icon">⚠</div>
                <div>
                  <p>Retracted Papers</p>
                  <h2>{formatNumber(summary?.retracted_publications)}</h2>
                  <span>Flags in dataset</span>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* ============================================================ */}
        {/* TRENDS TAB */}
        {/* ============================================================ */}
        {activeTab === "Trends" && (
          <div className="tab-panel animate-fade-in">
            <section className="chart-card">
              <h2>Publication Count in Sample by Year</h2>
              <p className="chart-description">Yearly distribution of research publications inside the cleaned dataset</p>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={yearlyTrend} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="publication_year" stroke="#475569" />
                    <YAxis stroke="#475569" />
                    <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="publication_count"
                      name="Publication Count (Sample)"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={{ r: 4, strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="chart-card">
              <h2>Average Citations by Year</h2>
              <p className="chart-description">Average citation index per paper showing temporal research impact shifts</p>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={yearlyTrend} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="publication_year" stroke="#475569" />
                    <YAxis stroke="#475569" />
                    <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="average_citations"
                      name="Average Citations"
                      stroke="#059669"
                      strokeWidth={3}
                      dot={{ r: 4, strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        )}

        {/* ============================================================ */}
        {/* DOMAINS TAB */}
        {/* ============================================================ */}
        {activeTab === "Domains" && (
          <div className="tab-panel animate-fade-in">
            <section className="chart-card">
              <h2>Research Domain Distribution</h2>
              <p className="chart-description">
                Top research domains based on publication count. Horizontal bars accommodate long names cleanly.
              </p>
              <div className="chart-container horizontal-bars">
                <ResponsiveContainer width="100%" height={500}>
                  <BarChart
                    data={top10Domains}
                    layout="vertical"
                    margin={{ top: 10, right: 40, left: 180, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis type="number" stroke="#475569" />
                    <YAxis
                      type="category"
                      dataKey="domain"
                      stroke="#475569"
                      tickFormatter={truncateLabel}
                      tick={{ fontSize: 12, fill: "#334155" }}
                      width={170}
                    />
                    <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
                    <Legend />
                    <Bar
                      dataKey="publication_count"
                      name="Publications"
                      fill="#7c3aed"
                      radius={[0, 6, 6, 0]}
                      barSize={20}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        )}

        {/* ============================================================ */}
        {/* TOPICS TAB */}
        {/* ============================================================ */}
        {activeTab === "Topics" && (
          <div className="tab-panel animate-fade-in">
            <section className="chart-card">
              <h2>Top 15 Research Topics</h2>
              <p className="chart-description">
                The most frequently identified topics across the publication catalog. Translucent grid coordinates and cropped names ensure clarity.
              </p>
              <div className="chart-container horizontal-bars">
                <ResponsiveContainer width="100%" height={600}>
                  <BarChart
                    data={top15Topics}
                    layout="vertical"
                    margin={{ top: 10, right: 40, left: 240, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis type="number" stroke="#475569" />
                    <YAxis
                      type="category"
                      dataKey="topic"
                      stroke="#475569"
                      tickFormatter={truncateLabel}
                      tick={{ fontSize: 12, fill: "#334155" }}
                      width={230}
                    />
                    <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
                    <Legend />
                    <Bar
                      dataKey="publication_count"
                      name="Publications"
                      fill="#059669"
                      radius={[0, 6, 6, 0]}
                      barSize={16}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        )}

        {/* ============================================================ */}
        {/* CITATIONS TAB */}
        {/* ============================================================ */}
        {activeTab === "Citations" && (
          <div className="tab-panel animate-fade-in">
            <section className="citation-stats-cards">
              <div className="stat-value-card">
                <span>Total Citations Captured</span>
                <strong>{formatNumber(citation?.total_citations)}</strong>
                <p>Accumulated citation signals from MySQL</p>
              </div>
              <div className="stat-value-card">
                <span>Average Citations Per Paper</span>
                <strong>{formatDecimal(citation?.average_citations)}</strong>
                <p>Standard intellectual footprint score</p>
              </div>
              <div className="stat-value-card">
                <span>Highest Cited Single Paper</span>
                <strong>{formatNumber(citation?.maximum_citations)}</strong>
                <p>Peak count for a highly cited publication</p>
              </div>
              <div className="stat-value-card">
                <span>Minimum Citation Score</span>
                <strong>{formatNumber(citation?.minimum_citations)}</strong>
                <p>Baseline count index</p>
              </div>
            </section>

            <section className="chart-card">
              <h2>Total Yearly Citations</h2>
              <p className="chart-description">Cumulative count of citations grouped by publishing year</p>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={yearlyTrend} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="publication_year" stroke="#475569" />
                    <YAxis stroke="#475569" />
                    <Tooltip contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total_citations"
                      name="Total Citations"
                      stroke="#ea580c"
                      strokeWidth={3}
                      dot={{ r: 4, strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="chart-card">
              <h2>Most Cited Publications (Top 10)</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Publication Title</th>
                      <th>Year</th>
                      <th>Citations</th>
                      <th>DOI Direct URL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topCited.slice(0, 10).map((paper, index) => (
                      <tr key={paper.id || index}>
                        <td>{index + 1}</td>
                        <td className="paper-title font-medium">{paper.title}</td>
                        <td>{paper.publication_year}</td>
                        <td>
                          <span className="citation-badge orange">
                            {formatNumber(paper.cited_by_count)}
                          </span>
                        </td>
                        <td>
                          {paper.doi ? (
                            <a href={paper.doi} target="_blank" rel="noreferrer" className="action-url">
                              Link ↗
                            </a>
                          ) : (
                            <span className="text-gray-400">N/A</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}

        {/* ============================================================ */}
        {/* RESEARCH INSIGHTS TAB */}
        {/* ============================================================ */}
        {activeTab === "Research Insights" && (
          <div className="tab-panel animate-fade-in">
            <section className="overview-intro-card">
              <h2>Emerging Research Topics</h2>
              <p>
                Topics are flagged as **emerging** if they show significant growth in publication volume from their previous active year to their latest active year (minimum of 5 latest publications to filter out random noise).
              </p>
            </section>

            <section className="chart-card">
              <h2>Top Emerging Research Topics Table</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Topic Name</th>
                      <th>Latest Count ({emergingTopics[0]?.latest_year || "Latest"})</th>
                      <th>Previous Count ({emergingTopics[0]?.previous_year || "Previous"})</th>
                      <th>Growth (%)</th>
                      <th>Trend Indicator</th>
                    </tr>
                  </thead>
                  <tbody>
                    {emergingTopics.map((item, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td className="paper-title">{item.topic}</td>
                        <td><strong>{item.latest_publications}</strong> publications</td>
                        <td>{item.previous_publications} publications</td>
                        <td>
                          <span className="growth-text positive">
                            +{formatDecimal(item.growth_percentage)}%
                          </span>
                        </td>
                        <td>
                          <span className="trend-status-tracker positive-up">
                            🔥 Emerging Trend
                          </span>
                        </td>
                      </tr>
                    ))}
                    {emergingTopics.length === 0 && (
                      <tr>
                        <td colSpan="6" style={{ textAlign: "center", padding: "30px" }}>
                          No emerging topics identified in the sampled range.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}

        {/* ============================================================ */}
        {/* PUBLICATIONS TAB */}
        {/* ============================================================ */}
        {activeTab === "Publications" && (
          <div className="tab-panel animate-fade-in">
            <section className="chart-card">
              <div className="section-title">
                <div>
                  <h2>All Publications Database Browser</h2>
                  <p className="chart-description">
                    Live lookup of publication rows stored inside MySQL server. Total database size: <strong>{formatNumber(publicationsTotal)}</strong> records.
                  </p>
                </div>
              </div>

              {publicationsLoading ? (
                <div className="table-loader-box">
                  <div className="small-loader"></div>
                  <p>Loading database entries...</p>
                </div>
              ) : (
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Year</th>
                        <th>Type</th>
                        <th>Citations</th>
                        <th>Open Access</th>
                        <th>DOI Lookup</th>
                      </tr>
                    </thead>
                    <tbody>
                      {publications.map((item) => (
                        <tr key={item.id}>
                          <td className="paper-title" title={item.title}>
                            {item.title || "Untitled Publication"}
                          </td>
                          <td>{item.publication_year}</td>
                          <td>
                            <span className="type-badge-style">
                              {item.type || "unknown"}
                            </span>
                          </td>
                          <td>
                            <span className="citation-badge min-width">
                              {formatNumber(item.cited_by_count)}
                            </span>
                          </td>
                          <td>
                            <span className={`oa-badge ${item.open_access ? "yes" : "no"}`}>
                              {item.open_access ? "🔓 OA" : "🔒 Paid"}
                            </span>
                          </td>
                          <td>
                            {item.doi ? (
                              <a href={item.doi} target="_blank" rel="noreferrer" className="action-url">
                                View Paper ↗
                              </a>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                      {publications.length === 0 && (
                        <tr>
                          <td colSpan="6" style={{ textAlign: "center", padding: "30px" }}>
                            No publication records found in the database.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}

              {/* PAGINATION INTERFACE */}
              <div className="pagination-bar-wrapper">
                <button
                  onClick={() => handlePageChange("prev")}
                  disabled={currentPage === 1 || publicationsLoading}
                  className="page-nav-btn"
                >
                  ◀ Previous Page
                </button>
                <span className="page-status-indicator">
                  Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong> (Records {formatNumber(publicationsOffset + 1)} - {formatNumber(Math.min(publicationsOffset + publicationsLimit, publicationsTotal))})
                </span>
                <button
                  onClick={() => handlePageChange("next")}
                  disabled={currentPage === totalPages || publicationsLoading}
                  className="page-nav-btn"
                >
                  Next Page ▶
                </button>
              </div>
            </section>
          </div>
        )}
      </main>

      {/* FOOTER BAR */}
      <footer className="dashboard-footer">
        <p>Publication Trend Analysis Project Dashboard</p>
        <span>OpenAlex Catalog • MySQL DB Storage Layer • FastAPI Server Router • React client & Recharts Engine</span>
      </footer>
    </div>
  );
}

export default App;
