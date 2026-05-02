// Native img tags used intentionally to avoid slow Next.js image optimization for external CDNs

export default function PlayerProfile({ profile }: { profile: any }) {
  if (!profile) return null;

  return (
    <div className="flex items-center gap-6 bg-app-card rounded p-6 border border-app-border mb-6">
      
      {/* Icon & Level */}
      <div className="relative">
        <div className="w-24 h-24 rounded overflow-hidden border border-app-border relative">
          {profile.profileIconId && (
            <img 
              src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/profileicon/${profile.profileIconId}.png`} 
              alt="Profile Icon" 
              className="w-full h-full object-cover"
            />
          )}
        </div>
        <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-[#121212] text-white text-xs font-bold px-3 py-1 rounded-full border border-app-border">
          {profile.summonerLevel}
        </div>
      </div>

      {/* Info & Ranks */}
      <div className="flex-1">
        <h1 className="text-3xl font-bold text-white mb-1">
          {profile.gameName} <span className="text-app-muted text-xl font-normal">#{profile.tagLine}</span>
        </h1>
        <div className="flex gap-4 mt-3">
          <div className="bg-[#121212] rounded px-4 py-2 border border-app-border">
            <span className="text-app-muted text-xs uppercase tracking-wider block mb-1">Ranked Solo</span>
            <div className="flex items-baseline gap-2">
              <span className="text-white font-bold text-lg">{profile.tier} {profile.rank}</span>
              <span className="text-app-muted text-sm">{profile.lp} LP</span>
            </div>
            <div className="text-xs text-app-muted mt-1">
              <span className="text-[#5383e8]">{profile.wins}W</span> <span className="text-[#e84057]">{profile.losses}L</span>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  );
}
