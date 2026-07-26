const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function indexRepo(repoUrl: string) {
  const res = await fetch(`${API_URL}/repos/index`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });
  if (!res.ok) throw new Error("Failed to start indexing");
  return res.json() as Promise<{ job_id: string; status: string }>;
}

export async function getIndexStatus(jobId: string) {
  const res = await fetch(`${API_URL}/repos/index/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job status");
  return res.json() as Promise<{ status: string; progress?: string; error?: string }>;
}

export async function askQuestion(repoId: string, question: string) {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_id: repoId, question }),
  });
  if (!res.ok) throw new Error("Failed to get answer");
  return res.json() as Promise<{
    answer: string;
    citations: { file: string; start_line: number; end_line: number }[];
  }>;
}
