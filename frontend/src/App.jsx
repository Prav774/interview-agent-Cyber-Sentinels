import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/interview";

function App() {
  const [candidateId, setCandidateId] = useState("CAND-001");
  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [questionNumber, setQuestionNumber] = useState(0);
  const [done, setDone] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState("");

  async function sendRequest(payload) {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  async function startInterview() {
    setLoading(true);
    setError("");

    const newSessionId = `frontend-${Date.now()}`;
    setSessionId(newSessionId);

    try {
      const data = await sendRequest({
        sessionId: newSessionId,
        candidate: {
          member: {
            id: candidateId,
          },
        },
      });

      setQuestion(data.reply);
      setQuestionNumber(1);
      setStarted(true);
      setDone(false);
      setFeedback(null);
    } catch (err) {
      setError("Unable to start the interview. Make sure the backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswer() {
    if (!answer.trim() || loading) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await sendRequest({
        sessionId,
        message: answer.trim(),
      });

      setAnswer("");
      setQuestion(data.reply);

      const nextQuestionNumber = questionNumber + 1;
      setQuestionNumber(nextQuestionNumber);

      if (data.done) {
        setDone(true);
        setFeedback(data.feedback);
      }
    } catch (err) {
      setError("Unable to submit your answer. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  function resetInterview() {
    setSessionId("");
    setQuestion("");
    setAnswer("");
    setQuestionNumber(0);
    setDone(false);
    setFeedback(null);
    setStarted(false);
    setError("");
  }

  return (
    <div className="app">
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <header className="header">
        <div>
          <div className="brand">INTERVIEW AGENT</div>
          <div className="subtitle">AI Cohort Technical Assessment</div>
        </div>

        {started && !done && (
          <div className="progress">
            <span>QUESTION</span>
            <strong>{questionNumber}</strong>
            <span>/ 8+</span>
          </div>
        )}
      </header>

      <main className="main">
        {!started && (
          <section className="start-card">
            <div className="badge">AI-POWERED TECHNICAL INTERVIEW</div>

            <h1>
              Personalized
              <br />
              <span>Technical Interview</span>
            </h1>

            <p className="intro">
              An adaptive interview based on your AI Cohort learning journey,
              strengths, developing areas, and curriculum progress.
            </p>

            <div className="candidate-box">
              <label>Candidate ID</label>

              <select
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
              >
                <option value="CAND-001">CAND-001 — Sarah Johnson</option>
                <option value="CAND-003">CAND-003 — Emily Chen</option>
                <option value="CAND-010">CAND-010 — Gerald Combs</option>
                <option value="CAND-011">CAND-011</option>
              </select>
            </div>

            <button
              className="primary-button"
              onClick={startInterview}
              disabled={loading}
            >
              {loading ? "Starting..." : "Start Interview →"}
            </button>

            <div className="requirements">
              <div>
                <strong>8+</strong>
                <span>Questions</span>
              </div>

              <div>
                <strong>4+</strong>
                <span>Curriculum Days</span>
              </div>

              <div>
                <strong>AI</strong>
                <span>Adaptive Follow-ups</span>
              </div>
            </div>
          </section>
        )}

        {started && !done && (
          <section className="interview-card">
            <div className="question-header">
              <div>
                <div className="section-label">TECHNICAL INTERVIEW</div>
                <h2>Question {questionNumber}</h2>
              </div>

              <div className="live-indicator">
                <span></span>
                LIVE
              </div>
            </div>

            <div className="question-box">
              <div className="question-mark">?</div>

              <p>{question}</p>
            </div>

            <div className="answer-section">
              <label>Your answer</label>

              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Explain your approach, reasoning, and technical decisions..."
                disabled={loading}
                onKeyDown={(e) => {
                  if (
                    e.key === "Enter" &&
                    e.ctrlKey
                  ) {
                    submitAnswer();
                  }
                }}
              />

              <div className="answer-footer">
                <span>Ctrl + Enter to submit</span>

                <button
                  className="primary-button submit-button"
                  onClick={submitAnswer}
                  disabled={!answer.trim() || loading}
                >
                  {loading ? "Evaluating..." : "Submit Answer →"}
                </button>
              </div>
            </div>

            {error && (
              <div className="error">
                {error}
              </div>
            )}
          </section>
        )}

        {done && (
          <section className="feedback-card">
            <div className="completion-badge">
              INTERVIEW COMPLETE
            </div>

            <h1>Technical Interview<br />Completed</h1>

            <p className="completion-text">
              Your responses have been evaluated against your personalized
              curriculum journey.
            </p>

            {feedback && (
              <div className="feedback-content">
                <div className="feedback-section">
                  <h3>Summary</h3>
                  <p>{feedback.summary}</p>
                </div>

                <div className="feedback-grid">
                  <div className="feedback-section">
                    <h3>Strengths</h3>

                    <ul>
                      {feedback.strengths?.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="feedback-section">
                    <h3>Gaps</h3>

                    <ul>
                      {feedback.gaps?.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="feedback-section">
                  <h3>Next Steps</h3>

                  <ul>
                    {feedback.next?.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            <button
              className="primary-button"
              onClick={resetInterview}
            >
              Start New Interview →
            </button>
          </section>
        )}

        {error && !started && (
          <div className="error">
            {error}
          </div>
        )}
      </main>

      <footer>
        <span>Cyber Sentinels</span>
        <span>•</span>
        <span>AI Cohort Interview Agent</span>
      </footer>
    </div>
  );
}

export default App;