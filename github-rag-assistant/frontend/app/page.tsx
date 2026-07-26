"use client";

import { useState } from "react";
import { askQuestion, getIndexStatus, indexRepo } from "@/lib/api";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [repoId, setRepoId] = useState("");
  const [indexStatus, setIndexStatus] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<
    { file: string; start_line: number; end_line: number }[]
  >([]);

  async function handleIndex() {
    setIndexStatus("starting…");
    const { job_id } = await indexRepo(repoUrl);
    const id = repoUrl.replace(/\/$/, "").split("/").pop()?.replace(".git", "") || "";
    setRepoId(id);

    const poll = setInterval(async () => {
      const status = await getIndexStatus(job_id);
      setIndexStatus(status.status);
      if (status.status === "done" || status.status === "failed") {
        clearInterval(poll);
      }
    }, 2000);
  }

  async function handleAsk() {
    setAnswer("thinking…");
    const result = await askQuestion(repoId, question);
    setAnswer(result.answer);
    setCitations(result.citations);
  }

  return (
    <main
      style={{
        maxWidth: 720,
        margin: "0 auto",
        padding: "3rem 1.5rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>Codebase RAG Assistant</h1>
      <p style={{ color: "#555" }}>Index a public GitHub repo, then ask questions about it.</p>

      <section style={{ marginTop: "2rem" }}>
        <label style={{ display: "block", fontWeight: 500, marginBottom: "0.5rem" }}>
          Repository URL
        </label>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <input
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            style={{ flex: 1, padding: "0.5rem", border: "1px solid #ccc", borderRadius: 6 }}
          />
          <button onClick={handleIndex} style={{ padding: "0.5rem 1rem", borderRadius: 6 }}>
            Index
          </button>
        </div>
        {indexStatus && <p style={{ color: "#888", marginTop: "0.5rem" }}>Status: {indexStatus}</p>}
      </section>

      <section style={{ marginTop: "2rem" }}>
        <label style={{ display: "block", fontWeight: 500, marginBottom: "0.5rem" }}>
          Ask a question
        </label>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="How does authentication work?"
            style={{ flex: 1, padding: "0.5rem", border: "1px solid #ccc", borderRadius: 6 }}
          />
          <button onClick={handleAsk} style={{ padding: "0.5rem 1rem", borderRadius: 6 }}>
            Ask
          </button>
        </div>
      </section>

      {answer && (
        <section style={{ marginTop: "2rem" }}>
          <h2 style={{ fontSize: "1rem", fontWeight: 600 }}>Answer</h2>
          <p style={{ whiteSpace: "pre-wrap" }}>{answer}</p>
          {citations.length > 0 && (
            <ul style={{ color: "#555", fontSize: "0.9rem" }}>
              {citations.map((c, i) => (
                <li key={i}>
                  {c.file} (lines {c.start_line}-{c.end_line})
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </main>
  );
}
