import React, { useState, useEffect } from "react";
import "./App.css";
import { generateQuiz, getAllQuizzes, getQuizById } from "./api";

function App() {
  const [activeTab, setActiveTab] = useState("generate");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [quizData, setQuizData] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Load history when switching to history tab
  useEffect(() => {
    if (activeTab === "history") {
      loadHistory();
    }
  }, [activeTab]);

  const loadHistory = async () => {
    try {
      const data = await getAllQuizzes();
      setHistory(data);
    } catch (err) {
      console.error("Error loading history:", err);
    }
  };

  const handleGenerateQuiz = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setQuizData(null);

    try {
      const data = await generateQuiz(url);
      setQuizData(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to generate quiz. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (quizId) => {
    try {
      const data = await getQuizById(quizId);
      setSelectedQuiz(data);
      setShowModal(true);
    } catch (err) {
      alert("Failed to load quiz details");
    }
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedQuiz(null);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>📚 Wiki Quiz Generator</h1>
        <p>Generate interactive quizzes from Wikipedia articles</p>
      </header>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === "generate" ? "active" : ""}`}
          onClick={() => setActiveTab("generate")}
        >
          Generate Quiz
        </button>
        <button
          className={`tab ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          Quiz History
        </button>
      </div>

      {/* Tab 1: Generate Quiz */}
      {activeTab === "generate" && (
        <div className="tab-content">
          <div className="container">
            <form onSubmit={handleGenerateQuiz} className="url-form">
              <input
                type="url"
                placeholder="Enter Wikipedia URL (e.g., https://en.wikipedia.org/wiki/Python_(programming_language))"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                className="url-input"
              />
              <button type="submit" disabled={loading} className="generate-btn">
                {loading ? "Generating..." : "Generate Quiz"}
              </button>
            </form>

            {error && <div className="error">{error}</div>}

            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Generating your quiz... This may take a moment.</p>
              </div>
            )}

            {quizData && <QuizDisplay data={quizData} />}
          </div>
        </div>
      )}

      {/* Tab 2: History */}
      {activeTab === "history" && (
        <div className="tab-content">
          <div className="container">
            <h2>Past Quizzes</h2>
            {history.length === 0 ? (
              <p className="no-data">
                No quizzes generated yet. Start by generating your first quiz!
              </p>
            ) : (
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>URL</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td>{item.title}</td>
                      <td className="url-cell">
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View Article
                        </a>
                      </td>
                      <td>{new Date(item.created_at).toLocaleDateString()}</td>
                      <td>
                        <button
                          onClick={() => handleViewDetails(item.id)}
                          className="details-btn"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Modal */}
      {showModal && selectedQuiz && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>
              ×
            </button>
            <QuizDisplay data={selectedQuiz} />
          </div>
        </div>
      )}
    </div>
  );
}

function QuizDisplay({ data }) {
  return (
    <div className="quiz-display">
      <div className="quiz-header">
        <h2>{data.title}</h2>
        {data.summary && <p className="summary">{data.summary}</p>}
      </div>

      {data.sections && data.sections.length > 0 && (
        <div className="sections-info">
          <h3>Article Sections</h3>
          <div className="sections">
            {data.sections.map((section, idx) => (
              <span key={idx} className="section-tag">
                {section}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.key_entities && (
        <div className="entities-info">
          <h3>Key Entities</h3>
          <div className="entities">
            {data.key_entities.people &&
              data.key_entities.people.length > 0 && (
                <div>
                  <strong>People:</strong> {data.key_entities.people.join(", ")}
                </div>
              )}
            {data.key_entities.organizations &&
              data.key_entities.organizations.length > 0 && (
                <div>
                  <strong>Organizations:</strong>{" "}
                  {data.key_entities.organizations.join(", ")}
                </div>
              )}
            {data.key_entities.locations &&
              data.key_entities.locations.length > 0 && (
                <div>
                  <strong>Locations:</strong>{" "}
                  {data.key_entities.locations.join(", ")}
                </div>
              )}
          </div>
        </div>
      )}

      <div className="quiz-questions">
        <h3>Quiz Questions ({data.quiz.length} questions)</h3>
        {data.quiz.map((q, idx) => (
          <div key={idx} className="question-card">
            <div className="question-header">
              <span className="question-number">Question {idx + 1}</span>
              <span className={`difficulty ${q.difficulty}`}>
                {q.difficulty}
              </span>
            </div>
            <p className="question-text">{q.question}</p>
            <div className="options">
              {q.options.map((option, optIdx) => (
                <div
                  key={optIdx}
                  className={`option ${option === q.answer ? "correct" : ""}`}
                >
                  {option}
                  {option === q.answer && (
                    <span className="correct-mark"> ✓</span>
                  )}
                </div>
              ))}
            </div>
            <div className="explanation">
              <strong>Explanation:</strong> {q.explanation}
            </div>
          </div>
        ))}
      </div>

      {data.related_topics && data.related_topics.length > 0 && (
        <div className="related-topics">
          <h3>Related Topics for Further Reading</h3>
          <div className="topics">
            {data.related_topics.map((topic, idx) => (
              <span key={idx} className="topic-tag">
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
