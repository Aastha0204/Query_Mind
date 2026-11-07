
import { useState } from "react";
import "./App.css";

const suggestions = [
  "Show all students",
  "Count students in each department",
  "Show courses with department names",
  "Find the top 3 courses by enrollment",
];

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const askQuestion = async (customQuestion) => {
    const finalQuestion = (customQuestion ?? question).trim();

    if (!finalQuestion) return;

    setQuestion(finalQuestion);
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: finalQuestion }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        success: false,
        error: "Cannot connect to the backend. Make sure FastAPI is running.",
      });
    } finally {
      setLoading(false);
    }
  };

  const copySQL = async (sql) => {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      alert("Unable to copy SQL.");
    }
  };

  const resetWorkspace = () => {
    setQuestion("");
    setResult(null);
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">⌘</div>
          <div>
            <h2>QueryMind</h2>
            <span>AI SQL Assistant</span>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <button className="nav-item active">
          <span>▦</span> Query Studio
        </button>

        <button className="nav-item" onClick={resetWorkspace}>
          <span>＋</span> New Query
        </button>

        <div className="sidebar-bottom">
          <div className="connection-card">
            <span className="status-dot"></span>
            <div>
              <strong>Database connected</strong>
              <small>MySQL · university_db</small>
            </div>
          </div>
          <p>Powered by Groq AI</p>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace /</span>
            <strong> Query Studio</strong>
          </div>
          <div className="topbar-right">
            <span className="api-status">
              <span className="status-dot"></span> API ready
            </span>
            <div className="avatar">AI</div>
          </div>
        </header>

        <div className="content">
          <section className="welcome">
            <div className="eyebrow">YOUR INTELLIGENT DATABASE ASSISTANT</div>
            <h1>Ask your data anything.</h1>
            <p>
              Turn natural language into SQL queries and explore your
              database with the power of AI.
            </p>
          </section>

          <section className="query-card">
            <div className="card-heading">
              <div>
                <h3>Ask a question</h3>
                <p>Describe what you want to retrieve from your database.</p>
              </div>
              <span className="ai-badge">✦ AI POWERED</span>
            </div>

            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                  askQuestion();
                }
              }}
              placeholder="e.g. Show all students belonging to Computer Science..."
              rows="4"
            />

            <div className="query-footer">
              <span>Tip: Press Ctrl + Enter to run your query</span>
              <button
                className="ask-button"
                onClick={() => askQuestion()}
                disabled={loading || !question.trim()}
              >
                {loading ? "Generating..." : "✦  Generate SQL"}
              </button>
            </div>

            <div className="suggestions">
              <span>Try asking:</span>
              {suggestions.map((item) => (
                <button
                  key={item}
                  onClick={() => askQuestion(item)}
                  disabled={loading}
                >
                  {item}
                </button>
              ))}
            </div>
          </section>

          {loading && (
            <div className="loading-card">
              <div className="spinner"></div>
              <div>
                <strong>Working on your query...</strong>
                <p>AI is generating SQL and retrieving database records.</p>
              </div>
            </div>
          )}

          {!result && !loading && (
            <section className="empty-state">
              <div className="empty-icon">⌘</div>
              <h3>Your query workspace is ready</h3>
              <p>
                Enter a question above to generate SQL and view
                results from your database.
              </p>
            </section>
          )}

          {result && (
            <section className="result-section">
              {result.success ? (
                <>
                  <div className="result-heading">
                    <div>
                      <span className="success-label">● QUERY COMPLETED</span>
                      <h2>Query results</h2>
                      <p>{result.question}</p>
                    </div>
                    <button className="secondary-button" onClick={resetWorkspace}>
                      + New query
                    </button>
                  </div>

                  <div className="metric-grid">
                    <div className="metric-card">
                      <span>ROWS RETURNED</span>
                      <strong>{result.row_count}</strong>
                    </div>
                    <div className="metric-card">
                      <span>COLUMNS</span>
                      <strong>{result.columns?.length ?? 0}</strong>
                    </div>
                    <div className="metric-card">
                      <span>VALIDATION</span>
                      <strong className="valid-text">Passed ✓</strong>
                    </div>
                  </div>

                  <div className="sql-card">
                    <div className="panel-heading">
                      <div>
                        <span className="panel-icon">⌘</span>
                        <strong>Generated SQL</strong>
                      </div>
                      <button onClick={() => copySQL(result.generated_sql)}>
                        {copied ? "Copied ✓" : "Copy SQL"}
                      </button>
                    </div>
                    <pre>{result.generated_sql}</pre>
                  </div>

                  <div className="sql-card">
                    <div className="panel-heading">
                      <div>
                        <span className="panel-icon">✓</span>
                        <strong>Validated SQL</strong>
                      </div>
                      <span className="validated-badge">Validated</span>
                    </div>
                    <pre>{result.validated_sql}</pre>
                  </div>

                  <div className="table-card">
                    <div className="panel-heading">
                      <div>
                        <strong>Database records</strong>
                        <p>Actual results retrieved from MySQL</p>
                      </div>
                      <span className="row-badge">
                        {result.row_count} rows
                      </span>
                    </div>

                    {result.rows?.length > 0 ? (
                      <div className="table-scroll">
                        <table>
                          <thead>
                            <tr>
                              {result.columns.map((column) => (
                                <th key={column}>{column}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {result.rows.map((row, index) => (
                              <tr key={index}>
                                {result.columns.map((column) => (
                                  <td key={column}>
                                    {row[column] === null
                                      ? "NULL"
                                      : String(row[column])}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="no-records">No records found.</div>
                    )}

                    {result.truncated && (
                      <p className="notice">
                        Only the first 100 records are displayed.
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <div className="error-card">
                  <h3>Query could not be completed</h3>
                  <p>{result.error || "An unexpected error occurred."}</p>
                  <button className="secondary-button" onClick={() => askQuestion()}>
                    Try again
                  </button>
                </div>
              )}
            </section>
          )}

          <footer className="footer">
            <span>QueryMind · Natural Language to SQL AI Agent</span>
            <span>React · FastAPI · Groq · MySQL</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
