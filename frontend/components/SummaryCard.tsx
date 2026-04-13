"use client";

interface SummaryCardProps {
  summary: string;
  videoUrl: string;
  videoId: string | null;
  duration: number;
  wordCount: number;
  transcript: string;
}

export default function SummaryCard({
  summary,
  videoUrl,
  videoId,
  duration,
  wordCount,
  transcript,
}: SummaryCardProps) {
  const durMin = Math.floor(duration);
  const durSec = Math.round((duration % 1) * 60);
  const durStr = duration > 0 ? `${durMin}m ${durSec}s` : "N/A";

  function handleDownload() {
    const text = [
      "ClipReply Summary",
      "=".repeat(40),
      `Video: ${videoUrl}`,
      `Duration: ${durStr}`,
      "",
      "--- Summary ---",
      summary,
      "",
      "--- Transcript ---",
      transcript.slice(0, 5000),
    ].join("\n");

    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "clipreply_summary.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-4">
      {/* Video info */}
      <div className="flex gap-4 px-4 py-3 bg-gray-800/50 rounded-lg text-sm text-gray-400">
        <span>
          Duration: <b className="text-gray-200">{durStr}</b>
        </span>
        <span>
          Words: <b className="text-gray-200">{wordCount.toLocaleString()}</b>
        </span>
        <span>
          Source: <b className="text-gray-200">YouTube</b>
        </span>
      </div>

      {/* Embedded player */}
      {videoId && (
        <div className="aspect-video rounded-lg overflow-hidden">
          <iframe
            src={`https://www.youtube.com/embed/${videoId}`}
            className="w-full h-full"
            allowFullScreen
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          />
        </div>
      )}

      {/* Summary */}
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Summary</h2>
        <div className="prose prose-invert prose-sm max-w-none whitespace-pre-wrap">
          {summary}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleDownload}
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm transition-colors"
        >
          Download Summary (.txt)
        </button>
      </div>
    </div>
  );
}
