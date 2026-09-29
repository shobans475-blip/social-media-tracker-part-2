/**
 * Sentinel AI Social Media Intelligence Dashboard Controller
 */

let activePlatform = "all";
let graphRenderer = null;
let sentimentChart = null;
let ageChart = null;
let regionChart = null;
let ws = null;
let isFeedPaused = false;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initPlatformFilters();
  initDemoEventInjection();
  initNlpSandbox();
  
  // Initialize Network Canvas
  graphRenderer = new NetworkGraphRenderer("network-canvas", "node-tooltip");

  // Load Initial Data
  loadAllDashboardData();

  // Connect WebSocket Stream
  connectWebSocket();
});

// Tab Navigation
function initTabs() {
  const tabs = document.querySelectorAll(".tab-item");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      const content = document.getElementById(targetId);
      if (content) content.classList.add("active");

      if (targetId === "tab-network" && graphRenderer) {
        setTimeout(() => graphRenderer.resize(), 100);
      }
    });
  });
}

// Platform Filter
function initPlatformFilters() {
  const filterBtns = document.querySelectorAll(".filter-btn");
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activePlatform = btn.getAttribute("data-platform");
      loadAllDashboardData();
    });
  });
}

// Demo Event Injection
function initDemoEventInjection() {
  const injectThreat = document.getElementById("btn-inject-threat");
  const injectViral = document.getElementById("btn-inject-viral");

  if (injectThreat) {
    injectThreat.addEventListener("click", async () => {
      try {
        await fetch("/api/dashboard/inject-event?event_type=telegram", { method: "POST" });
        loadSummary();
      } catch (e) {
        console.error("Injection failed:", e);
      }
    });
  }

  if (injectViral) {
    injectViral.addEventListener("click", async () => {
      try {
        await fetch("/api/dashboard/inject-event?event_type=twitter", { method: "POST" });
        loadSummary();
      } catch (e) {
        console.error("Injection failed:", e);
      }
    });
  }

  const pauseBtn = document.getElementById("btn-pause-feed");
  if (pauseBtn) {
    pauseBtn.addEventListener("click", () => {
      isFeedPaused = !isFeedPaused;
      pauseBtn.textContent = isFeedPaused ? "▶ Resume" : "⏸ Pause";
    });
  }
}

// NLP Sandbox Evaluation
function initNlpSandbox() {
  const btn = document.getElementById("btn-analyze-sandbox");
  const input = document.getElementById("sandbox-input");
  const resultDiv = document.getElementById("sandbox-result");

  if (!btn || !input || !resultDiv) return;

  btn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) return;

    btn.disabled = true;
    btn.textContent = "Analyzing NLP...";

    try {
      const res = await fetch("/api/sentiment/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text, deep_ai: true })
      });
      const data = await res.json();
      const ana = data.analysis;
      const sent = ana.sentiment;
      const prep = ana.preprocessed;

      let badgeClass = "neutral";
      if (sent.sentiment_label === "positive") badgeClass = "positive";
      if (sent.sentiment_label === "negative") badgeClass = "negative";
      if (sent.hate_speech_flag || sent.toxicity_score > 0.6) badgeClass = "threat";

      resultDiv.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-weight:700;">Detection Results:</span>
          <span class="sentiment-badge ${badgeClass}">${sent.sentiment_label.toUpperCase()}</span>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-top:8px;">
          <div>Language: <strong style="color:#38bdf8;">${prep.language_name} (${prep.language})</strong></div>
          <div>Polarity Score: <strong>${sent.compound_score}</strong></div>
          <div>Toxicity Rating: <strong style="color:${sent.toxicity_score > 0.5 ? '#f43f5e' : '#34d399'};">${(sent.toxicity_score * 100).toFixed(0)}%</strong></div>
          <div>Threat Flag: <strong style="color:${sent.hate_speech_flag ? '#f43f5e' : '#9ca3af'};">${sent.hate_speech_flag ? 'ACTIVE THREAT' : 'NONE'}</strong></div>
          <div>Misinfo Flag: <strong style="color:${sent.misinformation_flag ? '#f59e0b' : '#9ca3af'};">${sent.misinformation_flag ? 'SUSPECT' : 'CLEAR'}</strong></div>
        </div>
        ${data.gemini_deep_intel ? `
          <div style="margin-top:10px; padding:10px; background:rgba(6, 182, 212, 0.1); border-left:3px solid #06b6d4; border-radius:4px;">
            <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; margin-bottom:4px;">✨ Gemini AI Intelligence Assessment:</div>
            <div style="font-size:0.8rem; line-height:1.4; color:#e2e8f0; white-space:pre-line;">${data.gemini_deep_intel}</div>
          </div>
        ` : ''}
      `;
      resultDiv.style.display = "flex";
    } catch (err) {
      resultDiv.innerHTML = `<span style="color:#f43f5e;">Error running NLP analysis: ${err.message}</span>`;
      resultDiv.style.display = "flex";
    } finally {
      btn.disabled = false;
      btn.textContent = "Run Deep NLP & Threat Scan";
    }
  });
}

// Fetch all dashboard metrics
async function loadAllDashboardData() {
  await Promise.all([
    loadSummary(),
    loadFeed(),
    loadNetworkGraph(),
    loadTrends(),
    loadDemographics()
  ]);
}

// Summary KPIs
async function loadSummary() {
  try {
    const url = `/api/dashboard/summary?platform=${activePlatform}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.status !== "success") return;

    const kpis = data.kpis;
    document.getElementById("kpi-total-posts").textContent = (kpis.total_posts_monitored || 0).toLocaleString();
    document.getElementById("kpi-threat-signals").textContent = (kpis.threat_signals_detected || 0);
    document.getElementById("kpi-network-nodes").textContent = (kpis.network_nodes_mapped || 0);
    document.getElementById("kpi-network-edges").textContent = (kpis.network_edges_active || 0);
    document.getElementById("kpi-avg-polarity").textContent = (kpis.avg_sentiment_polarity >= 0 ? `+${kpis.avg_sentiment_polarity}` : kpis.avg_sentiment_polarity);

    // Threat level badge
    const badge = document.getElementById("threat-status-badge");
    if (badge) {
      badge.textContent = `STATUS: ${data.threat_level}`;
      if (data.threat_level === "HIGH ALERT" || data.threat_level === "ELEVATED") {
        badge.className = "status-badge alert";
      } else {
        badge.className = "status-badge";
      }
    }

    // Render sentiment chart
    renderSentimentChart(data.sentiment);
  } catch (e) {
    console.error("Error loading summary:", e);
  }
}

// Live Feed
async function loadFeed() {
  try {
    const url = `/api/dashboard/feed?limit=12&platform=${activePlatform}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.status !== "success") return;

    const container = document.getElementById("feed-stream");
    if (!container) return;
    container.innerHTML = "";

    data.posts.forEach(p => {
      container.appendChild(createFeedItemElement(p));
    });
  } catch (e) {
    console.error("Error loading feed:", e);
  }
}

function createFeedItemElement(p) {
  const item = document.createElement("div");
  const isThreat = p.hate_speech_flag || p.toxicity_score > 0.6 || p.threat_flag;
  item.className = `feed-item ${isThreat ? 'threat' : ''}`;

  let sentClass = "neutral";
  if (p.sentiment_label === "positive" || p.sentiment === "positive") sentClass = "positive";
  if (p.sentiment_label === "negative" || p.sentiment === "negative") sentClass = "negative";
  if (isThreat) sentClass = "threat";

  const dateStr = p.created_at ? new Date(p.created_at).toLocaleTimeString() : "Just now";

  item.innerHTML = `
    <div class="feed-item-header">
      <div class="author-info">
        <span class="platform-pill ${p.platform}">${p.platform}</span>
        <strong style="color:#fff;">${p.user_name || p.user_id}</strong>
        <span style="color:#64748b;">${p.handle || ''}</span>
      </div>
      <span class="sentiment-badge ${sentClass}">${isThreat ? 'ALERT' : (p.sentiment_label || p.sentiment || 'NEUTRAL')}</span>
    </div>
    <div class="feed-text">${escapeHtml(p.text)}</div>
    <div class="feed-meta">
      <span>📍 ${p.user_location || 'India'} &bull; ${dateStr}</span>
      <div class="feed-metrics">
        <span>❤️ ${p.likes || 0}</span>
        <span>🔄 ${p.shares || 0}</span>
      </div>
    </div>
  `;
  return item;
}

function escapeHtml(text) {
  if (!text) return "";
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Network Graph
async function loadNetworkGraph() {
  try {
    const url = `/api/network/graph?platform=${activePlatform}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === "success" && graphRenderer) {
      graphRenderer.setData(data.graph);
      renderInfluencersList(data.graph.top_influencers);
    }
  } catch (e) {
    console.error("Error loading network graph:", e);
  }
}

function renderInfluencersList(influencers) {
  const container = document.getElementById("influencer-list");
  if (!container || !influencers) return;

  container.innerHTML = influencers.map(inf => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:8px; background:rgba(255,255,255,0.02); border-radius:6px; margin-bottom:6px; font-size:12px;">
      <div>
        <strong style="color:#fff;">${inf.label}</strong>
        <div style="color:#64748b; font-size:11px;">${inf.handle} &bull; ${inf.platform}</div>
      </div>
      <div style="text-align:right;">
        <span style="color:#38bdf8; font-weight:700;">PR: ${inf.pagerank}</span>
        <div style="color:#94a3b8; font-size:10px;">${inf.followers ? inf.followers.toLocaleString() : 0} flws</div>
      </div>
    </div>
  `).join("");
}

// Trends
async function loadTrends() {
  try {
    const url = `/api/trends/?platform=${activePlatform}`;
    const res = await fetch(url);
    const json = await res.json();
    if (json.status !== "success") return;
    const data = json.data;

    // Hashtags
    const hashContainer = document.getElementById("hashtag-leaderboard");
    if (hashContainer && data.ranked_hashtags) {
      hashContainer.innerHTML = data.ranked_hashtags.map(h => `
        <div class="hashtag-row">
          <span class="hashtag-name">${h.hashtag}</span>
          <div class="hashtag-stats">
            <span style="color:#94a3b8;">${h.volume} posts</span>
            <span class="velocity-badge ${h.is_alert ? 'alert' : ''}">${h.velocity}</span>
          </div>
        </div>
      `).join("");
    }

    // Topics Cloud / List
    const topicsContainer = document.getElementById("top-topics-list");
    if (topicsContainer && data.top_topics) {
      topicsContainer.innerHTML = data.top_topics.map(t => `
        <span style="display:inline-block; padding:5px 12px; margin:4px; background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59,130,246,0.3); border-radius:20px; font-size:12px; color:#93c5fd;">
          # ${t.topic} <strong style="color:#38bdf8; margin-left:4px;">${t.score}</strong>
        </span>
      `).join("");
    }
  } catch (e) {
    console.error("Error loading trends:", e);
  }
}

// Demographics
async function loadDemographics() {
  try {
    const url = `/api/demographics/?platform=${activePlatform}`;
    const res = await fetch(url);
    const json = await res.json();
    if (json.status !== "success") return;
    const demo = json.demographics;

    renderAgeChart(demo.age_distribution);
    renderRegionChart(demo.regional_distribution);

    const botCount = document.getElementById("demo-bot-count");
    if (botCount) botCount.textContent = `${demo.bot_accounts_count || 0} flagged`;
  } catch (e) {
    console.error("Error loading demographics:", e);
  }
}

// Charts (Chart.js)
function renderSentimentChart(sentimentData) {
  const canvas = document.getElementById("chart-sentiment");
  if (!canvas || !window.Chart) return;

  const dist = sentimentData.distribution || { positive: 10, neutral: 5, negative: 3 };

  if (sentimentChart) sentimentChart.destroy();

  sentimentChart = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [dist.positive || 0, dist.neutral || 0, dist.negative || 0],
        backgroundColor: ["#10b981", "#3b82f6", "#f43f5e"],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { color: "#94a3b8", boxWidth: 12 } }
      },
      cutout: "68%"
    }
  });
}

function renderAgeChart(ageData) {
  const canvas = document.getElementById("chart-age");
  if (!canvas || !window.Chart || !ageData) return;

  if (ageChart) ageChart.destroy();

  const labels = Object.keys(ageData);
  const values = Object.values(ageData);

  ageChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Age %",
        data: values,
        backgroundColor: "#8b5cf6",
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
      },
      plugins: { legend: { display: false } }
    }
  });
}

function renderRegionChart(regionData) {
  const canvas = document.getElementById("chart-region");
  if (!canvas || !window.Chart || !regionData) return;

  if (regionChart) regionChart.destroy();

  const labels = Object.keys(regionData);
  const values = Object.values(regionData);

  regionChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Posts",
        data: values,
        backgroundColor: "#06b6d4",
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { display: false } }
      },
      plugins: { legend: { display: false } }
    }
  });
}

// WebSocket Connection
function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/live-stream`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Connected to Sentinel AI Live WebSocket Stream");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === "NEW_POST" && !isFeedPaused) {
        handleNewStreamPost(data.post);
      }
    } catch (e) {
      console.error("Error processing websocket payload:", e);
    }
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected. Reconnecting in 3s...");
    setTimeout(connectWebSocket, 3000);
  };
}

function handleNewStreamPost(post) {
  const container = document.getElementById("feed-stream");
  if (!container) return;

  // Prepend
  const item = createFeedItemElement(post);
  container.insertBefore(item, container.firstChild);

  // Keep max 20 items in UI
  while (container.children.length > 20) {
    container.removeChild(container.lastChild);
  }

  // Bump total posts KPI
  const kpiTotal = document.getElementById("kpi-total-posts");
  if (kpiTotal) {
    const curr = parseInt(kpiTotal.textContent.replace(/,/g, "")) || 0;
    kpiTotal.textContent = (curr + 1).toLocaleString();
  }

  // If threat, bump threat KPI
  if (post.threat_flag) {
    const kpiThreat = document.getElementById("kpi-threat-signals");
    if (kpiThreat) {
      const curr = parseInt(kpiThreat.textContent) || 0;
      kpiThreat.textContent = (curr + 1);
    }
  }
}
