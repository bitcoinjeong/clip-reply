"use client";

import { useState } from "react";
import VideoInput from "@/components/VideoInput";
import SummaryCard from "@/components/SummaryCard";
import Chat from "@/components/Chat";
import { fetchTranscript, fetchSummary, type TranscriptResult } from "@/lib/api";

const FREE_LIMIT = 3;

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState("");

  const [transcriptData, setTranscriptData] = useState<TranscriptResult | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [lang, setLang] = useState("ko");
  const [videosToday, setVideosToday] = useState(0);

  const remaining = Math.max(0, FREE_LIMIT - videosToday);

  async function handleSubmit(url: string, selectedLang: string) {
    if (remaining <= 0) return;

    setLoading(true);
    setError(null);
    setSummary(null);
    setTranscriptData(null);
    setVideoUrl(url);
    setLang(selectedLang);

    try {
      setStatus("Extracting transcript...");
      const data = await fetchTranscript(url);
      setTranscriptData(data);
      setVideosToday((v) => v + 1);

      setStatus("AI is summarizing...");
      const summaryText = await fetchSummary(data.transcript, selectedLang);
      setSummary(summaryText);
      setStatus("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setStatus("");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setSummary(null);
    setTranscriptData(null);
    setVideoUrl("");
    setError(null);
    setStatus("");
  }

  return (
    <div className="flex-1 flex flex-col">
      <main className="flex-1 w-full max-w-3xl mx-auto px-4 py-8 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">ClipReply</h1>
          <p className="text-gray-400 mt-1">
            Paste a video link. Get the summary. Ask anything.
          </p>
        </div>

        {/* Input */}
        <VideoInput
          onSubmit={handleSubmit}
          loading={loading}
          disabled={remaining <= 0}
        />

        {/* Free limit warning */}
        {remaining <= 0 && (
          <div className="px-4 py-3 bg-yellow-900/30 border border-yellow-700 rounded-lg text-yellow-200 text-sm">
            Free limit reached ({FREE_LIMIT}/day). Upgrade to{" "}
            <b>Pro ($9/mo)</b> for unlimited videos.
          </div>
        )}

        {/* Status */}
        {status && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            {status}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="px-4 py-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
            {error}
          </div>
        )}

        {/* Results */}
        {summary && transcriptData && (
          <>
            <SummaryCard
              summary={summary}
              videoUrl={videoUrl}
              videoId={transcriptData.video_id}
              duration={transcriptData.duration}
              wordCount={transcriptData.word_count}
              transcript={transcriptData.transcript}
            />

            <hr className="border-gray-800" />

            <Chat transcript={transcriptData.transcript} lang={lang} />

            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm transition-colors"
            >
              New video
            </button>
          </>
        )}

        {/* Footer */}
        <div className="pt-4 border-t border-gray-800 text-xs text-gray-500">
          Free: {remaining}/{FREE_LIMIT} videos remaining today &nbsp;|&nbsp;{" "}
          <b>Pro $9/mo</b>: unlimited + long videos + PDF export
        </div>
      </main>
    </div>
  );
}
