import { useEffect, useState } from "react";
import "./App.css";

const API_URL = `${
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
}/api/interview`;

function App() {
  const [candidates, setCandidates] = useState([]);
  const [candidateId, setCandidateId] = useState("");
  const [candidatesLoading, setCandidatesLoading] = useState(true);

  const [sessionId, setSessionId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [questionNumber, setQuestionNumber] = useState(0);
  const [done, setDone] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState("");

  // ============================================================
  // LOAD ALL CANDIDATES
  // ============================================================

  useEffect(() => {
    async function loadCandidates() {
      try {
        const response = await fetch("/candidates.json");

        if (!response.ok) {
          throw new Error(
            `Failed to load candidates: ${response.status}`
          );
        }

        const data = await response.json();

        if (!Array.isArray(data.candidates)) {
          throw new Error("Invalid candidates.json format");
        }

        setCandidates(data.candidates);

        if (data.candidates.length > 0) {
          setCandidateId(data.candidates[0].member.id);
        }
      } catch (err) {
        console.error(err);
        setError("Unable to load candidate list.");
      } finally {
        setCandidatesLoading(false);
      }
    }

    loadCandidates();
  }, []);

  // ============================================================
  // API REQUEST
  // ============================================================

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
      throw new Error(
        text || `Request failed: ${response.status}`
      );
    }

    return response.json();
  }

  // ============================================================
  // START INTERVIEW
  // ============================================================

  async function startInterview() {
    if (!candidateId || candidates.length === 0) {
      setError("Please select a candidate.");
      return;
    }

    const selectedCandidate = candidates.find(
      (candidate) =>
        candidate.member.id === candidateId
    );

    if (!selectedCandidate) {
      setError("Selected candidate was not found.");
      return;
    }

    setLoading(true);
    setError("");

    const newSessionId = `frontend-${Date.now()}`;

    setSessionId(newSessionId);

    try {
      const data = await sendRequest({
        sessionId: newSessionId,

        // IMPORTANT:
        // Send the COMPLETE candidate object.
        candidate: selectedCandidate,
      });

      setQuestion(data.reply);
      setQuestionNumber(1);
      setStarted(true);
      setDone(false);
      setFeedback(null);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to start the interview. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // SUBMIT ANSWER
  // ============================================================

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

      const nextQuestionNumber =
        questionNumber + 1;

      setQuestionNumber(nextQuestionNumber);

      if (data.done) {
        setDone(true);
        setFeedback(data.feedback);
      }
    } catch (err) {
      console.error(err);
      setError(
        "Unable to submit your answer. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // RESET
  // ============================================================

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

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="app">

      <header className="header">
        <div>
          <div className="brand">
            INTERVIEW AGENT
          </div>

          <div className="subtitle">
            AI Cohort Technical Assessment
          </div>
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

        {/* =====================================================
            START SCREEN
        ===================================================== */}

        {!started && (
          <section className="start-card">

            <div className="badge">
              AI-POWERED TECHNICAL INTERVIEW
            </div>

            <h1>
              Personalized
              <br />
              <span>Technical Interview</span>
            </h1>

            <p className="intro">
              An adaptive interview based on your AI Cohort
              learning journey, strengths, developing areas,
              and curriculum progress.
            </p>

            <div className="candidate-box">

              <label>
                Candidate
              </label>

              <select
                value={candidateId}
                onChange={(e) =>
                  setCandidateId(e.target.value)
                }
                disabled={
                  candidatesLoading ||
                  loading ||
                  candidates.length === 0
                }
              >
                {candidatesLoading ? (
                  <option>
                    Loading candidates...
                  </option>
                ) : candidates.length === 0 ? (
                  <option>
                    No candidates available
                  </option>
                ) : (
                  candidates.map((candidate) => (
                    <option
                      key={candidate.member.id}
                      value={candidate.member.id}
                    >
                      {candidate.member.id} —{" "}
                      {candidate.member.name}
                    </option>
                  ))
                )}
              </select>

            </div>

            <button
              className="primary-button"
              onClick={startInterview}
              disabled={
                loading ||
                candidatesLoading ||
                candidates.length === 0
              }
            >
              {loading
                ? "Starting..."
                : "Start Interview →"}
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

        {/* =====================================================
            INTERVIEW SCREEN
        ===================================================== */}

        {started && !done && (
          <section className="interview-card">

            <div className="question-header">

              <div>
                <div className="section-label">
                  TECHNICAL INTERVIEW
                </div>

                <h2>
                  Question {questionNumber}
                </h2>
              </div>

              <div className="live-indicator">
                <span></span>
                LIVE
              </div>

            </div>

            <div className="question-box">

              <div className="question-mark">
                ?
              </div>

              <p>{question}</p>

            </div>

            <div className="answer-section">

              <label>
                Your answer
              </label>

              <textarea
                value={answer}
                onChange={(e) =>
                  setAnswer(e.target.value)
                }
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

                <span>
                  Ctrl + Enter to submit
                </span>

                <button
                  className="primary-button submit-button"
                  onClick={submitAnswer}
                  disabled={
                    !answer.trim() ||
                    loading
                  }
                >
                  {loading
                    ? "Evaluating..."
                    : "Submit Answer →"}
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

        {/* =====================================================
            FEEDBACK SCREEN
        ===================================================== */}

        {done && (
          <section className="feedback-card">

            <div className="completion-badge">
              INTERVIEW COMPLETE
            </div>

            <h1>
              Technical Interview
              <br />
              Completed
            </h1>

            <p className="completion-text">
              Your responses have been evaluated
              against your personalized curriculum journey.
            </p>

            {feedback && (
              <div className="feedback-content">

                <div className="feedback-section">

                  <h3>
                    Summary
                  </h3>

                  <p>
                    {feedback.summary}
                  </p>

                </div>

                <div className="feedback-grid">

                  <div className="feedback-section">

                    <h3>
                      Strengths
                    </h3>

                    <ul>
                      {feedback.strengths?.map(
                        (item, index) => (
                          <li key={index}>
                            {item}
                          </li>
                        )
                      )}
                    </ul>

                  </div>

                  <div className="feedback-section">

                    <h3>
                      Gaps
                    </h3>

                    <ul>
                      {feedback.gaps?.map(
                        (item, index) => (
                          <li key={index}>
                            {item}
                          </li>
                        )
                      )}
                    </ul>

                  </div>

                </div>

                <div className="feedback-section">

                  <h3>
                    Next Steps
                  </h3>

                  <ul>
                    {feedback.next?.map(
                      (item, index) => (
                        <li key={index}>
                          {item}
                        </li>
                      )
                    )}
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

        {/* =====================================================
            ERROR
        ===================================================== */}

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