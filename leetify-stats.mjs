#!/usr/bin/env node
// Print a player's CS2 stats from the Leetify Public CS API.
// Usage: node leetify-stats.mjs <SteamID64 | steamcommunity.com profile URL>
// Optional: LEETIFY_API_KEY in .env or the environment for higher rate limits
// (get one at https://leetify.com/app/developer). Data from Leetify (https://leetify.com).

import { existsSync, readFileSync } from 'node:fs';

const API = 'https://api-public.cs-prod.leetify.com';

function loadEnvKey() {
  if (process.env.LEETIFY_API_KEY) return process.env.LEETIFY_API_KEY;
  if (!existsSync('.env')) return undefined;
  const m = readFileSync('.env', 'utf8').match(/^LEETIFY_API_KEY=(.*)$/m);
  return m ? m[1].trim() : undefined;
}

async function resolveSteam64(input) {
  input = input.trim().replace(/\/+$/, '');
  if (/^\d{17}$/.test(input)) return input;
  const profiles = input.match(/steamcommunity\.com\/profiles\/(\d{17})/);
  if (profiles) return profiles[1];
  const vanity = input.match(/steamcommunity\.com\/id\/([^/?#]+)/)?.[1] ?? (/^[\w-]+$/.test(input) ? input : null);
  if (!vanity) throw new Error(`Not a SteamID64 or Steam profile URL: ${input}`);
  const res = await fetch(`https://steamcommunity.com/id/${encodeURIComponent(vanity)}?xml=1`);
  const id = (await res.text()).match(/<steamID64>(\d{17})<\/steamID64>/)?.[1];
  if (!id) throw new Error(`Could not find a Steam profile for "${vanity}"`);
  return id;
}

async function leetify(path) {
  const key = loadEnvKey();
  const res = await fetch(API + path, { headers: key ? { _leetify_key: key } : {} });
  if (res.status === 404) throw new Error('Leetify has no profile for this player (sign in at leetify.com with Steam so it starts tracking your matches).');
  if (!res.ok) throw new Error(`Leetify API returned HTTP ${res.status}`);
  return res.json();
}

const fmt = (v, digits = 1, suffix = '') => (v == null ? '-' : `${Number(v).toFixed(digits)}${suffix}`);
const pct = (v) => (v == null ? '-' : `${(v <= 1 ? v * 100 : v).toFixed(1)}%`);
// Leetify sends per-match/side ratings as fractions (0.0512); its site shows them as +5.12.
const lr = (v) => (v == null ? '-' : `${v >= 0 ? '+' : ''}${(v * 100).toFixed(2)}`);
const row = (label, value) => console.log(`  ${label.padEnd(28)} ${value}`);

const arg = process.argv[2];
if (!arg) {
  console.error('Usage: node leetify-stats.mjs <SteamID64 | Steam profile URL>');
  process.exit(1);
}

try {
  const steam64 = await resolveSteam64(arg);
  const p = await leetify(`/v3/profile?steam64_id=${steam64}`);
  const r = p.ranks ?? {};
  const rt = p.rating ?? {};
  const s = p.stats ?? {};

  console.log(`\n${p.name} (${p.steam64_id})${p.privacy_mode && p.privacy_mode !== 'public' ? ` [privacy: ${p.privacy_mode}]` : ''}`);
  row('Matches tracked', `${p.total_matches ?? '-'} since ${p.first_match_date?.slice(0, 10) ?? '-'}`);
  row('Win rate', pct(p.winrate));
  if (p.bans?.length) row('Bans', p.bans.map((b) => `${b.platform} since ${b.banned_since?.slice(0, 10)}`).join(', '));

  console.log('\nRanks');
  row('Premier', r.premier ?? '-');
  row('Leetify rating', fmt(r.leetify, 2));
  row('FACEIT', r.faceit ? `level ${r.faceit} (${r.faceit_elo} Elo)` : '-');
  row('Wingman', r.wingman ?? '-');
  for (const c of (r.competitive ?? []).filter((c) => c.rank > 0)) row(`Competitive ${c.map_name}`, c.rank);

  console.log('\nLeetify ratings');
  row('Aim', fmt(rt.aim, 1));
  row('Positioning', fmt(rt.positioning, 1));
  row('Utility', fmt(rt.utility, 1));
  row('Clutch', lr(rt.clutch));
  row('Opening', lr(rt.opening));
  row('CT side / T side', `${lr(rt.ct_leetify)} / ${lr(rt.t_leetify)}`);

  console.log('\nAim & duels');
  row('Reaction time', fmt(s.reaction_time_ms, 0, ' ms'));
  row('Preaim', fmt(s.preaim, 1, '°'));
  row('Headshot accuracy', pct(s.accuracy_head));
  row('Accuracy (enemy spotted)', pct(s.accuracy_enemy_spotted));
  row('Spray accuracy', pct(s.spray_accuracy));
  row('Counter-strafing', pct(s.counter_strafing_good_shots_ratio));
  row('Opening duels CT / T', `${pct(s.ct_opening_duel_success_percentage)} / ${pct(s.t_opening_duel_success_percentage)}`);
  row('Trade kill success', pct(s.trade_kills_success_percentage));

  console.log('\nUtility');
  row('Flashes thrown', fmt(s.flashbang_thrown, 1));
  row('Enemies flashed per flash', fmt(s.flashbang_hit_foe_per_flashbang, 2));
  row('Teammates flashed per flash', fmt(s.flashbang_hit_friend_per_flashbang, 2));
  row('HE damage to enemies', fmt(s.he_foes_damage_avg, 1));
  row('Unused utility on death', `$${fmt(s.utility_on_death_avg, 0)}`);

  const recent = p.recent_matches ?? [];
  if (recent.length) {
    console.log('\nRecent matches');
    for (const m of recent.slice(0, 10)) {
      const score = Array.isArray(m.score) ? m.score.join('-') : '';
      console.log(`  ${m.finished_at?.slice(0, 10)}  ${(m.map_name ?? '').padEnd(12)} ${(m.outcome ?? '').padEnd(5)} ${score.padEnd(6)} rating ${lr(m.leetify_rating).padStart(6)}  ${m.data_source}`);
    }
  }
  console.log('\nData from Leetify (https://leetify.com)');
} catch (e) {
  console.error(`Error: ${e.message}`);
  process.exit(1);
}
