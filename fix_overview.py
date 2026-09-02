"""
Surgically replace the broken old loadOverview tail (listening-story / cats block)
with the new wrapped implementation. Operates on line ranges.
"""

with open('dashboard/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with '// Listening story'
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if '// Listening story' in line and start_idx is None:
        start_idx = i
    if start_idx is not None and "console.error('Error loading overview:', e);" in line:
        # This is the catch — we want to replace up to and including the closing }
        # Lines after this: '  }', '}'
        end_idx = i + 2  # include the '  }' and '}' closing braces
        break

if start_idx is None:
    print("ERROR: Could not find '// Listening story' marker")
    exit(1)

print(f"Found old block at lines {start_idx+1} to {end_idx+1}")
print(f"Content to replace:")
for i in range(start_idx, min(end_idx+1, len(lines))):
    print(f"  {i+1}: {lines[i]}", end='')

new_tail = '''
    // Safe: clear the "Loading..." stub under total listening
    const kpiDateEl = document.getElementById('kpi-date-range');
    if (kpiDateEl) kpiDateEl.textContent = '';

  } catch (e) {
    console.error('Error loading overview base:', e);
  }

  // Wrapped: populate all ov-* sections + lower KPIs from /api/overview/wrapped
  try {
    const w = await apiFetch('/api/overview/wrapped');
    const setEl2 = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };

    setEl2('kpi-sessions', fmt(w.total_sessions || 0));
    setEl2('kpi-active-year', w.most_active_year || '\u2014');
    setEl2('kpi-peak-month', w.most_active_month || '\u2014');
    setEl2('kpi-peak-month-hrs', w.most_active_month_hours ? `${w.most_active_month_hours}h` : '');
    setEl2('kpi-streak', fmt(w.longest_streak_days || 0));

    // Era Timeline
    const eraEl = document.getElementById('ov-era-timeline');
    if (eraEl && w.yearly_eras && w.yearly_eras.length > 0) {
      const maxH = Math.max(...w.yearly_eras.map(e => e.listening_hours));
      eraEl.innerHTML = w.yearly_eras.map(era => `
        <div class="flex items-center gap-4 p-3 rounded-xl bg-surface-container hover:bg-surface-container-high transition-colors">
          <div class="w-14 text-right font-bold text-primary text-lg flex-shrink-0">${era.year}</div>
          <div class="flex-1 min-w-0">
            <div class="h-2 rounded-full bg-primary mb-1" style="width:${Math.max(4, Math.round((era.listening_hours / maxH) * 100))}%"></div>
            <div class="flex flex-wrap gap-3 text-xs text-on-surface-variant">
              <span>${fmtHrs(era.listening_hours)} hrs</span>
              <span>${fmt(era.plays)} plays</span>
              <span>${fmt(era.unique_artists)} artists</span>
              ${era.dominant_artist ? `<span class="text-on-surface font-medium">\\u2191 ${era.dominant_artist}</span>` : ''}
            </div>
          </div>
          <div class="text-xs text-on-surface-variant flex-shrink-0">${fmt(era.unique_tracks)} tracks</div>
        </div>`).join('');
    }

    // Top Artists grid
    const taEl = document.getElementById('ov-top-artists');
    if (taEl && w.top_artists && w.top_artists.length > 0) {
      taEl.innerHTML = w.top_artists.slice(0, 10).map((a, i) => `
        <div class="bg-surface-container rounded-xl p-4 flex flex-col gap-2 hover:bg-surface-container-high transition-colors cursor-pointer" onclick="navigate('artists')">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-primary">#${i + 1}</span>
            <span class="text-xs text-on-surface-variant">${a.lifecycle_stage || ''}</span>
          </div>
          <p class="font-semibold text-on-surface text-sm truncate">${a.artist_name}</p>
          <div class="flex justify-between text-xs text-on-surface-variant">
            <span>${fmtHrs(a.total_hours)} hrs</span>
            <span>${fmt(a.total_plays)} plays</span>
          </div>
        </div>`).join('');
    }

    // Top Songs list
    const tsEl = document.getElementById('ov-top-songs');
    if (tsEl && w.top_songs && w.top_songs.length > 0) {
      tsEl.innerHTML = w.top_songs.slice(0, 10).map((s, i) => `
        <div class="flex items-center gap-4 p-3 rounded-xl bg-surface-container hover:bg-surface-container-high transition-colors">
          <span class="text-sm font-bold text-primary w-6 text-right flex-shrink-0">${i + 1}</span>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-on-surface text-sm truncate">${s.track_name}</p>
            <p class="text-xs text-on-surface-variant truncate">${s.artist_name}${s.project_name ? ' \xb7 ' + s.project_name : ''}</p>
          </div>
          <div class="text-right flex-shrink-0">
            <p class="text-sm font-bold text-on-surface">${fmt(s.total_plays)} plays</p>
            <p class="text-xs text-on-surface-variant">${fmtHrs(s.total_minutes / 60)} hrs</p>
          </div>
          ${catBadge(s.lifecycle_category)}
        </div>`).join('');
    }

    // Top Projects grid
    const tpEl = document.getElementById('ov-top-projects');
    if (tpEl && w.top_projects && w.top_projects.length > 0) {
      tpEl.innerHTML = w.top_projects.slice(0, 6).map(p => `
        <div class="bg-surface-container rounded-xl p-4 hover:bg-surface-container-high transition-colors cursor-pointer" onclick="navigate('albums')">
          <p class="font-semibold text-on-surface text-sm truncate mb-1">${p.project_name}</p>
          <p class="text-xs text-on-surface-variant truncate mb-3">${p.artist_name}</p>
          <div class="flex justify-between text-xs">
            <span class="text-primary font-bold">${fmtHrs(p.total_hours)} hrs</span>
            <span class="text-on-surface-variant">${fmt(p.tracks_heard)} tracks</span>
          </div>
          ${p.top_song_name ? `<p class="text-xs text-on-surface-variant mt-2 truncate">\\u2191 ${p.top_song_name}</p>` : ''}
        </div>`).join('');
    }

    // Top Catalyst hero card
    const tcEl = document.getElementById('ov-top-catalyst');
    if (tcEl) {
      try {
        const tc = await apiFetch('/api/discovery/top-catalyst');
        if (tc && tc.catalyst_artist_name) {
          tcEl.innerHTML = `
            <div class="bg-gradient-to-br from-primary/20 to-transparent border border-primary/30 rounded-xl p-6 flex items-start gap-6">
              <div class="w-16 h-16 rounded-xl bg-primary/20 flex items-center justify-center flex-shrink-0">
                <span class="material-symbols-outlined text-primary text-3xl">rocket_launch</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs uppercase tracking-widest text-primary font-bold mb-1">#1 Discovery Catalyst</p>
                <p class="text-2xl font-black text-on-surface mb-1">${tc.catalyst_artist_name}</p>
                <p class="text-sm text-on-surface-variant mb-3">${tc.catalyst_track_name || ''}</p>
                <div class="flex flex-wrap gap-4 text-xs text-on-surface-variant">
                  <span>${fmt(tc.tracks_7d || 0)} new tracks in 7 days</span>
                  <span>${fmt(tc.minutes_30d || 0)} min over 30 days</span>
                </div>
              </div>
            </div>`;
        }
      } catch (_) {}
    }

    // Deepest Dives (artists by hours)
    const ddEl = document.getElementById('ov-deepest-dives');
    if (ddEl && w.top_artists && w.top_artists.length > 0) {
      ddEl.innerHTML = w.top_artists.slice(0, 6).map((a, i) => `
        <div class="bg-surface-container rounded-xl p-4 hover:bg-surface-container-high transition-colors cursor-pointer" onclick="navigate('artists')">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-primary">#${i + 1}</span>
            <span class="text-xs text-on-surface-variant">${a.unique_projects || 0} projects</span>
          </div>
          <p class="font-semibold text-on-surface text-sm truncate mb-1">${a.artist_name}</p>
          <div class="flex justify-between text-xs text-on-surface-variant">
            <span>${fmtHrs(a.total_hours)} hrs</span>
            <span>${fmt(a.unique_tracks || 0)} tracks</span>
          </div>
        </div>`).join('');
    }

    // Most Replayed songs
    const mrEl = document.getElementById('ov-most-replayed');
    if (mrEl && w.top_replayed && w.top_replayed.length > 0) {
      mrEl.innerHTML = w.top_replayed.slice(0, 8).map((s, i) => `
        <div class="flex items-center gap-4 p-3 rounded-xl bg-surface-container hover:bg-surface-container-high transition-colors">
          <span class="text-sm font-bold text-primary w-6 text-right flex-shrink-0">${i + 1}</span>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-on-surface text-sm truncate">${s.track_name}</p>
            <p class="text-xs text-on-surface-variant truncate">${s.artist_name}</p>
          </div>
          <span class="text-sm font-bold text-on-surface flex-shrink-0">${fmt(s.total_plays)}\xd7</span>
        </div>`).join('');
    }

    // Revival artists
    const rvEl = document.getElementById('ov-revivals');
    if (rvEl && w.revival_artists && w.revival_artists.length > 0) {
      rvEl.innerHTML = w.revival_artists.map(a => `
        <div class="bg-surface-container rounded-xl p-4 hover:bg-surface-container-high transition-colors cursor-pointer" onclick="navigate('artists')">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-primary">${fmt(a.revival_count)}\xd7 revivals</span>
            <span class="text-xs text-on-surface-variant">${a.lifecycle_stage || ''}</span>
          </div>
          <p class="font-semibold text-on-surface text-sm truncate mb-1">${a.artist_name}</p>
          <p class="text-xs text-on-surface-variant">${fmtHrs(a.total_hours)} hrs total</p>
        </div>`).join('');
    }

    // Listening Story statements
    const stEl = document.getElementById('ov-story');
    if (stEl && w.story_statements && w.story_statements.length > 0) {
      stEl.innerHTML = w.story_statements.map(s => `
        <div class="flex items-start gap-3 p-4 bg-surface-container rounded-xl">
          <span class="material-symbols-outlined text-primary flex-shrink-0 mt-0.5">auto_stories</span>
          <p class="text-sm text-on-surface leading-relaxed">${s}</p>
        </div>`).join('');
    }

  } catch (e) {
    console.error('Error loading overview wrapped:', e);
  }
}
'''

# Replace lines from start_idx to end_idx (inclusive)
new_lines = lines[:start_idx] + [new_tail + '\n'] + lines[end_idx + 1:]

with open('dashboard/app.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\nSUCCESS: Replaced {end_idx - start_idx + 1} lines ({start_idx+1}-{end_idx+1}) with new wrapped implementation")
print(f"New file length: {len(new_lines)} lines")
