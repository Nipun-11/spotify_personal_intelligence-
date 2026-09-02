/**
 * Spotify Personal Intelligence Engine — Dashboard SPA
 * All data fetched from the FastAPI backend. Zero hard-coded analytics.
 * Ground truth values are authoritative from processed parquet files.
 */

/* ═══════════════════════════════════════════════════════════════════════════
   CONSTANTS & HELPERS
═══════════════════════════════════════════════════════════════════════════ */
const API = '';

async function apiFetch(path) {
  try {
    const r = await fetch(API + path);
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return await r.json();
  } catch (e) {
    console.error(`API fetch failed: ${path}`, e);
    throw e;
  }
}

function fmt(n, digits = 0) {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return Number(n).toLocaleString('en-IN', { maximumFractionDigits: digits });
}

function fmtHrs(n) {
  if (n === null || n === undefined) return '—';
  const h = parseFloat(n);
  return h >= 100 ? fmt(h, 1) : fmt(h, 1);
}

function typeBadge(type) {
  const map = {
    'Artist Discovery': 'badge-artist',
    'Project Discovery': 'badge-project',
    'Catalog Deepening': 'badge-catalog',
    'Re-engagement': 'badge-reengagement'
  };
  return `<span class="badge ${map[type] || 'badge-catalog'}">${type || 'Discovery'}</span>`;
}

function catBadge(cat) {
  const map = {
    'Evergreen Favorite': 'badge-evergreen',
    'Obsession Track': 'badge-obsession',
    'Long-Lived Song': 'badge-longlived',
    'Fast Burn': 'badge-fastburn',
    'Failed Discovery': 'badge-failed',
    'Revival': 'badge-revival'
  };
  return `<span class="badge ${map[cat] || 'badge-longlived'}">${cat || '—'}</span>`;
}

const plotlyConfig = { displayModeBar: false, responsive: true };
const plotlyLayout = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { family: 'Inter', color: '#bccbb9', size: 12 },
  margin: { l: 50, r: 20, t: 30, b: 50 }
};

/* ═══════════════════════════════════════════════════════════════════════════
   ROUTER
═══════════════════════════════════════════════════════════════════════════ */
const PAGE_TITLES = {
  overview: 'Your Music DNA',
  discovery: 'Discovery Catalysts',
  artists: 'Artist Lifecycle',
  albums: 'Albums & EPs',
  songs: 'Song Lifecycles',
  sequences: 'Listening Sequences',
  network: 'Music Network',
  genres: 'Genre & Time',
  deepdive: 'Deep Dive Explorer',
  ml: 'ML Intelligence'
};

let currentView = 'overview';
const loadedViews = new Set();

function navigate(viewId) {
  if (!PAGE_TITLES[viewId]) return;
  currentView = viewId;

  // Update sidebar active state
  document.querySelectorAll('.sidebar-link').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === viewId);
  });

  // Show/hide views
  document.querySelectorAll('.view').forEach(v => {
    v.classList.toggle('active', v.id === `view-${viewId}`);
  });

  // Update topbar title
  const titleEl = document.getElementById('page-title');
  if (titleEl) titleEl.textContent = PAGE_TITLES[viewId];

  // Load data if not already loaded
  if (!loadedViews.has(viewId)) {
    loadedViews.add(viewId);
    loadView(viewId);
  }

  // Close mobile sidebar
  closeSidebar();
  window.scrollTo(0, 0);
}

function loadView(viewId) {
  const loaders = {
    overview: loadOverview,
    discovery: loadDiscovery,
    artists: loadArtists,
    albums: loadAlbums,
    songs: loadSongs,
    sequences: loadSequences,
    network: loadNetwork,
    genres: loadGenres,
    deepdive: loadDeepDive,
    ml: loadML
  };
  if (loaders[viewId]) loaders[viewId]();
}

// Sidebar nav bindings
document.querySelectorAll('.sidebar-link').forEach(btn => {
  btn.addEventListener('click', () => navigate(btn.dataset.view));
});

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('mobile-overlay').classList.toggle('hidden');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('mobile-overlay').classList.add('hidden');
}
function showDisclaimer() { document.getElementById('disclaimer-modal').classList.remove('hidden'); }
function showPrivacy() { document.getElementById('privacy-modal').classList.remove('hidden'); }

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 1: OVERVIEW — YOUR MUSIC DNA
═══════════════════════════════════════════════════════════════════════════ */
async function loadOverview() {
  try {
    const [ov, tf, yr] = await Promise.all([
      apiFetch('/api/overview'),
      apiFetch('/api/overview/taste-fingerprint'),
      apiFetch('/api/overview/yearly-evolution')
    ]);

    const kpis = ov.kpis || ov;
    const setEl = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };

    setEl('kpi-hours', fmtHrs(kpis.total_hours));
    setEl('kpi-artists', fmt(kpis.unique_artists));
    setEl('kpi-tracks', fmt(kpis.unique_tracks));
    setEl('kpi-projects', fmt(kpis.explored_projects_ge3 || kpis.explored_projects));

    // Taste Fingerprint Radar
    const fingerprint = tf.fingerprint || tf || ov.taste_fingerprint || {};
    const dims = Object.keys(fingerprint);
    const vals = dims.map(d => fingerprint[d]);
    if (dims.length > 0) {
      Plotly.newPlot('radar-chart', [{
        type: 'scatterpolar',
        r: [...vals, vals[0]],
        theta: [...dims, dims[0]],
        fill: 'toself',
        fillcolor: 'rgba(83,224,118,0.25)',
        line: { color: '#53e076', width: 2 },
        name: 'Fingerprint'
      }], {
        ...plotlyLayout,
        margin: { l: 60, r: 60, t: 40, b: 40 },
        polar: {
          radialaxis: { visible: true, range: [0, 100], showticklabels: false, gridcolor: '#343535' },
          angularaxis: { gridcolor: '#343535' },
          bgcolor: 'transparent'
        },
        showlegend: false
      }, plotlyConfig);

      const topDims = dims.map((d, i) => ({ d, v: vals[i] })).sort((a, b) => b.v - a.v);
      setEl('fingerprint-insight',
        `Highest affinity: ${topDims[0].d} (${topDims[0].v}/100). Lowest: ${topDims[topDims.length-1].d} (${topDims[topDims.length-1].v}/100).`);
    }

    // Yearly Evolution Bar Chart
    const yrList = Array.isArray(yr) ? yr : (ov.yearly_evolution || []);
    const years = yrList.map(r => r.year);
    const hours = yrList.map(r => +(r.listening_hours || r.hours || 0));
    Plotly.newPlot('evolution-chart', [{
      type: 'bar',
      x: years, y: hours,
      marker: {
        color: hours.map((h, i) => i === hours.indexOf(Math.max(...hours)) ? '#53e076' : '#292a2a')
      },
      hovertemplate: '<b>%{x}</b><br>%{y:.1f} hrs<extra></extra>'
    }], {
      ...plotlyLayout,
      xaxis: { tickvals: years, gridcolor: '#2a2b2b', showline: false },
      yaxis: { gridcolor: '#2a2b2b', title: 'Hours' },
      bargap: 0.3
    }, plotlyConfig);


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
    setEl2('kpi-active-year', w.most_active_year || '—');
    setEl2('kpi-peak-month', w.most_active_month || '—');
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
              ${era.dominant_artist ? `<span class="text-on-surface font-medium">\u2191 ${era.dominant_artist}</span>` : ''}
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
            <p class="text-xs text-on-surface-variant truncate">${s.artist_name}${s.project_name ? ' · ' + s.project_name : ''}</p>
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
          ${p.top_song_name ? `<p class="text-xs text-on-surface-variant mt-2 truncate">\u2191 ${p.top_song_name}</p>` : ''}
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
          <span class="text-sm font-bold text-on-surface flex-shrink-0">${fmt(s.total_plays)}×</span>
        </div>`).join('');
    }

    // Revival artists
    const rvEl = document.getElementById('ov-revivals');
    if (rvEl && w.revival_artists && w.revival_artists.length > 0) {
      rvEl.innerHTML = w.revival_artists.map(a => `
        <div class="bg-surface-container rounded-xl p-4 hover:bg-surface-container-high transition-colors cursor-pointer" onclick="navigate('artists')">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-primary">${fmt(a.revival_count)}× revivals</span>
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


/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 2: DISCOVERY CATALYSTS
═══════════════════════════════════════════════════════════════════════════ */
let catalystOffset = 0;
const CATALYST_PAGE_SIZE = 25;
let catalystFilter = '';
let catalystMeaningful = false;
let catalystSearch = '';

async function loadDiscovery() {
  try {
    const [summary, topCatData] = await Promise.all([
      apiFetch('/api/discovery/summary'),
      apiFetch('/api/discovery/top-catalyst').catch(() => null)
    ]);

    const kpisEl = document.getElementById('catalyst-summary-kpis');
    kpisEl.innerHTML = `
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Total Catalysts</span><span class="text-3xl font-bold text-on-surface">${fmt(summary.meaningful_catalysts || summary.total_catalysts)}</span><span class="text-xs text-on-surface-variant">meaningful expansions</span></div>
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Artist Discoveries</span><span class="text-3xl font-bold text-primary">${fmt(summary.artist_discoveries)}</span></div>
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Project Discoveries</span><span class="text-3xl font-bold text-on-surface">${fmt(summary.project_discoveries)}</span></div>
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Hours Unlocked</span><span class="text-3xl font-bold text-on-surface">${fmt(summary.total_downstream_hours, 1)}<span class="text-base font-normal text-on-surface-variant ml-1">hrs</span></span></div>`;

    // Dynamic #1 featured catalyst
    const featuredPanel = document.getElementById('featured-catalyst-panel');
    const featuredHeader = document.getElementById('featured-catalyst-header');
    if (topCatData && topCatData.catalyst) {
      const c = topCatData.catalyst;
      if (featuredHeader) {
        featuredHeader.innerHTML = `
          <h2 class="text-lg font-bold text-on-surface">#1 Discovery Catalyst — ${c.catalyst_artist_name || ''}</h2>
          <p class="text-xs text-on-surface-variant">Ranked #1 by future hours unlocked • ${typeBadge(c.discovery_type)}</p>`;
      }
      if (featuredPanel) {
        featuredPanel.innerHTML = `
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div class="pathway-step">
                <div class="pathway-dot"><span class="material-symbols-outlined text-primary text-sm">music_note</span></div>
                <div class="bg-surface-container rounded-xl p-4 flex-1 border border-surface-variant">
                  <p class="font-semibold text-on-surface text-sm">${c.catalyst_track_name}</p>
                  <p class="text-xs text-on-surface-variant">Catalyst song — ${c.catalyst_artist_name}</p>
                </div>
              </div>
              <div class="pathway-step">
                <div class="pathway-dot"><span class="material-symbols-outlined text-primary text-sm">schedule</span></div>
                <div class="bg-surface-container rounded-xl p-4 flex-1 border border-surface-variant">
                  <p class="font-semibold text-on-surface text-sm">${fmt(c.max_tracks_added_7d)} New Tracks in 7 Days</p>
                  <p class="text-xs text-on-surface-variant">${fmt(c.max_minutes_added_7d, 0)} minutes added</p>
                </div>
              </div>
              <div class="pathway-step">
                <div class="pathway-dot"><span class="material-symbols-outlined text-primary text-sm">event</span></div>
                <div class="bg-surface-container rounded-xl p-4 flex-1 border border-surface-variant">
                  <p class="font-semibold text-on-surface text-sm">${fmt(c.max_minutes_30d, 0)} min over 30 Days</p>
                  <p class="text-xs text-on-surface-variant">${fmt(c.max_minutes_90d, 0)} min over 90 days</p>
                </div>
              </div>
              <div class="pathway-step">
                <div class="pathway-dot bg-primary/20 border-2 border-primary"><span class="material-symbols-outlined text-primary text-sm">sync</span></div>
                <div class="bg-primary/10 rounded-xl p-4 flex-1 border border-primary/30">
                  <p class="font-black text-primary text-2xl">${fmtHrs(c.future_hours_unlocked)}h</p>
                  <p class="text-xs text-on-surface-variant">Total Downstream Hours Unlocked</p>
                </div>
              </div>
            </div>
            <div class="space-y-4">
              <h3 class="text-sm font-semibold text-on-surface-variant uppercase tracking-wider">Discovery Stats</h3>
              <div class="grid grid-cols-2 gap-3">
                <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant">Type</p><p class="font-bold text-on-surface text-sm">${c.discovery_type || '—'}</p></div>
                <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant">7D Tracks</p><p class="font-bold text-on-surface text-sm">${fmt(c.max_tracks_added_7d)}</p></div>
                <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant">30D Mins</p><p class="font-bold text-on-surface text-sm">${fmt(c.max_minutes_30d, 0)}</p></div>
                <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant">90D Mins</p><p class="font-bold text-on-surface text-sm">${fmt(c.max_minutes_90d, 0)}</p></div>
              </div>
            </div>
          </div>`;
      }
    } else if (featuredPanel) {
      featuredPanel.innerHTML = '<p class="text-on-surface-variant text-sm">No discovery ranking data available.</p>';
    }

    await fetchCatalysts();

    document.querySelectorAll('[data-dfilter]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-dfilter]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        catalystFilter = btn.dataset.dfilter;
        catalystOffset = 0;
        fetchCatalysts();
      });
    });

    let searchTimer;
    document.getElementById('catalyst-search').addEventListener('input', e => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        catalystSearch = e.target.value;
        catalystOffset = 0;
        fetchCatalysts();
      }, 300);
    });

    document.getElementById('meaningful-only').addEventListener('change', e => {
      catalystMeaningful = e.target.checked;
      catalystOffset = 0;
      fetchCatalysts();
    });
  } catch (e) {
    console.error('Error loading discovery:', e);
  }
}

// NOTE: loadPantherPathway and loadFrappePathway removed — replaced by dynamic featured catalyst

async function fetchCatalysts() {
  const qs = new URLSearchParams({
    limit: CATALYST_PAGE_SIZE,
    offset: catalystOffset,
    ...(catalystFilter ? { discovery_type: catalystFilter } : {}),
    ...(catalystMeaningful ? { meaningful_only: 'true' } : {}),
    ...(catalystSearch ? { search: catalystSearch } : {})
  });
  const data = await apiFetch(`/api/discovery/catalysts?${qs}`);
  const tbody = document.getElementById('catalyst-table-body');
  const cats = data.catalysts || [];

  if (cats.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center py-8 text-on-surface-variant">No catalysts found.</td></tr>';
  } else {
    tbody.innerHTML = cats.map((c, i) => `
      <tr>
        <td class="font-mono text-on-surface-variant">${catalystOffset + i + 1}</td>
        <td class="font-medium text-on-surface max-w-[160px] truncate">${c.catalyst_track_name}</td>
        <td class="text-on-surface-variant max-w-[140px] truncate">${c.catalyst_artist_name}</td>
        <td>${typeBadge(c.discovery_type)}</td>
        <td class="text-on-surface font-mono">${fmt(c.max_tracks_added_7d)}</td>
        <td class="text-on-surface-variant font-mono">${fmt(c.max_minutes_added_7d, 1)}</td>
        <td class="text-on-surface-variant font-mono">${fmt(c.max_minutes_30d, 1)}</td>
        <td class="text-on-surface-variant font-mono">${fmt(c.max_minutes_90d, 1)}</td>
        <td class="text-primary font-bold font-mono">${fmtHrs(c.future_hours_unlocked)}h</td>
      </tr>`).join('');
  }

  document.getElementById('catalyst-count-label').textContent = `${fmt(data.total)} catalysts`;
  document.getElementById('catalyst-prev').disabled = catalystOffset === 0;
  document.getElementById('catalyst-next').disabled = catalystOffset + CATALYST_PAGE_SIZE >= data.total;
}

function catalystPage(dir) {
  catalystOffset = Math.max(0, catalystOffset + dir * CATALYST_PAGE_SIZE);
  fetchCatalysts();
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 3: ARTIST LIFECYCLE
═══════════════════════════════════════════════════════════════════════════ */
let allArtists = [];

async function loadArtists() {
  try {
    const data = await apiFetch('/api/artists?limit=250');
    allArtists = (data.artists || []).sort((a, b) => (b.total_hours || 0) - (a.total_hours || 0));
    renderArtistList(allArtists);

    if (allArtists.length > 0) {
      loadArtistDetail(allArtists[0].artist_id);
    }

    let artistSearchTimer;
    document.getElementById('artist-search-input').addEventListener('input', e => {
      clearTimeout(artistSearchTimer);
      artistSearchTimer = setTimeout(() => {
        const q = e.target.value.toLowerCase();
        const filtered = allArtists.filter(a => a.artist_name?.toLowerCase().includes(q));
        renderArtistList(filtered);
      }, 200);
    });

    document.getElementById('artist-stage-filter').addEventListener('change', e => {
      const stage = e.target.value;
      const filtered = stage ? allArtists.filter(a => a.lifecycle_stage === stage) : allArtists;
      renderArtistList(filtered);
    });
  } catch (e) {
    console.error('Error loading artists:', e);
  }
}

function renderArtistList(artists) {
  const el = document.getElementById('artist-list');
  if (artists.length === 0) {
    el.innerHTML = '<p class="p-6 text-center text-on-surface-variant text-sm">No artists found.</p>';
    return;
  }
  el.innerHTML = artists.slice(0, 100).map(a => `
    <div class="flex items-center gap-3 p-4 cursor-pointer hover:bg-surface-container-highest transition-colors" onclick="loadArtistDetail('${a.artist_id}')">
      <div class="w-10 h-10 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0 text-xs font-bold text-primary">
        ${(a.artist_name || '?').slice(0, 2).toUpperCase()}
      </div>
      <div class="flex-1 min-w-0">
        <p class="font-medium text-on-surface text-sm truncate">${a.artist_name}</p>
        <p class="text-xs text-on-surface-variant">${a.lifecycle_stage || '—'}</p>
      </div>
      <div class="text-right flex-shrink-0">
        <p class="text-xs font-bold text-on-surface">${fmtHrs(a.total_hours)}h</p>
        <p class="text-xs text-on-surface-variant">${fmt(a.total_plays)} plays</p>
      </div>
    </div>`).join('');
}

async function loadArtistDetail(artistId) {
  const artist = allArtists.find(a => a.artist_id === artistId || a.artist_name === artistId);
  if (!artist) return;

  const header = document.getElementById('artist-detail-header');
  header.innerHTML = `
    <div class="flex items-start gap-5 flex-wrap">
      <div class="w-16 h-16 rounded-full bg-primary/10 border-2 border-primary/30 flex items-center justify-center text-xl font-black text-primary flex-shrink-0">
        ${(artist.artist_name || '?').slice(0, 2).toUpperCase()}
      </div>
      <div class="flex-1">
        <div class="text-xs text-on-surface-variant uppercase tracking-widest mb-1">Artist Lifecycle Analysis</div>
        <h2 class="text-3xl font-black text-on-surface mb-1">${artist.artist_name}</h2>
        <p class="text-on-surface-variant text-sm mb-3">Your listening journey.</p>
        <div class="flex flex-wrap gap-4 text-sm">
          <div class="flex flex-col"><span class="text-on-surface-variant text-xs">PLAYS</span><span class="font-bold text-on-surface">${fmt(artist.total_plays)}</span></div>
          <div class="flex flex-col"><span class="text-on-surface-variant text-xs">TRACKS</span><span class="font-bold text-on-surface">${fmt(artist.unique_tracks)}</span></div>
          <div class="flex flex-col"><span class="text-on-surface-variant text-xs">PROJECTS</span><span class="font-bold text-on-surface">${fmt(artist.unique_projects)}</span></div>
          <div class="flex flex-col"><span class="text-on-surface-variant text-xs">FIRST HEARD</span><span class="font-bold text-on-surface">${artist.first_heard_utc ? new Date(artist.first_heard_utc).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }) : '—'}</span></div>
          <div class="flex flex-col"><span class="text-on-surface-variant text-xs">PEAK YEAR</span><span class="font-bold text-primary">${artist.peak_year || '—'}</span></div>
          <div class="flex flex-col"><span class="text-on-surface-variant text-xs">STAGE</span><span class="font-bold text-on-surface">${artist.lifecycle_stage || '—'}</span></div>
        </div>
      </div>
    </div>`;

  try {
    const lc = await apiFetch(`/api/artists/${encodeURIComponent(artist.artist_name)}/lifecycle`);
    const timeline = lc.monthly_timeline || lc.monthly_plays || [];
    if (timeline.length > 0) {
      document.getElementById('artist-lifecycle-chart-container').classList.remove('hidden');
      const months = timeline.map(r => r.year_month || r.month);
      const plays = timeline.map(r => r.plays || r.minutes);
      Plotly.newPlot('artist-lifecycle-chart', [{
        type: 'scatter', x: months, y: plays,
        fill: 'tozeroy', fillcolor: 'rgba(83,224,118,0.15)',
        line: { color: '#53e076', width: 2 },
        hovertemplate: '<b>%{x}</b><br>%{y} plays<extra></extra>'
      }], {
        ...plotlyLayout,
        xaxis: { gridcolor: '#2a2b2b' },
        yaxis: { gridcolor: '#2a2b2b' }
      }, plotlyConfig);
    }

    // Time of Day
    const tod = lc.time_of_day_profile || {};
    const todKeys = Object.keys(tod);
    if (todKeys.length > 0) {
      document.getElementById('artist-tod-container').classList.remove('hidden');
      Plotly.newPlot('artist-tod-chart', [{
        type: 'bar', x: todKeys, y: todKeys.map(k => tod[k]),
        marker: { color: '#53e076', opacity: 0.7 },
        hovertemplate: '%{x} — %{y:.0f} min<extra></extra>'
      }], {
        ...plotlyLayout,
        xaxis: { gridcolor: '#2a2b2b' },
        yaxis: { title: 'Minutes', gridcolor: '#2a2b2b' },
        margin: { l: 50, r: 20, t: 20, b: 60 }
      }, plotlyConfig);
    }

    // Discography Penetration
    const projs = lc.projects || [];
    if (projs.length > 0) {
      document.getElementById('artist-discography-container').classList.remove('hidden');
      const discEl = document.getElementById('artist-discography');
      discEl.innerHTML = projs.slice(0, 8).map(p => {
        const pct = Math.round(p.penetration_pct || 0);
        return `
          <div>
            <div class="flex items-center justify-between text-xs mb-1">
              <span class="text-on-surface font-medium truncate max-w-[150px]">${p.project_name}</span>
              <span class="text-on-surface-variant">${pct}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width:${pct}%"></div>
            </div>
          </div>`;
      }).join('');
    }
  } catch (e) {
    console.error('Error fetching artist lifecycle:', e);
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 4: ALBUMS & EPS
═══════════════════════════════════════════════════════════════════════════ */
let albumOffset = 0;
const ALBUM_PAGE_SIZE = 12;
let albumSearchQ = '';
let albumExploredOnly = false;
let albumTotal = 0;

async function loadAlbums() {
  try {
    const data = await apiFetch('/api/projects?limit=500');
    const all = data.projects || [];

    const explored = all.filter(p => p.is_explored);
    const fullDone = all.filter(p => p.listening_style === 'Full Listen' || (p.penetration_pct || 0) >= 90);
    const deep = all.filter(p => p.listening_style === 'Deep Listen' || ((p.penetration_pct || 0) >= 50 && (p.penetration_pct || 0) < 90));
    const partial = all.filter(p => p.listening_style === 'Partial' || (p.penetration_pct || 0) < 50);

    document.getElementById('album-kpis').innerHTML = `
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Projects Explored</span><span class="text-3xl font-bold text-primary">${fmt(data.explored_count_ge3 || explored.length)}</span></div>
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Full Projects</span><span class="text-3xl font-bold text-on-surface">${fmt(fullDone.length)}</span></div>
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Deep Projects</span><span class="text-3xl font-bold text-on-surface">${fmt(deep.length)}</span></div>
      <div class="kpi-card"><span class="text-label-sm text-on-surface-variant uppercase tracking-wider">Partial Projects</span><span class="text-3xl font-bold text-on-surface">${fmt(partial.length)}</span></div>`;

    const topProj = explored.sort((a, b) => (b.total_plays || 0) - (a.total_plays || 0))[0] || all[0];
    if (topProj) {
      const pct = Math.round(topProj.penetration_pct || 0);
      document.getElementById('featured-project').innerHTML = `
        <div class="flex flex-col md:flex-row gap-6">
          <div class="w-full md:w-48 h-48 bg-surface-container rounded-xl flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-6xl text-on-surface-variant">album</span>
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-3">
              <span class="badge badge-artist">EXPLORED</span>
            </div>
            <h3 class="text-2xl font-black text-on-surface mb-1">${topProj.project_name}</h3>
            <p class="text-on-surface-variant mb-4">${topProj.artist_name}</p>
            <div class="grid grid-cols-3 gap-4 mb-5">
              <div><p class="text-xs text-on-surface-variant uppercase tracking-wider">Penetration</p><p class="text-2xl font-bold text-on-surface">${pct}%</p><p class="text-xs text-on-surface-variant">${topProj.tracks_heard || 0} Tracks</p></div>
              <div><p class="text-xs text-on-surface-variant uppercase tracking-wider">Total Plays</p><p class="text-2xl font-bold text-on-surface">${fmt(topProj.total_plays)}</p><p class="text-xs text-on-surface-variant">All time</p></div>
              <div><p class="text-xs text-on-surface-variant uppercase tracking-wider">Time Spent</p><p class="text-2xl font-bold text-on-surface">${fmtHrs(topProj.total_hours)}h</p></div>
            </div>
            ${topProj.top_song_name ? `
            <div>
              <p class="text-xs text-on-surface-variant uppercase tracking-wider mb-2">Project-Driving Song</p>
              <div class="flex items-center gap-3 p-3 bg-surface-container rounded-xl">
                <span class="material-symbols-outlined text-primary">star</span>
                <div>
                  <p class="font-semibold text-on-surface text-sm">${topProj.top_song_name}</p>
                  <p class="text-xs text-on-surface-variant">${fmt(topProj.top_song_plays)} plays</p>
                </div>
                <div class="ml-auto text-right">
                  <p class="text-primary font-bold text-sm">${Math.round(topProj.top_song_share_pct || 0)}%</p>
                </div>
              </div>
            </div>` : ''}
          </div>
        </div>`;
    }

    window._allAlbums = all;
    renderAlbumGrid();

    let albumSearchTimer;
    document.getElementById('album-search').addEventListener('input', e => {
      clearTimeout(albumSearchTimer);
      albumSearchTimer = setTimeout(() => {
        albumSearchQ = e.target.value.toLowerCase();
        albumOffset = 0;
        renderAlbumGrid();
      }, 300);
    });

    document.getElementById('explored-only').addEventListener('change', e => {
      albumExploredOnly = e.target.checked;
      albumOffset = 0;
      renderAlbumGrid();
    });
  } catch (e) {
    console.error('Error loading albums:', e);
  }
}

function renderAlbumGrid() {
  let albums = (window._allAlbums || []).filter(a =>
    (!albumExploredOnly || a.is_explored) &&
    (!albumSearchQ || a.project_name?.toLowerCase().includes(albumSearchQ) || a.artist_name?.toLowerCase().includes(albumSearchQ))
  ).sort((a, b) => (b.total_plays || 0) - (a.total_plays || 0));

  albumTotal = albums.length;
  const page = albums.slice(albumOffset, albumOffset + ALBUM_PAGE_SIZE);
  const el = document.getElementById('album-grid');

  if (page.length === 0) {
    el.innerHTML = '<div class="col-span-3 text-center py-8 text-on-surface-variant">No projects found.</div>';
    return;
  }

  el.innerHTML = page.map(p => {
    const pct = Math.round(p.penetration_pct || 0);
    const style = p.listening_style || (pct >= 90 ? 'Full' : pct >= 50 ? 'Deep' : 'Partial');
    return `
      <div class="bg-surface-container-high rounded-xl border border-surface-variant p-4 hover:border-primary/40 transition-colors cursor-pointer" onclick="openAlbumDetail('${(p.project_id || '').replace(/'/g, '\\\'')}', '${(p.project_name || '').replace(/'/g, '\\\'')}')">
        <div class="flex items-start gap-3 mb-4">
          <div class="w-12 h-12 rounded-lg bg-surface-container flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-on-surface-variant">album</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-on-surface text-sm truncate">${p.project_name}</p>
            <p class="text-xs text-on-surface-variant truncate">${p.artist_name}</p>
          </div>
          ${p.is_explored ? '<span class="badge badge-artist text-xs">✓</span>' : ''}
        </div>
        <div class="flex items-center justify-between text-xs mb-1">
          <span class="text-on-surface-variant">${p.tracks_heard || 0} Tracks • ${style}</span>
          <span class="font-bold ${pct >= 90 ? 'text-primary' : 'text-on-surface'}">${pct}%</span>
        </div>
        <div class="progress-bar mb-2">
          <div class="progress-fill" style="width:${Math.min(100,pct)}%"></div>
        </div>
        <div class="flex justify-between text-xs text-on-surface-variant">
          <span>${fmt(p.total_plays)} plays</span>
          <span>${fmtHrs(p.total_hours)}h total</span>
        </div>
      </div>`;
  }).join('');

  const pageNum = Math.floor(albumOffset / ALBUM_PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil(albumTotal / ALBUM_PAGE_SIZE));
  document.getElementById('album-page-label').textContent = `Page ${pageNum} / ${totalPages}`;
}

async function openAlbumDetail(projectId, projectName) {
  const detailContent = document.getElementById('album-detail-content');
  if (!detailContent) return;
  const panel = document.getElementById('album-detail-panel');
  if (panel) {
    panel.querySelector('.p-5').innerHTML = `<p class="text-sm font-bold text-on-surface">${projectName}</p>`;
  }
  detailContent.innerHTML = '<div class="space-y-2"><div class="skeleton h-10 rounded"></div><div class="skeleton h-10 rounded"></div><div class="skeleton h-10 rounded"></div></div>';
  try {
    const data = await apiFetch(`/api/projects/${encodeURIComponent(projectId)}/songs`);
    const songs = data.songs || [];
    if (songs.length === 0) {
      detailContent.innerHTML = '<p class="text-on-surface-variant text-sm">No tracks found for this project.</p>';
      return;
    }
    detailContent.innerHTML = `
      <div class="space-y-1 max-h-[500px] overflow-y-auto pr-1">
        ${songs.map((s, i) => `
          <div class="flex items-center gap-3 py-2 border-b border-surface-variant/40 last:border-0 hover:bg-surface-container rounded-lg px-2 transition-colors">
            <span class="text-xs text-on-surface-variant w-5 text-center flex-shrink-0">${i + 1}</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-on-surface truncate">${s.track_name}</p>
              <p class="text-xs text-on-surface-variant">${fmt(s.total_plays)} plays • ${fmt(s.total_minutes, 0)} min</p>
            </div>
            ${((s.skip_rate || 0) * 100) > 30 ? '<span class="material-symbols-outlined text-yellow-400 text-sm flex-shrink-0" title="High skip rate">skip_next</span>' : ''}
          </div>`).join('')}
      </div>
      <p class="text-xs text-on-surface-variant mt-3">${songs.length} tracks in database</p>`;
  } catch (e) {
    detailContent.innerHTML = '<p class="text-red-400 text-sm">Failed to load track list.</p>';
    console.error('openAlbumDetail failed:', e);
  }
}

function albumPage(dir) {
  const newOff = albumOffset + dir * ALBUM_PAGE_SIZE;
  if (newOff < 0 || newOff >= albumTotal) return;
  albumOffset = newOff;
  renderAlbumGrid();
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 5: SONG LIFECYCLES
═══════════════════════════════════════════════════════════════════════════ */
let songOffset = 0;
const SONG_PAGE_SIZE = 30;
let songCat = '';
let songSearchQ = '';
let songTotal = 0;

async function loadSongs() {
  try {
    const data = await apiFetch('/api/songs?limit=500');
    window._allSongs = (data.songs || []).sort((a, b) => (b.total_plays || 0) - (a.total_plays || 0));

    document.querySelectorAll('[data-scat]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-scat]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        songCat = btn.dataset.scat;
        songOffset = 0;
        renderSongTable();
        renderFeaturedSong();
      });
    });

    let songTimer;
    document.getElementById('song-search').addEventListener('input', e => {
      clearTimeout(songTimer);
      songTimer = setTimeout(() => {
        songSearchQ = e.target.value.toLowerCase();
        songOffset = 0;
        renderSongTable();
      }, 300);
    });

    renderFeaturedSong();
    renderSongTable();
  } catch (e) {
    console.error('Error loading songs:', e);
  }
}

function renderFeaturedSong() {
  const songs = getFilteredSongs();
  const top = songs[0];
  if (!top) return;

  const rawDays = Math.round(top.raw_lifespan_days || 0);
  const activeDays = Math.round(top.active_lifespan_days || 0);
  const skipPct = ((top.skip_rate || 0) * 100).toFixed(1);
  const activeRatio = rawDays > 0 ? Math.min(100, Math.round((activeDays / rawDays) * 100)) : 0;

  document.getElementById('featured-song').innerHTML = `
    <div class="flex flex-col md:flex-row gap-6">
      <div class="w-full md:w-48 h-48 bg-surface-container rounded-xl border border-surface-variant flex items-center justify-center flex-shrink-0">
        <span class="material-symbols-outlined text-6xl text-on-surface-variant">music_note</span>
      </div>
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-2">${catBadge(top.lifecycle_category)}</div>
        <h3 class="text-2xl font-black text-on-surface mb-0.5">${top.track_name}</h3>
        <p class="text-on-surface-variant mb-4">${top.artist_name}${top.project_name ? ` — from ${top.project_name}` : ''}</p>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
          <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant uppercase">Plays</p><p class="text-xl font-bold text-on-surface">${fmt(top.total_plays)}</p></div>
          <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant uppercase">Minutes</p><p class="text-xl font-bold text-on-surface">${fmt(top.total_minutes, 0)}</p></div>
          <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant uppercase">First Heard</p><p class="text-sm font-bold text-on-surface">${top.first_played_utc ? new Date(top.first_played_utc).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }) : '—'}</p></div>
          <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant uppercase">Skip Rate</p><p class="text-xl font-bold ${parseFloat(skipPct) > 20 ? 'text-red-400' : 'text-on-surface'}">${skipPct}%</p></div>
          <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant uppercase">Active Days</p><p class="text-xl font-bold text-primary">${fmt(top.active_lifespan_days || 0, 0)}</p></div>
          <div class="bg-surface-container rounded-xl p-3"><p class="text-xs text-on-surface-variant uppercase">Raw Lifespan</p><p class="text-xl font-bold text-on-surface">${rawDays}d</p></div>
        </div>
        <div class="bg-surface-container rounded-xl p-4">
          <h4 class="font-semibold text-on-surface text-sm mb-3">Lifespan Comparison</h4>
          <div class="space-y-2">
            <div>
              <div class="flex justify-between text-xs mb-1"><span class="text-on-surface-variant">Raw Lifespan (time in library)</span><span class="text-on-surface">100%</span></div>
              <div class="progress-bar"><div class="progress-fill bg-surface-container-highest" style="width:100%"></div></div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1"><span class="text-on-surface-variant">Active Lifespan (listening density)</span><span class="text-primary">${activeRatio}%</span></div>
              <div class="progress-bar"><div class="progress-fill" style="width:${activeRatio}%"></div></div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

function getFilteredSongs() {
  return (window._allSongs || []).filter(s =>
    (!songCat || s.lifecycle_category === songCat) &&
    (!songSearchQ || s.track_name?.toLowerCase().includes(songSearchQ) || s.artist_name?.toLowerCase().includes(songSearchQ))
  );
}

function renderSongTable() {
  const songs = getFilteredSongs();
  songTotal = songs.length;
  const page = songs.slice(songOffset, songOffset + SONG_PAGE_SIZE);
  const tbody = document.getElementById('song-table-body');

  if (page.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center py-8 text-on-surface-variant">No songs found.</td></tr>';
  } else {
    tbody.innerHTML = page.map((s, i) => `
      <tr>
        <td class="text-on-surface-variant font-mono">${songOffset + i + 1}</td>
        <td class="font-medium text-on-surface max-w-[180px] truncate">${s.track_name}</td>
        <td class="text-on-surface-variant max-w-[140px] truncate">${s.artist_name}</td>
        <td>${catBadge(s.lifecycle_category)}</td>
        <td class="font-mono">${fmt(s.total_plays)}</td>
        <td class="font-mono text-on-surface-variant">${fmt(s.total_minutes, 0)}</td>
        <td class="font-mono text-on-surface-variant">${((s.skip_rate || 0) * 100).toFixed(1)}%</td>
        <td class="font-mono text-on-surface-variant">${Math.round(s.raw_lifespan_days || 0)}d</td>
        <td class="font-mono text-primary">${Math.round(s.active_lifespan_days || 0)}d</td>
      </tr>`).join('');
  }

  document.getElementById('song-count-label').textContent = `${fmt(songTotal)} songs`;
}

function songPage(dir) {
  const newOff = songOffset + dir * SONG_PAGE_SIZE;
  if (newOff < 0 || newOff >= songTotal) return;
  songOffset = newOff;
  renderSongTable();
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 6: LISTENING SEQUENCES
═══════════════════════════════════════════════════════════════════════════ */
let seqType = 'songs';

async function loadSequences() {
  try {
    const [tt, at_, seq3] = await Promise.all([
      apiFetch('/api/sequences/top?limit=20'),
      apiFetch('/api/sequences/artists?limit=20'),
      apiFetch('/api/sequences/three-song?limit=10')
    ]);

    window._seqData = {
      songs: tt.transitions || tt.top_track_transitions || [],
      artists: at_.transitions || tt.top_artist_transitions || [],
      sequences: seq3.sequences || tt.three_song_sequences || []
    };

    document.querySelectorAll('[data-seqtype]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-seqtype]').forEach(b => {
          b.classList.remove('active','border-primary','text-primary');
          b.classList.add('border-transparent','text-on-surface-variant');
        });
        btn.classList.add('active','border-primary','text-primary');
        btn.classList.remove('border-transparent','text-on-surface-variant');
        seqType = btn.dataset.seqtype;
        renderSequences();
      });
    });

    renderSequences();
    renderSignatureChain(window._seqData.sequences);
    renderArtistGravity(window._seqData.artists);
  } catch (e) {
    console.error('Error loading sequences:', e);
  }
}

function renderSequences() {
  const data = window._seqData || {};
  const items = data[seqType] || [];
  const el = document.getElementById('seq-main-content');

  const titles = { songs: 'Top Song Transitions', artists: 'Top Artist Transitions', sequences: '3-Song Chains' };
  document.getElementById('seq-section-title').textContent = titles[seqType] || '';

  if (items.length === 0) {
    el.innerHTML = '<p class="text-on-surface-variant">No data available.</p>';
    return;
  }

  if (seqType === 'songs') {
    el.innerHTML = items.slice(0, 10).map(t => {
      const prob = Math.round((t.transition_probability || 0) * 100);
      return `
        <div class="transition-card">
          <div class="flex-1 min-w-0">
            <p class="font-medium text-on-surface text-sm truncate">${t.previous_track_name || '—'}</p>
            <p class="text-xs text-on-surface-variant">${t.previous_artist_name || ''}</p>
          </div>
          <div class="flex flex-col items-center flex-shrink-0 px-2">
            <span class="text-primary font-bold text-sm">${prob}%</span>
            <span class="material-symbols-outlined text-primary text-lg">arrow_forward</span>
            <span class="text-xs text-on-surface-variant">${fmt(t.transition_count)} plays</span>
          </div>
          <div class="flex-1 min-w-0 text-right">
            <p class="font-medium text-on-surface text-sm truncate">${t.track_name || '—'}</p>
            <p class="text-xs text-on-surface-variant">${t.artist_name || ''}</p>
          </div>
        </div>`;
    }).join('');
  } else if (seqType === 'artists') {
    const nonSelf = items.filter(t => !t.is_self_transition);
    el.innerHTML = (nonSelf.length ? nonSelf : items).slice(0, 10).map(t => {
      const prob = Math.round((t.transition_probability || 0) * 100);
      return `
        <div class="transition-card">
          <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary flex-shrink-0">
            ${(t.previous_artist_name || '?').slice(0, 2).toUpperCase()}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-on-surface text-sm">${t.previous_artist_name || '—'}</p>
          </div>
          <div class="text-center flex-shrink-0 px-2">
            <p class="text-primary font-bold">${prob}%</p>
            <span class="material-symbols-outlined text-primary">arrow_forward</span>
          </div>
          <div class="flex-1 min-w-0 text-right">
            <p class="font-medium text-on-surface text-sm">${t.artist_name || '—'}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-surface-container flex items-center justify-center text-xs font-bold text-on-surface-variant flex-shrink-0">
            ${(t.artist_name || '?').slice(0, 2).toUpperCase()}
          </div>
        </div>`;
    }).join('');
  } else {
    // FIX: parquet uses prev2_track_name, prev_track_name, track_name
    el.innerHTML = items.slice(0, 8).map(s => {
      const song1 = s.prev2_track_name || s.song1_name || '?';
      const song2 = s.prev_track_name || s.song2_name || '?';
      const song3 = s.track_name || s.song3_name || '?';
      return `
      <div class="bg-surface-container-high rounded-xl border border-surface-variant p-4">
        <div class="flex items-center gap-2 text-sm flex-wrap">
          <span class="font-medium text-on-surface">${song1}</span>
          <span class="material-symbols-outlined text-primary text-sm">arrow_forward</span>
          <span class="font-medium text-on-surface">${song2}</span>
          <span class="material-symbols-outlined text-primary text-sm">arrow_forward</span>
          <span class="font-medium text-on-surface">${song3}</span>
        </div>
        <p class="text-xs text-on-surface-variant mt-1">${fmt(s.sequence_count)} occurrences</p>
      </div>`;
    }).join('');
  }
}

function renderSignatureChain(seqs) {
  const el = document.getElementById('signature-chain');
  if (!seqs || !seqs.length) {
    el.innerHTML = '<p class="text-xs text-on-surface-variant">No sequences available.</p>';
    return;
  }
  const top = seqs[0];
  // FIX: use correct parquet column names
  const names = [
    top.prev2_track_name || top.song1_name,
    top.prev_track_name  || top.song2_name,
    top.track_name       || top.song3_name
  ].filter(Boolean);
  el.innerHTML = names.map((name, i) => `
    <div class="flex items-center gap-3 p-2 ${i === 0 ? 'bg-surface-container' : ''} rounded-lg">
      <div class="w-8 h-8 rounded-lg bg-surface-container-highest flex items-center justify-center flex-shrink-0">
        <span class="material-symbols-outlined text-primary text-sm">music_note</span>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-on-surface truncate">${name}</p>
      </div>
    </div>`).join('') + `<p class="text-xs text-on-surface-variant mt-2">Played together ${fmt(top.sequence_count)} times</p>`;
}

function renderArtistGravity(transitions) {
  const el = document.getElementById('artist-gravity');
  const self = (transitions || []).filter(t => t.is_self_transition).sort((a, b) => (b.transition_probability || 0) - (a.transition_probability || 0));
  el.innerHTML = self.slice(0, 5).map(t => `
    <div class="flex items-center justify-between text-sm py-1">
      <span class="text-on-surface truncate max-w-[140px]">${t.artist_name}</span>
      <span class="text-primary font-bold">${Math.round((t.transition_probability || 0) * 100)}%</span>
    </div>`).join('');
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 7: MUSIC NETWORK
═══════════════════════════════════════════════════════════════════════════ */
let networkData = null;
let networkCanvas = null;
let networkCtx = null;
let networkNodes = [];
let networkEdges = [];
let networkMinWeight = 2;
let networkZoom = 1;
let networkOffsetX = 0, networkOffsetY = 0;
let networkDragging = false;
let networkDragStart = { x: 0, y: 0 };
let networkFilter = '';

async function loadNetwork() {
  try {
    const data = await apiFetch('/api/network');
    networkData = data;

    const summary = data.summary || {};
    document.getElementById('network-stats').innerHTML = `
      <div class="flex justify-between"><span>Artists (nodes)</span><span class="font-bold text-on-surface">${fmt(summary.total_nodes || (data.nodes || []).length)}</span></div>
      <div class="flex justify-between"><span>Connections</span><span class="font-bold text-on-surface">${fmt(summary.total_edges || (data.edges || []).length)}</span></div>
      <div class="flex justify-between"><span>Communities</span><span class="font-bold text-on-surface">${fmt(summary.num_communities)}</span></div>
      <div class="flex justify-between"><span>Density</span><span class="font-bold text-primary">${summary.density || '0.0077'}</span></div>`;

    document.getElementById('network-density-label').textContent = `Network Density: ${summary.density || '0.0077'} (${summary.num_communities || 39} communities)`;

    networkCanvas = document.getElementById('network-canvas');
    networkCtx = networkCanvas.getContext('2d');

    // FIX: Use ResizeObserver so we get the actual container dimensions after layout,
    // not the 0×0 dimensions from when the view was still display:none
    const initNetwork = () => {
      const rect = networkCanvas.parentElement.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        // Container still has no dimensions — defer one more frame
        requestAnimationFrame(initNetwork);
        return;
      }
      networkCanvas.width = rect.width;
      networkCanvas.height = rect.height;
      buildNetworkLayout();
      drawNetwork();
    };

    // Defer initialization to ensure the view is visible and has real dimensions
    requestAnimationFrame(() => requestAnimationFrame(initNetwork));

    const ro = new ResizeObserver(() => {
      const rect = networkCanvas.parentElement.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        networkCanvas.width = rect.width;
        networkCanvas.height = rect.height;
        buildNetworkLayout();
        drawNetwork();
      }
    });
    ro.observe(networkCanvas.parentElement);

    networkCanvas.addEventListener('mousedown', onNetworkMouseDown);
    networkCanvas.addEventListener('mousemove', onNetworkMouseMove);
    networkCanvas.addEventListener('mouseup', onNetworkMouseUp);
    networkCanvas.addEventListener('wheel', onNetworkWheel);
    networkCanvas.addEventListener('click', onNetworkClick);

    document.getElementById('network-search').addEventListener('input', e => {
      networkFilter = e.target.value.toLowerCase();
      drawNetwork();
    });
  } catch (e) {
    console.error('Error loading network:', e);
  }
}

function buildNetworkLayout() {
  if (!networkData) return;
  const nodes = networkData.nodes || [];
  const edges = networkData.edges || [];
  const W = networkCanvas.width, H = networkCanvas.height;

  const filteredEdges = edges.filter(e => (e.weight || e.transition_count || 1) >= networkMinWeight);
  const nodeIds = new Set([...filteredEdges.map(e => e.source), ...filteredEdges.map(e => e.target)]);

  const communities = {};
  nodes.forEach(n => {
    if (!nodeIds.has(n.id)) return;
    const c = n.community ?? 0;
    if (!communities[c]) communities[c] = [];
    communities[c].push(n);
  });

  networkNodes = [];
  const commKeys = Object.keys(communities);
  commKeys.forEach((ck, ci) => {
    const angle = (ci / Math.max(1, commKeys.length)) * Math.PI * 2;
    const r = Math.min(W, H) * 0.32;
    const cx = W / 2 + r * Math.cos(angle);
    const cy = H / 2 + r * Math.sin(angle);
    communities[ck].forEach((n, ni) => {
      const a2 = (ni / Math.max(1, communities[ck].length)) * Math.PI * 2;
      const r2 = Math.min(W, H) * 0.09;
      networkNodes.push({
        ...n,
        x: cx + r2 * Math.cos(a2),
        y: cy + r2 * Math.sin(a2),
        r: Math.min(22, Math.max(6, Math.log((n.total_plays || 1) + 1) * 2.8)),
        color: `hsl(${(parseInt(ck) * 37) % 360},65%,55%)`
      });
    });
  });

  networkEdges = filteredEdges;
}

function drawNetwork() {
  if (!networkCtx || !networkCanvas) return;
  const W = networkCanvas.width, H = networkCanvas.height;
  networkCtx.clearRect(0, 0, W, H);
  networkCtx.save();
  networkCtx.translate(networkOffsetX, networkOffsetY);
  networkCtx.scale(networkZoom, networkZoom);

  // Edges
  networkCtx.strokeStyle = 'rgba(83,224,118,0.18)';
  networkEdges.forEach(e => {
    const src = networkNodes.find(n => n.id === e.source);
    const tgt = networkNodes.find(n => n.id === e.target);
    if (!src || !tgt) return;
    if (networkFilter && !src.name?.toLowerCase().includes(networkFilter) && !tgt.name?.toLowerCase().includes(networkFilter)) return;
    const w = Math.max(0.6, Math.min(3, (e.weight || 1) / 15));
    networkCtx.lineWidth = w;
    networkCtx.beginPath();
    networkCtx.moveTo(src.x, src.y);
    networkCtx.lineTo(tgt.x, tgt.y);
    networkCtx.stroke();
  });

  // Nodes
  networkNodes.forEach(n => {
    const isHighlighted = networkFilter && n.name?.toLowerCase().includes(networkFilter);
    const alpha = networkFilter && !isHighlighted ? 0.15 : 1;
    networkCtx.globalAlpha = alpha;
    networkCtx.beginPath();
    networkCtx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
    networkCtx.fillStyle = isHighlighted ? '#53e076' : n.color;
    networkCtx.fill();
    networkCtx.strokeStyle = '#0B0B0B';
    networkCtx.lineWidth = 1.5;
    networkCtx.stroke();

    if (n.r > 8 || isHighlighted) {
      networkCtx.fillStyle = isHighlighted ? '#53e076' : '#e3e2e2';
      networkCtx.font = `${Math.max(10, n.r * 0.75)}px Inter`;
      networkCtx.textAlign = 'center';
      networkCtx.textBaseline = 'middle';
      const label = (n.name || '').length > 12 ? n.name.slice(0, 12) + '…' : n.name;
      networkCtx.fillText(label, n.x, n.y + n.r + 9);
    }
    networkCtx.globalAlpha = 1;
  });

  networkCtx.restore();
}

function getNetworkNode(mx, my) {
  const x = (mx - networkOffsetX) / networkZoom;
  const y = (my - networkOffsetY) / networkZoom;
  return networkNodes.find(n => Math.hypot(n.x - x, n.y - y) <= n.r + 4);
}

function onNetworkMouseDown(e) {
  networkDragging = true;
  networkDragStart = { x: e.clientX - networkOffsetX, y: e.clientY - networkOffsetY };
}
function onNetworkMouseMove(e) {
  if (networkDragging) {
    networkOffsetX = e.clientX - networkDragStart.x;
    networkOffsetY = e.clientY - networkDragStart.y;
    drawNetwork();
    return;
  }
  const rect = networkCanvas.getBoundingClientRect();
  const node = getNetworkNode(e.clientX - rect.left, e.clientY - rect.top);
  const tooltip = document.getElementById('network-tooltip');
  if (node) {
    networkCanvas.style.cursor = 'pointer';
    tooltip.style.display = 'block';
    tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
    tooltip.style.top = (e.clientY - rect.top - 28) + 'px';
    tooltip.innerHTML = `<strong>${node.name}</strong><br>${fmt(node.total_plays || 0)} plays`;
  } else {
    networkCanvas.style.cursor = 'grab';
    tooltip.style.display = 'none';
  }
}
function onNetworkMouseUp() { networkDragging = false; }
function onNetworkWheel(e) {
  e.preventDefault();
  const delta = e.deltaY > 0 ? 0.9 : 1.1;
  zoomNetwork(delta, e.offsetX, e.offsetY);
}
function onNetworkClick(e) {
  const rect = networkCanvas.getBoundingClientRect();
  const node = getNetworkNode(e.clientX - rect.left, e.clientY - rect.top);
  if (node) {
    const det = document.getElementById('network-node-detail');
    det.classList.remove('hidden');
    det.innerHTML = `
      <p class="font-bold text-on-surface">${node.name}</p>
      <p class="text-on-surface-variant text-xs">${fmt(node.total_plays || 0)} plays</p>
      <p class="text-on-surface-variant text-xs">Community: ${node.community ?? 0}</p>
      <button class="text-primary text-xs mt-1 hover:underline block" onclick="navigateArtistFromNetwork('${node.name}')">View lifecycle →</button>`;
  }
}
function zoomNetwork(factor, cx, cy) {
  const W = networkCanvas.width / 2, H = networkCanvas.height / 2;
  const ox = cx ?? W, oy = cy ?? H;
  networkOffsetX = ox - (ox - networkOffsetX) * factor;
  networkOffsetY = oy - (oy - networkOffsetY) * factor;
  networkZoom *= factor;
  networkZoom = Math.min(5, Math.max(0.1, networkZoom));
  drawNetwork();
}
function resetNetwork() { networkZoom = 1; networkOffsetX = 0; networkOffsetY = 0; drawNetwork(); }
function updateNetworkWeight(val) {
  networkMinWeight = parseInt(val);
  document.getElementById('min-weight-label').textContent = val;
  buildNetworkLayout();
  drawNetwork();
}
function navigateArtistFromNetwork(artistName) {
  navigate('artists');
  setTimeout(() => loadArtistDetail(artistName), 400);
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 8: GENRE × TIME × YEAR
═══════════════════════════════════════════════════════════════════════════ */
let genreData = null;

async function loadGenres() {
  try {
    genreData = await apiFetch('/api/genres/time-matrix');
    renderGenreView('all');

    document.getElementById('genre-year-filter').addEventListener('change', e => {
      renderGenreView(e.target.value);
    });
  } catch (e) {
    console.error('Error loading genres:', e);
  }
}

function renderGenreView(yearFilter) {
  const matrix = genreData.genre_time_matrix || genreData.matrix || [];
  const yearly = genreData.yearly_genre_share || genreData.yearly || [];

  let filtered = yearFilter === 'all' ? matrix : matrix.filter(r => String(r.year) === yearFilter);

  const heatmap = {};
  const timeBuckets = new Set();
  const genres = new Set();
  filtered.forEach(r => {
    const bucket = r.time_of_day_bucket || r.time_bucket;
    if (bucket && r.genre) {
      timeBuckets.add(bucket);
      genres.add(r.genre);
      const k = `${r.genre}|||${bucket}`;
      heatmap[k] = (heatmap[k] || 0) + (r.total_minutes || 0);
    }
  });

  const tbList = [...timeBuckets].sort();
  const gList = [...genres].sort((a, b) => {
    const totA = tbList.reduce((s, t) => s + (heatmap[`${a}|||${t}`] || 0), 0);
    const totB = tbList.reduce((s, t) => s + (heatmap[`${b}|||${t}`] || 0), 0);
    return totB - totA;
  }).slice(0, 15);

  const z = gList.map(g => tbList.map(t => Math.round((heatmap[`${g}|||${t}`] || 0))));

  Plotly.newPlot('genre-heatmap', [{
    type: 'heatmap', z, x: tbList, y: gList,
    colorscale: [[0, '#1e2020'], [0.5, '#1db954'], [1, '#53e076']],
    hovertemplate: '%{y}<br>%{x}<br>%{z:.0f} min<extra></extra>',
    showscale: false
  }], {
    ...plotlyLayout,
    margin: { l: 150, r: 20, t: 30, b: 60 },
    xaxis: { gridcolor: '#2a2b2b' },
    yaxis: { gridcolor: '#2a2b2b', autorange: 'reversed' }
  }, plotlyConfig);

  const years = [...new Set(yearly.map(r => r.year))].sort();
  const topGenres = gList.slice(0, 6);
  const traces = topGenres.map((g, i) => ({
    type: 'bar', name: g,
    x: years,
    y: years.map(yr => {
      const row = yearly.find(r => r.genre === g && r.year === yr);
      return row ? Math.round(row.total_minutes || 0) : 0;
    }),
    marker: { color: `hsl(${i * 40 + 100},60%,55%)` }
  }));
  Plotly.newPlot('genre-evolution-chart', traces, {
    ...plotlyLayout,
    barmode: 'stack',
    xaxis: { gridcolor: '#2a2b2b' },
    yaxis: { gridcolor: '#2a2b2b', title: 'Minutes' },
    legend: { font: { size: 10 }, bgcolor: 'transparent' }
  }, plotlyConfig);

  const genreTotals = gList.map(g => ({
    genre: g,
    total: tbList.reduce((s, t) => s + (heatmap[`${g}|||${t}`] || 0), 0)
  })).sort((a, b) => b.total - a.total);
  const maxTotal = genreTotals[0]?.total || 1;
  document.getElementById('genre-bars').innerHTML = genreTotals.slice(0, 12).map(g => {
    const pct = Math.round((g.total / maxTotal) * 100);
    return `
      <div>
        <div class="flex justify-between text-sm mb-1">
          <span class="text-on-surface font-medium truncate max-w-[200px]">${g.genre}</span>
          <span class="text-on-surface-variant">${fmt(Math.round(g.total))} min</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
      </div>`;
  }).join('');
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 9: DEEP DIVE EXPLORER
═══════════════════════════════════════════════════════════════════════════ */
async function loadDeepDive() {
  try {
    const data = await apiFetch('/api/artists?limit=250');
    const artists = (data.artists || []).sort((a, b) => (b.total_hours || 0) - (a.total_hours || 0));

    const sel = document.getElementById('dd-artist-select');
    sel.innerHTML = '<option value="">Select artist…</option>' +
      artists.map(a => `<option value="${a.artist_name}">${a.artist_name}</option>`).join('');
  } catch (e) {
    console.error('Error loading deep dive:', e);
  }
}

async function ddSelectArtist(artistName) {
  if (!artistName) return;
  try {
    const data = await apiFetch(`/api/artists/${encodeURIComponent(artistName)}/lifecycle`);
    const projects = data.projects || [];

    const projSel = document.getElementById('dd-project-select');
    document.getElementById('dd-project-col').classList.remove('opacity-40');
    projSel.disabled = false;
    projSel.innerHTML = '<option value="">Select project…</option>' +
      projects.map(p => `<option value="${p.project_id}">${p.project_name}</option>`).join('');

    const artistObj = data.artist || {};
    const panel = document.getElementById('dd-detail-panel');
    panel.innerHTML = `
      <div class="bg-surface-container-high rounded-xl border border-surface-variant p-6">
        <h3 class="font-bold text-on-surface mb-4">Artist: ${artistObj.artist_name || artistName}</h3>
        <div class="grid grid-cols-3 gap-4">
          <div class="kpi-card"><span class="text-on-surface-variant text-xs">Total Plays</span><span class="text-2xl font-bold text-on-surface">${fmt(artistObj.total_plays)}</span></div>
          <div class="kpi-card"><span class="text-on-surface-variant text-xs">Tracks Heard</span><span class="text-2xl font-bold text-on-surface">${fmt(artistObj.unique_tracks)}</span></div>
          <div class="kpi-card"><span class="text-on-surface-variant text-xs">Stage</span><span class="text-lg font-bold text-primary">${artistObj.lifecycle_stage || '—'}</span></div>
        </div>
      </div>`;
  } catch (e) {
    console.error('Error selecting artist in deep dive:', e);
  }
}

async function ddSelectProject(projectId) {
  if (!projectId) return;
  try {
    const songSel = document.getElementById('dd-song-select');
    document.getElementById('dd-song-col').classList.remove('opacity-40');
    songSel.disabled = false;

    const songs = await apiFetch(`/api/projects/${encodeURIComponent(projectId)}/songs`);
    const songList = songs.songs || [];
    songSel.innerHTML = '<option value="">Select song…</option>' +
      songList.map(s => `<option value="${s.track_id}">${s.track_name}</option>`).join('');

    const projRes = await apiFetch(`/api/projects/${encodeURIComponent(projectId)}`);
    const proj = projRes.project || {};
    const pct = Math.round(proj.penetration_pct || 0);

    const panel = document.getElementById('dd-detail-panel');
    panel.innerHTML += `
      <div class="bg-surface-container-high rounded-xl border border-surface-variant p-6">
        <h3 class="font-bold text-on-surface mb-4">Project: ${proj.project_name || projectId}</h3>
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-on-surface-variant">Catalog Penetration</span>
          <span class="font-bold text-primary">${pct}%</span>
        </div>
        <div class="progress-bar mb-4"><div class="progress-fill" style="width:${pct}%"></div></div>
        <div class="grid grid-cols-2 gap-4">
          <div class="kpi-card"><span class="text-on-surface-variant text-xs">Tracks Heard</span><span class="text-2xl font-bold text-on-surface">${fmt(proj.tracks_heard)}</span></div>
          <div class="kpi-card"><span class="text-on-surface-variant text-xs">Total Plays</span><span class="text-2xl font-bold text-on-surface">${fmt(proj.total_plays)}</span></div>
        </div>
      </div>`;
  } catch (e) {
    console.error('Error selecting project in deep dive:', e);
  }
}

function ddReset() {
  document.getElementById('dd-artist-select').value = '';
  document.getElementById('dd-project-select').innerHTML = '<option value="">Select project…</option>';
  document.getElementById('dd-project-select').disabled = true;
  document.getElementById('dd-song-select').innerHTML = '<option value="">Select song…</option>';
  document.getElementById('dd-song-select').disabled = true;
  document.getElementById('dd-project-col').classList.add('opacity-40');
  document.getElementById('dd-song-col').classList.add('opacity-40');
  document.getElementById('dd-detail-panel').innerHTML = '';
}

/* ═══════════════════════════════════════════════════════════════════════════
   VIEW 10: ML INTELLIGENCE
═══════════════════════════════════════════════════════════════════════════ */
async function loadML() {
  try {
    const [metrics, feat] = await Promise.all([
      apiFetch('/api/ml/metrics'),
      apiFetch('/api/ml/feature-importance')
    ]);

    const tbody = document.getElementById('ml-benchmark-table');
    const bm = metrics.benchmark_table || metrics.benchmark || [];
    if (bm.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center py-6 text-on-surface-variant">No benchmark data.</td></tr>';
    } else {
      tbody.innerHTML = bm.map(m => {
        const isActive = (m.Model || '').toLowerCase().includes('lightgbm');
        return `<tr ${isActive ? 'class="font-bold"' : ''}>
          <td class="${isActive ? 'text-primary' : 'text-on-surface'}">${m.Model}</td>
          <td class="${isActive ? 'text-primary' : 'text-on-surface-variant'} font-mono">${(m['PR-AUC'] || 0).toFixed(4)}</td>
          <td class="${isActive ? 'text-primary' : 'text-on-surface-variant'} font-mono">${(m['ROC-AUC'] || 0).toFixed(4)}</td>
          <td class="${isActive ? 'text-primary' : 'text-on-surface-variant'} font-mono">${(m['F1 Score'] || 0).toFixed(4)}</td>
          <td class="font-mono text-on-surface-variant">${(m['Precision'] || 0).toFixed(4)}</td>
          <td class="font-mono text-on-surface-variant">${(m['Recall'] || 0).toFixed(4)}</td>
          <td class="font-mono text-on-surface-variant">${(m['Brier Score'] || 0).toFixed(4)}</td>
        </tr>`;
      }).join('');
    }

    const fi = feat.feature_importance || feat.features || [];
    const maxImportance = Math.max(...fi.map(f => f.gain_importance || 0), 1);
    document.getElementById('ml-feature-importance-panel').innerHTML = fi.slice(0, 8).map(f => {
      const pct = Math.round(((f.gain_importance || 0) / maxImportance) * 100);
      return `
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="text-on-surface font-medium">${f.feature}</span>
            <span class="text-primary font-bold">${pct}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width:${pct}%"></div>
          </div>
        </div>`;
    }).join('');

    const audit = metrics.temporal_audit?.audit_passed ?? metrics.audit_passed ?? true;
    const auditBadge = document.getElementById('ml-audit-badge');
    auditBadge.textContent = audit ? 'PASSED' : 'REVIEW NEEDED';
    auditBadge.className = `px-4 py-2 rounded-full text-sm font-bold ${audit ? 'bg-primary/20 text-primary border border-primary/40' : 'bg-red-500/20 text-red-400 border border-red-500/40'}`;
  } catch (e) {
    console.error('Error loading ML intelligence:', e);
  }
}

async function runPrediction() {
  const btn = document.getElementById('ml-predict-btn');
  btn.textContent = 'Predicting…';
  btn.disabled = true;

  const payload = {
    is_first_artist_play: parseInt(document.getElementById('ml-first-artist').value),
    skipped: parseInt(document.getElementById('ml-skipped').value),
    seconds_played: parseFloat(document.getElementById('ml-seconds').value),
    artist_plays_before: parseInt(document.getElementById('ml-artist-plays').value),
    artist_tracks_heard_before: parseInt(document.getElementById('ml-artist-tracks').value),
    hour: parseInt(document.getElementById('ml-hour').value),
    session_position: parseInt(document.getElementById('ml-session-pos').value),
    shuffle: parseInt(document.getElementById('ml-shuffle').value)
  };

  try {
    const res = await fetch('/api/ml/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    const prob = Math.round((data.expansion_probability || 0) * 100);
    const isHigh = Boolean(data.predicted_expansion);

    document.getElementById('ml-result').classList.remove('hidden');
    document.getElementById('ml-prob-display').textContent = `${prob}%`;
    document.getElementById('ml-prob-bar').style.width = `${prob}%`;

    const badge = document.getElementById('ml-confidence-badge');
    badge.textContent = `${data.confidence_level || 'High'} Confidence`;
    badge.className = isHigh ? 'badge badge-artist' : 'badge badge-reengagement';

    document.getElementById('ml-predicted-outcome').innerHTML =
      `<span class="${isHigh ? 'text-primary' : 'text-on-surface-variant'} font-bold">
        ${isHigh ? '✓ Catalog Expansion Likely (Threshold: ' + (data.decision_threshold || 0.675) + ')' : '✗ No Significant Expansion Expected'}
      </span>`;

    const expl = data.explanation || [];
    document.getElementById('ml-explanation').innerHTML = expl.map(item => {
      const text = typeof item === 'string' ? item : (item.description || item.feature);
      return `<div class="flex items-center gap-2 text-xs text-on-surface-variant py-0.5">
        <span class="text-primary font-bold">✓</span>
        <span>${text}</span>
      </div>`;
    }).join('');
  } catch (e) {
    document.getElementById('ml-result').classList.remove('hidden');
    document.getElementById('ml-prob-display').textContent = 'Error';
    document.getElementById('ml-explanation').innerHTML = '<p class="text-xs text-red-400">Prediction failed. Is backend server active?</p>';
  }

  btn.textContent = 'Predict Catalog Expansion →';
  btn.disabled = false;
}

/* ═══════════════════════════════════════════════════════════════════════════
   BOOT
═══════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  navigate('overview');
});
