"use client";

interface VideoInputProps {
  onSubmit: (url: string, lang: string) => void;
  loading: boolean;
  disabled: boolean;
}

export default function VideoInput({
  onSubmit,
  loading,
  disabled,
}: VideoInputProps) {
  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const url = formData.get("url") as string;
    const lang = formData.get("lang") as string;
    if (url.trim()) onSubmit(url.trim(), lang);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        name="url"
        type="url"
        placeholder="https://www.youtube.com/watch?v=..."
        required
        disabled={disabled}
        className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <select
        name="lang"
        defaultValue="ko"
        className="px-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="ko">한국어</option>
        <option value="en">English</option>
      </select>
      <button
        type="submit"
        disabled={loading || disabled}
        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-semibold rounded-lg transition-colors"
      >
        {loading ? "..." : "Go"}
      </button>
    </form>
  );
}
