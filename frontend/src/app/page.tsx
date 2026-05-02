"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [riotId, setRiotId] = useState('');
  const [region, setRegion] = useState('br1');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!riotId.trim()) return;
    
    const cleanId = riotId.replace('#', '-');
    router.push(`/${region}/${cleanId}`);
  };

  const getSelectClass = (compact: boolean) => `bg-transparent text-app-text px-4 outline-none border-r border-app-border cursor-pointer ${compact ? 'py-3' : 'py-4 text-lg'}`;
  const getInputClass = (compact: boolean) => `flex-1 bg-transparent px-6 outline-none text-app-text placeholder-app-muted ${compact ? 'py-3' : 'py-4 text-lg'}`;
  const getButtonClass = (compact: boolean) => `bg-primary text-white font-bold hover:bg-[#436aca] transition-colors ${compact ? 'px-6 py-3' : 'px-10 py-4 text-lg'} disabled:opacity-50`;
  const getFormClass = (compact: boolean) => `flex w-full bg-app-card rounded overflow-hidden border border-app-border focus-within:border-primary transition-colors ${compact ? 'max-w-2xl' : 'max-w-3xl'}`;

  return (
    <main className="min-h-screen text-app-text p-4 md:p-8 flex flex-col items-center justify-center space-y-8 animate-in fade-in duration-500">
      <div className="text-center space-y-2">
        <h1 className="text-5xl md:text-7xl font-bold text-primary tracking-tight">
          LOL Stats
        </h1>
        <p className="text-app-muted text-lg max-w-xl mx-auto">
          Search your Riot ID to track matches and get AI coaching.
        </p>
      </div>
      
      <form 
        onSubmit={handleSearch}
        className={getFormClass(false)}
      >
        <select value={region} onChange={(e) => setRegion(e.target.value)} className={getSelectClass(false)}>
          <option value="br1" className="bg-app-bg">BR1</option>
          <option value="na1" className="bg-app-bg">NA1</option>
          <option value="euw1" className="bg-app-bg">EUW1</option>
          <option value="kr" className="bg-app-bg">KR</option>
        </select>
        <input 
          type="text" placeholder="GameName#TAG" 
          value={riotId} onChange={(e) => setRiotId(e.target.value)}
          className={getInputClass(false)}
        />
        <button type="submit" className={getButtonClass(false)}>
          Search
        </button>
      </form>
    </main>
  );
}
