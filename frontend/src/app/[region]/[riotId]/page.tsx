"use client";
import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import PlayerProfile from '@/components/PlayerProfile';
import MatchCard from '@/components/MatchCard';

export default function DashboardPage() {
  const params = useParams();
  const router = useRouter();

  const currentRegion = params.region as string;
  const currentRiotId = decodeURIComponent(params.riotId as string);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dashboardData, setDashboardData] = useState<any>(null);

  // Search Bar state for the header
  const [searchRegion, setSearchRegion] = useState(currentRegion || 'br1');
  const [searchRiotId, setSearchRiotId] = useState('');

  // Chat State
  const [chatMessages, setChatMessages] = useState<{ role: string, content: string }[]>([
    { role: "assistant", content: "Ask about your latest matches, I can help you!" }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    if (currentRegion && currentRiotId) {
      fetchDashboardData(currentRegion, currentRiotId);
    }
  }, [currentRegion, currentRiotId]);

  const fetchDashboardData = async (reg: string, id: string) => {
    setLoading(true);
    setError('');
    setDashboardData(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/matches/${reg}/${id}`);
      if (!res.ok) {
        throw new Error('Player not found or Riot API error');
      }
      const json = await res.json();
      setDashboardData(json.data);
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching matches');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchRiotId.trim()) return;

    const cleanId = searchRiotId.replace('#', '-');
    router.push(`/${searchRegion}/${cleanId}`);
  };

  const sendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = chatInput;
    setChatInput('');
    setChatMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setChatLoading(true);

    try {
      const payload = {
        message: userMessage,
        history: chatMessages.slice(1) // exclude the initial welcome message from context
      };
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/chat/${currentRegion}/${currentRiotId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Chat API failed');
      const data = await res.json();

      setChatMessages(prev => [...prev, { role: "assistant", content: data.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { role: "assistant", content: "Sorry, I couldn't process that right now. Ensure GEMINI_API_KEY is set." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const getSelectClass = (compact: boolean) => `bg-transparent text-app-text px-4 outline-none border-r border-app-border cursor-pointer ${compact ? 'py-3' : 'py-4 text-lg'}`;
  const getInputClass = (compact: boolean) => `flex-1 bg-transparent px-6 outline-none text-app-text placeholder-app-muted ${compact ? 'py-3' : 'py-4 text-lg'}`;
  const getButtonClass = (compact: boolean) => `bg-primary text-white font-bold hover:bg-[#436aca] transition-colors ${compact ? 'px-6 py-3' : 'px-10 py-4 text-lg'} disabled:opacity-50`;
  const getFormClass = (compact: boolean) => `flex w-full bg-app-card rounded overflow-hidden border border-app-border focus-within:border-primary transition-colors ${compact ? 'max-w-2xl' : 'max-w-3xl'}`;

  return (
    <main className="min-h-screen text-app-text p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6 animate-in slide-in-from-bottom-4 fade-in duration-500">

        {/* Header with Search */}
        <header className="flex flex-col lg:flex-row items-center justify-between gap-6 bg-app-card p-4 rounded border border-app-border">
          <h1 className="text-2xl font-bold text-primary cursor-pointer hover:underline" onClick={() => router.push('/')}>
            LOL Stats
          </h1>
          <form
            onSubmit={handleSearch}
            className={getFormClass(true)}
          >
            <select value={searchRegion} onChange={(e) => setSearchRegion(e.target.value)} className={getSelectClass(true)}>
              <option value="br1" className="bg-app-bg">BR1</option>
              <option value="na1" className="bg-app-bg">NA1</option>
              <option value="euw1" className="bg-app-bg">EUW1</option>
              <option value="kr" className="bg-app-bg">KR</option>
            </select>
            <input
              type="text" placeholder="GameName#TAG"
              value={searchRiotId} onChange={(e) => setSearchRiotId(e.target.value)}
              className={getInputClass(true)}
            />
            <button type="submit" disabled={loading} className={getButtonClass(true)}>
              Search
            </button>
          </form>
        </header>

        {/* Loading & Error States */}
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}

        {error && (
          <div className="bg-[#59343b] text-[#e84057] p-4 rounded border border-[#e84057] font-bold">
            {error}
          </div>
        )}

        {/* Dashboard Content */}
        {dashboardData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <PlayerProfile profile={dashboardData.profile} />

              <div className="space-y-2">
                {dashboardData.matches.map((match: any, idx: number) => (
                  <MatchCard key={idx} match={match} />
                ))}
              </div>
            </div>

            <div className="bg-app-card rounded p-5 border border-app-border h-[700px] flex flex-col">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-white">
                <div className="w-2 h-4 bg-primary rounded-sm"></div>
                AI Coach
              </h2>

              <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 flex flex-col">
                {chatMessages.map((msg, i) => (
                  <div key={i} className={`p-3 rounded text-sm max-w-[85%] ${msg.role === 'user' ? 'bg-primary text-white self-end' : 'bg-[#2b2d31] border border-app-border text-app-text self-start'}`}>
                    <ReactMarkdown
                      components={{
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        strong: ({ node, ...props }) => <strong className="font-bold text-white" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                        li: ({ node, ...props }) => <li {...props} />
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ))}
                {chatLoading && (
                  <div className="bg-[#2b2d31] border border-app-border p-3 rounded text-sm text-app-muted self-start animate-pulse">
                    Thinking...
                  </div>
                )}
              </div>

              <form className="mt-auto" onSubmit={sendChatMessage}>
                <div className="flex gap-2 bg-[#2b2d31] p-1 rounded border border-app-border focus-within:border-primary transition-colors">
                  <input
                    type="text"
                    placeholder="Ask for tips or analysis..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    disabled={chatLoading}
                    className="flex-1 bg-transparent px-3 py-2 text-sm outline-none text-white placeholder-app-muted disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={chatLoading}
                    className="bg-primary text-white hover:bg-[#436aca] transition-colors px-4 py-2 rounded text-sm font-semibold disabled:opacity-50"
                  >
                    Send
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
