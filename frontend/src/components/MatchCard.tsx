// Native img tags used intentionally to avoid slow Next.js image optimization for external CDNs
import Link from 'next/link';
import { useParams } from 'next/navigation';

const SPELL_MAP: Record<number, string> = {
  1: "SummonerBoost", 3: "SummonerExhaust", 4: "SummonerFlash",
  6: "SummonerHaste", 7: "SummonerHeal", 11: "SummonerSmite",
  12: "SummonerTeleport", 13: "SummonerMana", 14: "SummonerDot",
  21: "SummonerBarrier", 32: "SummonerSnowball"
};

export default function MatchCard({ match }: { match: any }) {
  const params = useParams();
  const region = params.region || 'br1';
  if (!match) return null;

  const isWin = match.win;
  const bgColor = isWin ? 'bg-[var(--color-win-bg)]' : 'bg-[var(--color-loss-bg)]';
  const borderColor = isWin ? 'border-[#5383e8]' : 'border-[#e84057]';
  const labelColor = isWin ? 'text-[#5383e8]' : 'text-[#e84057]';

  // Format duration
  const minutes = Math.floor(match.gameDuration / 60);
  const seconds = match.gameDuration % 60;
  const durationStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

  // KDA Ratio
  const deaths = match.deaths === 0 ? 1 : match.deaths;
  const kdaRatio = ((match.kills + match.assists) / deaths).toFixed(2);

  // Fallback for champion name formatting if needed (e.g. FiddleSticks)
  const formatChampName = (name: string) => {
    if (!name) return "Unknown";
    // Usually Riot API returns the correct key, but in case we need overrides:
    if (name === "Fiddlesticks") return "FiddleSticks";
    return name;
  };

  return (
    <div className={`flex w-full ${bgColor} rounded border-l-[6px] ${borderColor} text-[#9e9eb1] text-[12px] font-sans overflow-hidden mb-2`}>
      
      {/* 1. Match Info */}
      <div className="w-[100px] p-3 flex flex-col justify-center">
        <div className={`font-bold ${labelColor} mb-1 leading-tight`}>{match.queueName}</div>
        <div className="mb-2 leading-tight">Recent</div> {/* We can format gameCreation properly later */}
        <div className="w-8 h-[1px] bg-[#31313c] mb-2"></div>
        <div className={`font-bold mb-1 leading-tight ${labelColor}`}>{isWin ? 'Victory' : 'Defeat'}</div>
        <div className="leading-tight">{durationStr}</div>
      </div>

      {/* 2. Champion, Spells, Runes, Items */}
      <div className="flex flex-col justify-center py-3 px-2">
        <div className="flex gap-[2px] mb-2">
          {/* Champion Icon */}
          <div className="relative w-12 h-12 rounded overflow-hidden mr-1">
            {match.championName && (
               <img src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/champion/${formatChampName(match.championName)}.png`} alt={match.championName} className="w-full h-full object-cover" />
            )}
          </div>
          {/* Spells */}
          <div className="flex flex-col gap-[2px]">
             <div className="w-[22px] h-[22px] rounded overflow-hidden bg-[#31313c]">
               {match.summoner1Id && SPELL_MAP[match.summoner1Id] && <img src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/spell/${SPELL_MAP[match.summoner1Id]}.png`} alt="Spell 1" className="w-full h-full" />}
             </div>
             <div className="w-[22px] h-[22px] rounded overflow-hidden bg-[#31313c]">
               {match.summoner2Id && SPELL_MAP[match.summoner2Id] && <img src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/spell/${SPELL_MAP[match.summoner2Id]}.png`} alt="Spell 2" className="w-full h-full" />}
             </div>
          </div>
          {/* Runes */}
          <div className="flex flex-col gap-[2px]">
             <div className="w-[22px] h-[22px] rounded-full overflow-hidden bg-[#18181b]">
               {match.primaryStyle && <img src={`https://opgg-static.akamaized.net/meta/images/lol/latest/perk/${match.primaryStyle}.png`} alt="Primary Rune" className="w-full h-full" />}
             </div>
             <div className="w-[22px] h-[22px] rounded-full overflow-hidden bg-[#18181b]">
               {match.subStyle && <img src={`https://opgg-static.akamaized.net/meta/images/lol/latest/perkStyle/${match.subStyle}.png`} alt="Sub Rune" className="w-full h-full p-[2px]" />}
             </div>
          </div>
        </div>
        
        {/* Items (7 slots) */}
        <div className="flex gap-[2px]">
          {match.items && match.items.slice(0, 6).map((item: number, idx: number) => (
            <div key={idx} className={`w-[22px] h-[22px] rounded overflow-hidden ${item > 0 ? '' : 'bg-black/40 shadow-inner'}`}>
              {item > 0 && <img src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/item/${item}.png`} alt={`Item ${item}`} className="w-full h-full" />}
            </div>
          ))}
          <div className={`w-[22px] h-[22px] rounded-full overflow-hidden ml-1 ${match.items && match.items[6] > 0 ? '' : 'bg-black/40 shadow-inner'}`}>
             {match.items && match.items[6] > 0 && <img src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/item/${match.items[6]}.png`} alt={`Trinket`} className="w-full h-full" />}
          </div>
        </div>
      </div>

      {/* 3. KDA */}
      <div className="flex flex-col justify-center items-center px-6 min-w-[100px]">
        <div className="text-[15px] font-bold text-white mb-1">
          {match.kills} <span className="text-[#9e9eb1] font-normal">/</span> <span className="text-[#e84057]">{match.deaths}</span> <span className="text-[#9e9eb1] font-normal">/</span> {match.assists}
        </div>
        <div className="text-[#9e9eb1] mb-1 font-medium">{kdaRatio} KDA</div>
      </div>

      {/* 4. Teams */}
      <div className="flex flex-1 justify-end py-3 px-4 gap-4 border-l border-[#31313c]">
        {match.teams && match.teams.map((team: any[], teamIdx: number) => (
          <div key={teamIdx} className="flex flex-col gap-[1px] w-[90px]">
            {team.map((player: any, idx: number) => (
              <div key={idx} className="flex items-center gap-1 overflow-hidden">
                <div className="w-4 h-4 rounded overflow-hidden flex-shrink-0 bg-[#31313c]">
                  {player.championName && <img src={`https://ddragon.leagueoflegends.com/cdn/16.9.1/img/champion/${formatChampName(player.championName)}.png`} alt={player.championName} className="w-full h-full object-cover" />}
                </div>
                <Link 
                  href={`/${region}/${player.summonerName}-${player.tagLine}`} 
                  className={`truncate hover:underline cursor-pointer transition-colors block ${player.championName === match.championName ? 'text-white font-bold' : 'text-[#9e9eb1]'}`}
                  title={`${player.summonerName}#${player.tagLine}`}
                >
                  {player.summonerName}
                </Link>
              </div>
            ))}
          </div>
        ))}
      </div>
      
    </div>
  );
}
