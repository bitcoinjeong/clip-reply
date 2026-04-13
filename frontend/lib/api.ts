const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface TranscriptResult {
  transcript: string;
  source: string;
  duration: number;
  video_id: string | null;
  word_count: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function fetchTranscript(url: string): Promise<TranscriptResult> {
  const res = await fetch(`${API_URL}/api/transcript`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Failed to fetch transcript");
  }
  return res.json();
}

export async function fetchSummary(
  transcript: string,
  lang: string
): Promise<string> {
  const res = await fetch(`${API_URL}/api/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript, lang }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Failed to summarize");
  }
  const data = await res.json();
  return data.summary;
}

export async function fetchChatAnswer(
  transcript: string,
  question: string,
  chatHistory: ChatMessage[],
  lang: string
): Promise<string> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      transcript,
      question,
      chat_history: chatHistory,
      lang,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Failed to get answer");
  }
  const data = await res.json();
  return data.answer;
}
