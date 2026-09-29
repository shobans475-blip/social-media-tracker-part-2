/**
 * Sentinel Force-Directed Graph Engine for NetworkX Social Graph Visualization
 */
class NetworkGraphRenderer {
  constructor(canvasId, tooltipId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.tooltip = document.getElementById(tooltipId);
    
    this.nodes = [];
    this.links = [];
    this.nodeMap = new Map();
    
    // Transform & interaction state
    this.scale = 1.0;
    this.panX = 0;
    this.panY = 0;
    this.isDragging = false;
    this.dragNode = null;
    this.hoverNode = null;
    this.lastMouse = { x: 0, y: 0 };
    
    this.clusterColors = [
      '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#f43f5e'
    ];

    this.initEvents();
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
    if (this.panX === 0 && this.panY === 0) {
      this.panX = this.canvas.width / 2;
      this.panY = this.canvas.height / 2;
    }
  }

  setData(data) {
    if (!data || !data.nodes) return;
    
    this.nodeMap.clear();
    const existingPos = new Map(this.nodes.map(n => [n.id, { x: n.x, y: n.y, vx: n.vx, vy: n.vy }]));

    this.nodes = data.nodes.map(n => {
      const prev = existingPos.get(n.id);
      return {
        ...n,
        x: prev ? prev.x : (Math.random() - 0.5) * 400,
        y: prev ? prev.y : (Math.random() - 0.5) * 400,
        vx: prev ? prev.vx : (Math.random() - 0.5) * 2,
        vy: prev ? prev.vy : (Math.random() - 0.5) * 2,
        color: this.clusterColors[(n.group || 1) % this.clusterColors.length]
      };
    });

    this.nodes.forEach(n => this.nodeMap.set(n.id, n));

    this.links = (data.links || []).map(l => {
      const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
      const targetId = typeof l.target === 'object' ? l.target.id : l.target;
      return {
        ...l,
        sourceNode: this.nodeMap.get(sourceId),
        targetNode: this.nodeMap.get(targetId)
      };
    }).filter(l => l.sourceNode && l.targetNode);
  }

  updatePhysics() {
    const kRepel = 1200;
    const kSpring = 0.04;
    const damping = 0.88;
    const targetDist = 90;

    // Node-Node Repulsion
    for (let i = 0; i < this.nodes.length; i++) {
      const n1 = this.nodes[i];
      for (let j = i + 1; j < this.nodes.length; j++) {
        const n2 = this.nodes[j];
        const dx = n2.x - n1.x;
        const dy = n2.y - n1.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        if (dist < 350) {
          const force = (kRepel / (dist * dist));
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          n1.vx -= fx;
          n1.vy -= fy;
          n2.vx += fx;
          n2.vy += fy;
        }
      }
    }

    // Link Spring Forces
    for (const link of this.links) {
      const s = link.sourceNode;
      const t = link.targetNode;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const displacement = dist - targetDist;
      const force = displacement * kSpring;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      s.vx += fx;
      s.vy += fy;
      t.vx -= fx;
      t.vy -= fy;
    }

    // Center Gravity & Integration
    for (const node of this.nodes) {
      if (node === this.dragNode) continue;
      node.vx -= node.x * 0.003;
      node.vy -= node.y * 0.003;
      node.vx *= damping;
      node.vy *= damping;
      node.x += node.vx;
      node.y += node.vy;
    }
  }

  render() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    ctx.save();
    ctx.translate(this.panX, this.panY);
    ctx.scale(this.scale, this.scale);

    // Draw Links
    for (const link of this.links) {
      const s = link.sourceNode;
      const t = link.targetNode;
      const isHighlighted = (this.hoverNode && (this.hoverNode === s || this.hoverNode === t));
      
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = isHighlighted ? 'rgba(6, 182, 212, 0.8)' : 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = isHighlighted ? 2 : 1;
      ctx.stroke();

      // Arrow
      const angle = Math.atan2(t.y - s.y, t.x - s.x);
      const arrowDist = (t.radius || 12) + 3;
      const ax = t.x - Math.cos(angle) * arrowDist;
      const ay = t.y - Math.sin(angle) * arrowDist;
      
      ctx.beginPath();
      ctx.fillStyle = isHighlighted ? '#06b6d4' : 'rgba(255, 255, 255, 0.3)';
      ctx.arc(ax, ay, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw Nodes
    for (const node of this.nodes) {
      const r = node.radius || 12;
      const isHovered = (this.hoverNode === node);

      // Glow effect
      if (isHovered) {
        ctx.save();
        ctx.shadowColor = node.color;
        ctx.shadowBlur = 18;
        ctx.beginPath();
        ctx.arc(node.x, node.y, r + 4, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.globalAlpha = 0.3;
        ctx.fill();
        ctx.restore();
      }

      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();
      ctx.lineWidth = isHovered ? 2.5 : 1.5;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();

      // Label
      ctx.font = '10px Inter, sans-serif';
      ctx.fillStyle = isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.75)';
      ctx.textAlign = 'center';
      ctx.fillText(node.label || node.id, node.x, node.y + r + 13);
    }

    ctx.restore();
  }

  animate() {
    this.updatePhysics();
    this.render();
    requestAnimationFrame(() => this.animate());
  }

  getCanvasCoords(e) {
    const rect = this.canvas.getBoundingClientRect();
    const clientX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
    const clientY = e.clientY || (e.touches && e.touches[0].clientY) || 0;
    return {
      x: (clientX - rect.left - this.panX) / this.scale,
      y: (clientY - rect.top - this.panY) / this.scale,
      screenX: clientX,
      screenY: clientY
    };
  }

  findNodeAt(x, y) {
    for (let i = this.nodes.length - 1; i >= 0; i--) {
      const n = this.nodes[i];
      const r = (n.radius || 12) + 4;
      const dx = n.x - x;
      const dy = n.y - y;
      if (dx * dx + dy * dy <= r * r) {
        return n;
      }
    }
    return null;
  }

  initEvents() {
    this.canvas.addEventListener('mousedown', (e) => {
      const coords = this.getCanvasCoords(e);
      const node = this.findNodeAt(coords.x, coords.y);
      if (node) {
        this.dragNode = node;
      } else {
        this.isDragging = true;
      }
      this.lastMouse = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mousemove', (e) => {
      const coords = this.getCanvasCoords(e);

      if (this.dragNode) {
        this.dragNode.x = coords.x;
        this.dragNode.y = coords.y;
        this.dragNode.vx = 0;
        this.dragNode.vy = 0;
      } else if (this.isDragging) {
        this.panX += e.clientX - this.lastMouse.x;
        this.panY += e.clientY - this.lastMouse.y;
        this.lastMouse = { x: e.clientX, y: e.clientY };
      } else {
        const hovered = this.findNodeAt(coords.x, coords.y);
        if (hovered !== this.hoverNode) {
          this.hoverNode = hovered;
          this.updateTooltip(hovered, e.clientX, e.clientY);
        } else if (this.hoverNode) {
          this.positionTooltip(e.clientX, e.clientY);
        }
      }
    });

    window.addEventListener('mouseup', () => {
      this.dragNode = null;
      this.isDragging = false;
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
      this.scale = Math.max(0.3, Math.min(3.5, this.scale * zoomFactor));
    }, { passive: false });
  }

  updateTooltip(node, screenX, screenY) {
    if (!this.tooltip) return;
    if (!node) {
      this.tooltip.style.display = 'none';
      return;
    }

    this.tooltip.innerHTML = `
      <div style="font-weight:700; color:#fff; margin-bottom:3px;">${node.label || node.id}</div>
      <div style="color:#94a3b8; font-size:11px;">${node.handle || ''} &bull; ${node.platform || 'source'}</div>
      <div style="margin-top:6px; display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:11px;">
        <div>PageRank: <strong style="color:#38bdf8;">${node.pagerank || 0.05}</strong></div>
        <div>Community: <strong style="color:#a78bfa;">#${node.group || 1}</strong></div>
        <div>Followers: <strong style="color:#34d399;">${node.followers ? node.followers.toLocaleString() : 'N/A'}</strong></div>
        <div>Centrality: <strong style="color:#fbbf24;">${node.betweenness || 0}</strong></div>
      </div>
    `;
    this.tooltip.style.display = 'block';
    this.positionTooltip(screenX, screenY);
  }

  positionTooltip(screenX, screenY) {
    if (!this.tooltip) return;
    const parentRect = this.canvas.parentElement.getBoundingClientRect();
    const x = screenX - parentRect.left + 15;
    const y = screenY - parentRect.top + 15;
    this.tooltip.style.left = `${Math.min(x, parentRect.width - 220)}px`;
    this.tooltip.style.top = `${Math.min(y, parentRect.height - 120)}px`;
  }

  zoomIn() {
    this.scale = Math.min(3.5, this.scale * 1.25);
  }

  zoomOut() {
    this.scale = Math.max(0.3, this.scale * 0.8);
  }

  resetView() {
    this.scale = 1.0;
    this.panX = this.canvas.width / 2;
    this.panY = this.canvas.height / 2;
  }
}
