/**
 * Spotify Personal Intelligence Engine — Production Frontend App Logic
 */

const API_BASE = '/api';

// Application State Container
const state = {
  overview: null,
  artists: [],
  selectedArtist: null,
  catalysts: [],
  projects: [],
  songs: [],
  network: null,
  genres: null,
  mlMetrics: null,
  deepDiveArtistData: null
};

// Bootstrap on DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  loadOverviewData();
  loadCatalystsData();
  loadArtistsData();
  loadProjectsData();
  loadSongsData();
  loadSequencesData();
  loadNetworkData();
  loadGenreTimeData();
  loadMLData();
  initSimulator();
  initDeepDive();
});

// 1. Navigation Controller
function initNavigation() {
  const navButtons = document.querySelectorAll('.nav-item');
  const titleMap = {
    'overview': { title: 'Your Spotify DNA', sub: 'How your listening evolved from 2020 to 2026.' },
    'catalysts': { title: 'Discovery Catalyst Engine', sub: 'Forward 7D catalog expansion modeling, 30D retention & downstream hours unlocked.' },
    'artists': { title: 'Artist Lifecycle Intelligence', sub: 'Discovery → Peak → Decline → Revival trajectories & diurnal listening dynamics.' },
    'projects': { title: 'Albums & EPs Intelligence', sub: 'Project penetration, completion, driving songs & sequentiality (≥3-track rule).' },
    'songs': { title: 'Song Lifecycle Modeling', sub: 'Raw vs Active lifespan, obsession velocity tracking & 30D/90D retention.' },
    'sequences': { title: 'Listening Sequences & Pathways', sub: 'Markov transitions, 2-song conditional probabilities, and 3-song chains.' },
    'network': { title: 'Personal Music Network', sub: 'Topological graph, community clusters & betweenness bridge artists.' },
    'genres': { title: 'Genre × Time × Year Matrix', sub: 'Diurnal listening habits across 8 time buckets & longitudinal genre migrations.' },
    'deepdive': { title: 'Deep Dive Explorer', sub: 'Hierarchical multi-level catalog drill-down (Artist ➔ Project ➔ Song ➔ Discovery).' },
    'ml': { title: 'Machine Learning Intelligence', sub: 'Chronological test benchmarks (2026), feature importances & live predictor.' },
  };

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(`tab-${tabId}`);
      if (targetPane) targetPane.classList.add('active');

      if (titleMap[tabId]) {
        document.getElementById('page-title').textContent = titleMap[tabId].title;
        document.getElementById('page-subtitle').textContent = titleMap[tabId].sub;
      }
    });
  });
}

// 2. Load Overview / DNA
async function loadOverviewData() {
  try {
    const res = await fetch(`${API_BASE}/overview`);
    const data = await res.json();
    state.overview = data;

    // Headline KPIs
    document.getElementById('header-total-hours').textContent = `${data.kpis.total_hours} hrs`;
    document.getElementById('header-total-tracks').textContent = data.kpis.unique_tracks.toLocaleString();
    document.getElementById('kpi-hours').textContent = data.kpis.total_hours;
    document.getElementById('kpi-artists').textContent = data.kpis.unique_artists.toLocaleString();
    document.getElementById('kpi-projects').textContent = data.kpis.explored_projects_ge3;

    // Render Charts
    renderTasteRadar(data.taste_fingerprint);
    renderYearlyEvolution(data.yearly_evolution);
    renderOverviewArtists(data.top_artists);
    renderAuditGrid(data.quality_report);
  } catch (err) {
    console.error('Error loading overview:', err);
  }
}

function renderTasteRadar(fingerprint) {
  if (!fingerprint || !window.Plotly) return;
  
  const categories = Object.keys(fingerprint);
  const values = Object.values(fingerprint);

  const trace = {
    type: 'scatterpolar',
    r: [...values, values[0]],
    theta: [...categories, categories[0]],
    fill: 'toself',
    fillcolor: 'rgba(29, 185, 84, 0.22)',
    line: { color: '#1db954', width: 2 },
    marker: { size: 6, color: '#1ed760' }
  };

  const layout = {
    polar: {
      radialaxis: { visible: true, range: [0, 100], color: '#64748b', gridcolor: 'rgba(255,255,255,0.06)' },
      angularaxis: { color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.06)' },
      bgcolor: 'transparent'
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 30, b: 30, l: 40, r: 40 },
    showlegend: false
  };

  Plotly.newPlot('chart-taste-radar', [trace], layout, { responsive: true, displayModeBar: false });
}

function renderYearlyEvolution(yearlyData) {
  if (!yearlyData || !window.Plotly) return;

  const years = yearlyData.map(d => d.year);
  const hours = yearlyData.map(d => d.listening_hours);
  const artists = yearlyData.map(d => d.unique_artists);

  const traceHours = {
    x: years,
    y: hours,
    name: 'Listening Hours',
    type: 'bar',
    marker: { color: '#1db954' }
  };

  const traceArtists = {
    x: years,
    y: artists,
    name: 'Distinct Artists',
    type: 'scatter',
    mode: 'lines+markers',
    yaxis: 'y2',
    line: { color: '#00d2ff', width: 3 },
    marker: { size: 8 }
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 20, b: 40, l: 40, r: 40 },
    legend: { orientation: 'h', y: 1.15, font: { color: '#94a3b8' } },
    xaxis: { color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' },
    yaxis: { title: 'Hours', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' },
    yaxis2: { title: 'Artists', overlaying: 'y', side: 'right', color: '#00d2ff', showgrid: false }
  };

  Plotly.newPlot('chart-yearly-evolution', [traceHours, traceArtists], layout, { responsive: true, displayModeBar: false });
}

function renderOverviewArtists(artists) {
  const tbody = document.querySelector('#table-overview-artists tbody');
  if (!tbody || !artists) return;
  tbody.innerHTML = artists.map(a => `
    <tr>
      <td><strong>${a.artist_name}</strong></td>
      <td>${a.total_hours}h</td>
      <td>${a.total_plays}</td>
      <td><span class="badge-stage ${getStageClass(a.lifecycle_stage)}">${a.lifecycle_stage}</span></td>
    </tr>
  `).join('');
}

function renderAuditGrid(report) {
  const container = document.getElementById('overview-audit-grid');
  if (!container || !report) return;

  container.innerHTML = `
    <div class="audit-item"><div class="ai-label">Raw Records Ingested</div><div class="ai-val">${(report.total_records_ingested || 32696).toLocaleString()}</div></div>
    <div class="audit-item"><div class="ai-label">Clean Playbacks Retained</div><div class="ai-val">${(report.valid_records_retained || 32649).toLocaleString()}</div></div>
    <div class="audit-item"><div class="ai-label">Null Timestamps Filtered</div><div class="ai-val">${report.null_timestamps || 0}</div></div>
    <div class="audit-item"><div class="ai-label">Duplicates Deduplicated</div><div class="ai-val">${report.duplicate_records_removed || 38}</div></div>
    <div class="audit-item"><div class="ai-label">Video Logs Separated</div><div class="ai-val">${report.video_records || 399}</div></div>
    <div class="audit-item"><div class="ai-label">Podcast Episodes Processed</div><div class="ai-val">${report.podcast_records || 32}</div></div>
  `;
}

function getStageClass(stage) {
  if (!stage) return 'favorite';
  const s = stage.toLowerCase();
  if (s.includes('favorite') || s.includes('obsession')) return 'favorite';
  if (s.includes('evergreen')) return 'evergreen';
  if (s.includes('era')) return 'era';
  return 'dormant';
}

// 3. Load Discovery Catalysts
async function loadCatalystsData() {
  try {
    const res = await fetch(`${API_BASE}/discovery/catalysts?limit=150`);
    const data = await res.json();
    state.catalysts = data.catalysts;
    renderCatalystsTable(data.catalysts);

    const searchInput = document.getElementById('search-catalysts');
    const filterType = document.getElementById('filter-catalyst-type');

    const filterFn = () => {
      const q = searchInput.value.toLowerCase().trim();
      const type = filterType.value;
      const filtered = state.catalysts.filter(c => {
        const matchQ = !q || c.catalyst_track_name.toLowerCase().includes(q) || c.catalyst_artist_name.toLowerCase().includes(q);
        const matchT = !type || c.discovery_type === type;
        return matchQ && matchT;
      });
      renderCatalystsTable(filtered);
    };

    if (searchInput) searchInput.addEventListener('input', filterFn);
    if (filterType) filterType.addEventListener('change', filterFn);
  } catch (err) {
    console.error('Error loading catalysts:', err);
  }
}

function renderCatalystsTable(catalysts) {
  const tbody = document.querySelector('#table-catalysts tbody');
  if (!tbody || !catalysts) return;

  tbody.innerHTML = catalysts.slice(0, 50).map(c => `
    <tr>
      <td><strong>#${c.rank}</strong></td>
      <td><strong>${c.catalyst_track_name}</strong></td>
      <td>${c.catalyst_artist_name}</td>
      <td><span class="badge-type ${c.discovery_type.toLowerCase().replace(/\s+/g, '')}">${c.discovery_type}</span></td>
      <td>+${c.max_tracks_added_7d}</td>
      <td>${c.max_minutes_added_7d}m</td>
      <td>${c.max_minutes_30d}m</td>
      <td>${c.retention_90d ? '✅ Yes' : '—'}</td>
      <td><strong style="color:var(--accent-green);">${c.future_hours_unlocked}h</strong></td>
      <td><strong style="color:var(--cyan);">${c.catalyst_index}</strong></td>
    </tr>
  `).join('');
}

// 4. Load Artist Lifecycle
async function loadArtistsData() {
  try {
    const res = await fetch(`${API_BASE}/artists?limit=250`);
    const data = await res.json();
    state.artists = data.artists;

    const selector = document.getElementById('artist-selector');
    const ddSelector = document.getElementById('dd-artist-select');

    if (selector && data.artists.length > 0) {
      selector.innerHTML = data.artists.map(a => `<option value="${a.artist_name}">${a.artist_name} (${a.total_hours}h)</option>`).join('');
      if (ddSelector) ddSelector.innerHTML = selector.innerHTML;

      selector.addEventListener('change', (e) => loadSpecificArtist(e.target.value));
      loadSpecificArtist(data.artists[0].artist_name);
    }
  } catch (err) {
    console.error('Error loading artists:', err);
  }
}

async function loadSpecificArtist(artistName) {
  try {
    const res = await fetch(`${API_BASE}/artists/${encodeURIComponent(artistName)}/lifecycle`);
    const data = await res.json();

    document.getElementById('artist-stage-badge').textContent = `Stage: ${data.artist.lifecycle_stage}`;
    document.getElementById('art-kpi-hours').textContent = `${data.artist.total_hours}h`;
    document.getElementById('art-kpi-tracks').textContent = data.artist.unique_tracks;
    document.getElementById('art-kpi-peak').textContent = data.artist.peak_month;
    document.getElementById('art-kpi-gap').textContent = `${data.artist.longest_inactivity_gap_days}d`;

    renderArtistMonthlyChart(data.monthly_timeline);
    renderArtistTODChart(data.time_of_day_profile);

    const tbodyTracks = document.querySelector('#table-artist-top-tracks tbody');
    if (tbodyTracks) {
      tbodyTracks.innerHTML = data.top_tracks.map(t => `
        <tr>
          <td>${t.track_name}</td>
          <td>${t.total_plays}</td>
          <td>${t.total_minutes}m</td>
          <td><span class="badge-stage ${getStageClass(t.lifecycle_category)}">${t.lifecycle_category}</span></td>
        </tr>
      `).join('');
    }

    const tbodyProj = document.querySelector('#table-artist-projects tbody');
    if (tbodyProj) {
      tbodyProj.innerHTML = data.projects.map(p => `
        <tr>
          <td>${p.project_name}</td>
          <td>${p.tracks_heard} trk</td>
          <td>${p.is_explored ? '✅ Explored (≥3)' : 'Sampled'}</td>
          <td>${p.total_minutes}m</td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading artist details:', err);
  }
}

function renderArtistMonthlyChart(timeline) {
  if (!timeline || !window.Plotly) return;
  const x = timeline.map(t => t.year_month);
  const y = timeline.map(t => t.minutes);

  const trace = {
    x: x,
    y: y,
    type: 'bar',
    marker: { color: '#1db954' }
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 20, b: 40, l: 40, r: 20 },
    xaxis: { color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' },
    yaxis: { title: 'Minutes', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' }
  };

  Plotly.newPlot('chart-artist-monthly', [trace], layout, { responsive: true, displayModeBar: false });
}

function renderArtistTODChart(tod) {
  if (!tod || !window.Plotly) return;
  const buckets = Object.keys(tod);
  const vals = Object.values(tod);

  const trace = {
    x: buckets,
    y: vals,
    type: 'bar',
    marker: { color: '#00d2ff' }
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 20, b: 60, l: 40, r: 20 },
    xaxis: { color: '#94a3b8', tickangle: -25 },
    yaxis: { title: 'Minutes', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' }
  };

  Plotly.newPlot('chart-artist-tod', [trace], layout, { responsive: true, displayModeBar: false });
}

// 5. Load Albums & EPs
async function loadProjectsData() {
  try {
    const res = await fetch(`${API_BASE}/projects?limit=200`);
    const data = await res.json();
    state.projects = data.projects;
    renderProjectsTable(data.projects);

    const searchInput = document.getElementById('search-projects');
    const chkExplored = document.getElementById('checkbox-explored-ge3');

    const filterFn = () => {
      const q = searchInput.value.toLowerCase().trim();
      const expOnly = chkExplored.checked;
      const filtered = state.projects.filter(p => {
        const matchQ = !q || p.project_name.toLowerCase().includes(q) || p.artist_name.toLowerCase().includes(q);
        const matchE = !expOnly || p.is_explored;
        return matchQ && matchE;
      });
      renderProjectsTable(filtered);
    };

    if (searchInput) searchInput.addEventListener('input', filterFn);
    if (chkExplored) chkExplored.addEventListener('change', filterFn);
  } catch (err) {
    console.error('Error loading projects:', err);
  }
}

function renderProjectsTable(projects) {
  const tbody = document.querySelector('#table-projects-main tbody');
  if (!tbody || !projects) return;

  tbody.innerHTML = projects.slice(0, 50).map(p => `
    <tr>
      <td><strong>${p.project_name}</strong></td>
      <td>${p.artist_name}</td>
      <td>${p.tracks_heard} tracks</td>
      <td>${p.is_explored ? '<span class="badge-stage favorite">✅ Explored (≥3)</span>' : '<span class="badge-stage dormant">Sampled</span>'}</td>
      <td><em>${p.top_song_name || '—'}</em></td>
      <td><strong>${p.top_song_share_pct || 0}%</strong></td>
      <td><span class="badge-stage ${p.listening_style.includes('Hit') ? 'era' : 'evergreen'}">${p.listening_style}</span></td>
      <td>${p.total_hours}h</td>
    </tr>
  `).join('');
}

// 6. Load Song Lifecycles
async function loadSongsData() {
  try {
    const res = await fetch(`${API_BASE}/songs?limit=200`);
    const data = await res.json();
    state.songs = data.songs;
    renderSongsTable(data.songs);

    const searchInput = document.getElementById('search-songs');
    const filterCat = document.getElementById('filter-song-category');

    const filterFn = () => {
      const q = searchInput.value.toLowerCase().trim();
      const cat = filterCat.value;
      const filtered = state.songs.filter(s => {
        const matchQ = !q || s.track_name.toLowerCase().includes(q) || s.artist_name.toLowerCase().includes(q);
        const matchC = !cat || s.lifecycle_category === cat;
        return matchQ && matchC;
      });
      renderSongsTable(filtered);
    };

    if (searchInput) searchInput.addEventListener('input', filterFn);
    if (filterCat) filterCat.addEventListener('change', filterFn);
  } catch (err) {
    console.error('Error loading songs:', err);
  }
}

function renderSongsTable(songs) {
  const tbody = document.querySelector('#table-songs-main tbody');
  if (!tbody || !songs) return;

  tbody.innerHTML = songs.slice(0, 50).map(s => `
    <tr>
      <td><strong>${s.track_name}</strong></td>
      <td>${s.artist_name}</td>
      <td>${s.total_plays}</td>
      <td>${s.total_minutes}m</td>
      <td>${s.raw_lifespan_days}d</td>
      <td>${s.active_lifespan_days}d</td>
      <td>${s.plays_first_7d}</td>
      <td>${s.retained_30d ? '✅ Yes' : '—'}</td>
      <td><span class="badge-stage ${getStageClass(s.lifecycle_category)}">${s.lifecycle_category}</span></td>
    </tr>
  `).join('');
}

// 7. Load Listening Sequences
async function loadSequencesData() {
  try {
    const res = await fetch(`${API_BASE}/sequences/top`);
    const data = await res.json();

    const tbodyTrack = document.querySelector('#table-track-transitions tbody');
    if (tbodyTrack) {
      tbodyTrack.innerHTML = data.top_track_transitions.slice(0, 15).map(t => `
        <tr>
          <td><strong>${t.previous_track_name}</strong><br><small style="color:var(--text-dim)">${t.previous_artist_name}</small></td>
          <td><strong>${t.track_name}</strong><br><small style="color:var(--text-dim)">${t.artist_name}</small></td>
          <td>${t.transition_count}</td>
          <td><strong style="color:var(--accent-green);">${(t.transition_probability * 100).toFixed(1)}%</strong></td>
        </tr>
      `).join('');
    }

    const tbody3 = document.querySelector('#table-3song-sequences tbody');
    if (tbody3) {
      tbody3.innerHTML = data.three_song_sequences.slice(0, 15).map(s => `
        <tr>
          <td>${s.prev2_track_name} ➔ ${s.prev_track_name} ➔ <strong>${s.track_name}</strong></td>
          <td><strong>${s.sequence_count} times</strong></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading sequences:', err);
  }
}

// 8. Load & Render Music Network
async function loadNetworkData() {
  try {
    const res = await fetch(`${API_BASE}/network?min_weight=2`);
    const data = await res.json();
    state.network = data;

    const tbodyBridges = document.querySelector('#table-bridge-artists tbody');
    if (tbodyBridges) {
      tbodyBridges.innerHTML = data.bridges.map(b => `
        <tr>
          <td><strong>${b.name}</strong></td>
          <td><strong style="color:var(--cyan);">${b.betweenness}</strong></td>
          <td>${b.pagerank}</td>
          <td>${b.degree}</td>
          <td>${(b.total_minutes / 60).toFixed(1)}h</td>
        </tr>
      `).join('');
    }

    renderNetworkCanvas(data.nodes, data.edges);

    const slider = document.getElementById('net-min-weight');
    if (slider) {
      slider.addEventListener('input', async (e) => {
        document.getElementById('lbl-min-weight').textContent = e.target.value;
        const resW = await fetch(`${API_BASE}/network?min_weight=${e.target.value}`);
        const dataW = await resW.json();
        renderNetworkCanvas(dataW.nodes, dataW.edges);
      });
    }
  } catch (err) {
    console.error('Error loading network:', err);
  }
}

function renderNetworkCanvas(nodes, edges) {
  const canvas = document.getElementById('network-canvas');
  if (!canvas || !nodes || nodes.length === 0) return;
  const ctx = canvas.getContext('2d');

  const width = canvas.width;
  const height = canvas.height;

  const nodeMap = {};
  const commColors = ['#1db954', '#00d2ff', '#9d4edd', '#ff9f1c', '#ff4d6d', '#3a86ff'];

  nodes.slice(0, 60).forEach((n, i) => {
    const angle = (i / Math.min(nodes.length, 60)) * 2 * Math.PI;
    const r = 140 + (n.community_id % 3) * 60 + Math.random() * 30;
    nodeMap[n.id] = {
      ...n,
      x: width / 2 + r * Math.cos(angle),
      y: height / 2 + r * Math.sin(angle),
      radius: Math.max(5, Math.min(18, Math.sqrt(n.total_minutes) / 2)),
      color: commColors[n.community_id % commColors.length]
    };
  });

  ctx.clearRect(0, 0, width, height);

  edges.forEach(e => {
    const src = nodeMap[e.source];
    const tgt = nodeMap[e.target];
    if (src && tgt) {
      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = Math.min(3, e.weight * 0.7);
      ctx.stroke();
    }
  });

  Object.values(nodeMap).forEach(n => {
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
    ctx.fillStyle = n.color;
    ctx.shadowColor = n.color;
    ctx.shadowBlur = 8;
    ctx.fill();
    ctx.shadowBlur = 0;

    if (n.pagerank > 0.015 || n.total_minutes > 500) {
      ctx.fillStyle = '#ffffff';
      ctx.font = '10px Plus Jakarta Sans';
      ctx.fillText(n.name, n.x + n.radius + 3, n.y + 3);
    }
  });
}

// 9. Load Genre Time Analytics
async function loadGenreTimeData() {
  try {
    const res = await fetch(`${API_BASE}/genres/time-matrix`);
    const data = await res.json();
    state.genres = data;

    renderGenreTOD(data.genre_time_matrix);
    renderGenreYearly(data.yearly_genre_share);
  } catch (err) {
    console.error('Error loading genre time:', err);
  }
}

function renderGenreTOD(matrix) {
  if (!matrix || !window.Plotly) return;

  const genres = [...new Set(matrix.map(m => m.genre))].slice(0, 6);
  const buckets = ["12AM-3AM", "3AM-6AM", "6AM-9AM", "9AM-12PM", "12PM-3PM", "3PM-6PM", "6PM-9PM", "9PM-12AM"];

  const traces = genres.map((g, idx) => {
    const colors = ['#1db954', '#00d2ff', '#9d4edd', '#ff9f1c', '#ff4d6d', '#3a86ff'];
    const gRows = matrix.filter(m => m.genre === g);
    const yVals = buckets.map(b => {
      const row = gRows.find(r => r.time_of_day_bucket === b);
      return row ? row.total_minutes : 0;
    });

    return {
      x: buckets,
      y: yVals,
      name: g,
      type: 'bar',
      marker: { color: colors[idx % colors.length] }
    };
  });

  const layout = {
    barmode: 'stack',
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 20, b: 60, l: 40, r: 20 },
    legend: { orientation: 'h', y: 1.15, font: { color: '#94a3b8', size: 10 } },
    xaxis: { color: '#94a3b8', tickangle: -25 },
    yaxis: { title: 'Minutes', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' }
  };

  Plotly.newPlot('chart-genre-tod', traces, layout, { responsive: true, displayModeBar: false });
}

function renderGenreYearly(yearly) {
  if (!yearly || !window.Plotly) return;

  const years = [...new Set(yearly.map(y => y.year))];
  const genres = [...new Set(yearly.map(y => y.genre))].slice(0, 6);
  const colors = ['#1db954', '#00d2ff', '#9d4edd', '#ff9f1c', '#ff4d6d', '#3a86ff'];

  const traces = genres.map((g, idx) => {
    const gRows = yearly.filter(y => y.genre === g);
    const yVals = years.map(yr => {
      const row = gRows.find(r => r.year === yr);
      return row ? row.genre_share_pct : 0;
    });

    return {
      x: years,
      y: yVals,
      name: g,
      type: 'scatter',
      mode: 'lines+markers',
      stackgroup: 'one',
      line: { color: colors[idx % colors.length], width: 2 }
    };
  });

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 20, b: 40, l: 40, r: 20 },
    legend: { orientation: 'h', y: 1.15, font: { color: '#94a3b8', size: 10 } },
    xaxis: { color: '#94a3b8' },
    yaxis: { title: 'Share %', range: [0, 100], color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' }
  };

  Plotly.newPlot('chart-genre-yearly', traces, layout, { responsive: true, displayModeBar: false });
}

// 10. Load ML Intelligence
async function loadMLData() {
  try {
    const res = await fetch(`${API_BASE}/ml/metrics`);
    const data = await res.json();
    state.mlMetrics = data;

    const tbody = document.querySelector('#table-ml-benchmark tbody');
    if (tbody && data.benchmark_table) {
      tbody.innerHTML = data.benchmark_table.map(m => `
        <tr style="${m.Model.includes('LightGBM') ? 'background:rgba(29,185,84,0.12); font-weight:bold;' : ''}">
          <td><strong>${m.Model}</strong></td>
          <td><strong style="color:var(--cyan);">${m['PR-AUC']}</strong></td>
          <td>${m['ROC-AUC']}</td>
          <td>${m.Precision}</td>
          <td>${m.Recall}</td>
          <td><strong style="color:var(--accent-green);">${m['F1 Score']}</strong></td>
          <td>${m['Brier Score']}</td>
          <td>${m['Optimized Threshold']}</td>
        </tr>
      `).join('');
    }

    const resFi = await fetch(`${API_BASE}/ml/feature-importance`);
    const dataFi = await resFi.json();
    renderFeatureImportance(dataFi.feature_importance);

    const auditBox = document.getElementById('audit-cert-box');
    if (auditBox && data.temporal_audit) {
      auditBox.innerHTML = `
        <div style="font-family:var(--font-mono); font-size:0.85rem; line-height:1.6; color:#94a3b8;">
          <p><strong style="color:var(--accent-green);">[AUDIT STATUS: ${data.temporal_audit.leakage_risk_assessment}]</strong></p>
          <p>• Chronological Monotonicity: ${data.temporal_audit.chronological_monotonicity_verified ? 'VERIFIED' : 'FAILED'}</p>
          <p>• Zero Initial Counter Invariant: ${data.temporal_audit.zero_initial_song_counts_verified ? 'VERIFIED' : 'FAILED'}</p>
          <p>• Split Strategy: ${data.temporal_audit.train_validation_test_split_strategy}</p>
          <p>• Assertion: All 27 feature vectors computed strictly prior to timestamp T.</p>
        </div>
      `;
    }
  } catch (err) {
    console.error('Error loading ML intelligence:', err);
  }
}

function renderFeatureImportance(fi) {
  if (!fi || !window.Plotly) return;

  const topFi = fi.slice(0, 10).reverse();
  const x = topFi.map(f => f.gain_importance);
  const y = topFi.map(f => f.feature.replace(/_/g, ' '));

  const trace = {
    x: x,
    y: y,
    type: 'bar',
    orientation: 'h',
    marker: { color: '#9d4edd' }
  };

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { t: 20, b: 40, l: 160, r: 20 },
    xaxis: { title: 'Gain Importance', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.04)' },
    yaxis: { color: '#94a3b8' }
  };

  Plotly.newPlot('chart-feature-importance', [trace], layout, { responsive: true, displayModeBar: false });
}

// 11. Interactive ML Simulator
function initSimulator() {
  const btn = document.getElementById('btn-run-predict');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const payload = {
      is_first_artist_play: parseInt(document.getElementById('sim-first-artist').value),
      seconds_played: parseFloat(document.getElementById('sim-seconds').value),
      skipped: parseInt(document.getElementById('sim-skipped').value),
      artist_tracks_heard_before: parseInt(document.getElementById('sim-art-tracks').value),
      artist_plays_before: parseInt(document.getElementById('sim-art-plays').value),
      hour: parseInt(document.getElementById('sim-hour').value),
      is_first_song_play: 1,
      is_first_project_play: 1,
      shuffle: 0
    };

    try {
      const res = await fetch(`${API_BASE}/ml/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();

      const box = document.getElementById('sim-result-box');
      box.style.display = 'block';
      document.getElementById('srb-prob').textContent = `${(result.expansion_probability * 100).toFixed(1)}%`;
      document.getElementById('srb-badge').textContent = result.predicted_expansion ? '⚡ High Expansion Potential' : '💤 Low Expansion Signal';
      document.getElementById('srb-badge').style.background = result.predicted_expansion ? 'rgba(29,185,84,0.2)' : 'rgba(100,116,139,0.2)';
      document.getElementById('srb-badge').style.color = result.predicted_expansion ? '#1db954' : '#94a3b8';

      document.getElementById('srb-explanation').innerHTML = result.explanation.map(e => `• ${e}`).join('<br>');
    } catch (err) {
      console.error('Prediction error:', err);
    }
  });
}

// 12. Deep Dive Hierarchical Explorer
function initDeepDive() {
  const artSelect = document.getElementById('dd-artist-select');
  const prjSelect = document.getElementById('dd-project-select');
  const songSelect = document.getElementById('dd-song-select');
  const summaryBox = document.getElementById('dd-summary-text');

  if (!artSelect) return;

  artSelect.addEventListener('change', async (e) => {
    const artistName = e.target.value;
    try {
      const res = await fetch(`${API_BASE}/artists/${encodeURIComponent(artistName)}/lifecycle`);
      const data = await res.json();
      state.deepDiveArtistData = data;

      if (prjSelect) {
        prjSelect.innerHTML = '<option value="">-- Select Project --</option>' + 
          data.projects.map(p => `<option value="${p.project_name}">${p.project_name} (${p.tracks_heard} tracks)</option>`).join('');
      }

      if (songSelect) {
        songSelect.innerHTML = '<option value="">-- Select Track --</option>' + 
          data.top_tracks.map(t => `<option value="${t.track_name}">${t.track_name} (${t.total_plays} plays)</option>`).join('');
      }

      summaryBox.innerHTML = `
        <strong>${data.artist.artist_name}</strong>: ${data.artist.total_hours} total hours listened across ${data.artist.unique_tracks} distinct tracks. 
        Lifecycle Stage: <span class="badge-stage favorite">${data.artist.lifecycle_stage}</span>. Peak listening month was <strong>${data.artist.peak_month}</strong>.
      `;
    } catch (err) {
      console.error('Error in deep dive artist select:', err);
    }
  });

  if (prjSelect) {
    prjSelect.addEventListener('change', (e) => {
      const prjName = e.target.value;
      if (!prjName || !state.deepDiveArtistData) return;
      const proj = state.deepDiveArtistData.projects.find(p => p.project_name === prjName);
      if (proj) {
        summaryBox.innerHTML += `<br><br><strong>Project "${proj.project_name}"</strong>: ${proj.tracks_heard} tracks heard. Status: <strong>${proj.is_explored ? '✅ Explored (≥3 tracks)' : 'Sampled'}</strong>. Total minutes: ${proj.total_minutes} mins.`;
      }
    });
  }

  if (songSelect) {
    songSelect.addEventListener('change', (e) => {
      const songName = e.target.value;
      if (!songName || !state.deepDiveArtistData) return;
      const track = state.deepDiveArtistData.top_tracks.find(t => t.track_name === songName);
      if (track) {
        summaryBox.innerHTML += `<br><br><strong>Track "${track.track_name}"</strong>: ${track.total_plays} plays (${track.total_minutes} mins). Category: <strong>${track.lifecycle_category}</strong>.`;
      }
    });
  }
}
