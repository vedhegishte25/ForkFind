// ── ForkFind Food DNA Chart JavaScript ──

const DNA_COLORS = [
  '#2F5233', // pine green  — Indian
  '#87BFFF', // sky blue    — Italian
  '#DCC9A9', // sand        — Asian
  '#5B4636', // bark brown  — Street Food
  '#4a9e6b', // mid green   — Fast Food
  '#e07b39', // orange      — Desserts
  '#9b59b6', // purple      — Cafe
  '#e74c3c', // red         — Continental
  '#f39c12', // amber       — Seafood
  '#1abc9c', // teal        — Other
]


// ── Draw Donut Chart ──
function drawDonutChart(canvasId, dnaData) {
  const canvas = document.getElementById(canvasId)
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const size = canvas.width
  const cx = size / 2
  const cy = size / 2
  const radius = size * 0.38
  const innerRadius = size * 0.24
  const gap = 0.03

  // clear canvas
  ctx.clearRect(0, 0, size, size)

  const entries = Object.entries(dnaData)
  const total = entries.reduce((sum, [, val]) => sum + val, 0)

  if (total === 0) {
    drawEmptyDonut(ctx, cx, cy, radius, innerRadius)
    return
  }

  let startAngle = -Math.PI / 2

  entries.forEach(([cuisine, value], index) => {
    const sliceAngle = (value / total) * Math.PI * 2
    const endAngle = startAngle + sliceAngle - gap

    // draw slice
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.arc(cx, cy, radius, startAngle, endAngle)
    ctx.arc(cx, cy, innerRadius, endAngle, startAngle, true)
    ctx.closePath()
    ctx.fillStyle = DNA_COLORS[index % DNA_COLORS.length]
    ctx.fill()

    startAngle += sliceAngle
  })

  // draw center hole (white)
  ctx.beginPath()
  ctx.arc(cx, cy, innerRadius - 2, 0, Math.PI * 2)
  ctx.fillStyle = '#ffffff'
  ctx.fill()
}


// ── Draw Empty Donut ──
function drawEmptyDonut(ctx, cx, cy, radius, innerRadius) {
  ctx.beginPath()
  ctx.arc(cx, cy, radius, 0, Math.PI * 2)
  ctx.arc(cx, cy, innerRadius, 0, Math.PI * 2, true)
  ctx.fillStyle = '#e8e0d4'
  ctx.fill()
}


// ── Render DNA Legend ──
function renderDNALegend(containerId, dnaData) {
  const container = document.getElementById(containerId)
  if (!container) return

  const entries = Object.entries(dnaData)
    .sort((a, b) => b[1] - a[1])

  container.innerHTML = entries.map(([cuisine, pct], index) => `
    <div class="dna-legend-row">
      <div class="dna-legend-top">
        <div class="dna-legend-name">
          <div class="dna-color-dot"
               style="background:${DNA_COLORS[index % DNA_COLORS.length]}">
          </div>
          ${cuisine}
        </div>
        <div class="dna-legend-pct">${pct}%</div>
      </div>
      <div class="dna-bar-track">
        <div class="dna-bar-fill"
             style="width:0%;background:${DNA_COLORS[index % DNA_COLORS.length]}"
             data-target="${pct}">
        </div>
      </div>
    </div>
  `).join('')

  // animate bars after render
  setTimeout(() => {
    container.querySelectorAll('.dna-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.target + '%'
    })
  }, 100)
}


// ── Draw Taste Radar Chart ──
function drawRadarChart(canvasId, tasteData) {
  const canvas = document.getElementById(canvasId)
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const size = canvas.width
  const cx = size / 2
  const cy = size / 2
  const maxRadius = size * 0.38
  const levels = 4

  const labels = Object.keys(tasteData)
  const values = Object.values(tasteData)
  const maxVal = 10
  const count = labels.length

  if (count < 3) return

  ctx.clearRect(0, 0, size, size)

  // draw grid circles
  for (let i = 1; i <= levels; i++) {
    const r = (maxRadius / levels) * i
    ctx.beginPath()
    ctx.arc(cx, cy, r, 0, Math.PI * 2)
    ctx.strokeStyle = '#e0d5c5'
    ctx.lineWidth = 1
    ctx.stroke()
  }

  // draw axis lines
  labels.forEach((_, i) => {
    const angle = (i / count) * Math.PI * 2 - Math.PI / 2
    const x = cx + maxRadius * Math.cos(angle)
    const y = cy + maxRadius * Math.sin(angle)
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(x, y)
    ctx.strokeStyle = '#e0d5c5'
    ctx.lineWidth = 1
    ctx.stroke()
  })

  // draw data polygon
  ctx.beginPath()
  values.forEach((val, i) => {
    const angle = (i / count) * Math.PI * 2 - Math.PI / 2
    const r = (val / maxVal) * maxRadius
    const x = cx + r * Math.cos(angle)
    const y = cy + r * Math.sin(angle)
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.closePath()
  ctx.fillStyle = 'rgba(47,82,51,0.2)'
  ctx.fill()
  ctx.strokeStyle = '#2F5233'
  ctx.lineWidth = 2
  ctx.stroke()

  // draw labels
  ctx.fillStyle = '#4a4a4a'
  ctx.font = `${size * 0.065}px Inter, sans-serif`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  labels.forEach((label, i) => {
    const angle = (i / count) * Math.PI * 2 - Math.PI / 2
    const r = maxRadius + size * 0.1
    const x = cx + r * Math.cos(angle)
    const y = cy + r * Math.sin(angle)
    ctx.fillText(label, x, y)
  })

  // draw data points
  values.forEach((val, i) => {
    const angle = (i / count) * Math.PI * 2 - Math.PI / 2
    const r = (val / maxVal) * maxRadius
    const x = cx + r * Math.cos(angle)
    const y = cy + r * Math.sin(angle)
    ctx.beginPath()
    ctx.arc(x, y, size * 0.025, 0, Math.PI * 2)
    ctx.fillStyle = '#2F5233'
    ctx.fill()
  })
}


// ── Render Insights ──
function renderInsights(containerId, insights) {
  const container = document.getElementById(containerId)
  if (!container) return

  const icons = ['🎯', '🌍', '🌶️', '🍰', '☕']

  container.innerHTML = insights.map((insight, i) => `
    <div class="insight-card">
      <span class="insight-icon">${icons[i % icons.length]}</span>
      <span class="insight-text">${insight}</span>
    </div>
  `).join('')
}


// ── Animate progress rings ──
function animateProgressRings() {
  document.querySelectorAll('.progress-ring-fill').forEach(ring => {
    const pct = parseFloat(ring.dataset.percent || 0)
    const radius = parseFloat(ring.getAttribute('r') || 30)
    const circumference = 2 * Math.PI * radius

    ring.style.strokeDasharray = circumference
    ring.style.strokeDashoffset = circumference

    setTimeout(() => {
      const offset = circumference - (pct / 100) * circumference
      ring.style.strokeDashoffset = offset
    }, 300)
  })
}


// ── Init on page load ──
document.addEventListener('DOMContentLoaded', () => {

  // get DNA data from page
  const dnaDataEl = document.getElementById('dna-data')
  if (dnaDataEl) {
    try {
      const dnaData = JSON.parse(dnaDataEl.textContent)

      // draw donut
      drawDonutChart('dna-donut-canvas', dnaData)

      // render legend
      renderDNALegend('dna-legend-container', dnaData)

      // update center label with top cuisine
      const entries = Object.entries(dnaData).sort((a, b) => b[1] - a[1])
      if (entries.length > 0) {
        const centerVal = document.getElementById('donut-center-value')
        const centerLabel = document.getElementById('donut-center-label')
        if (centerVal) centerVal.textContent = entries[0][0]
        if (centerLabel) centerLabel.textContent = `${entries[0][1]}%`
      }

    } catch (e) {
      console.error('DNA data parse error', e)
    }
  }

  // get taste data for radar
  const tasteDataEl = document.getElementById('taste-data')
  if (tasteDataEl) {
    try {
      const tasteData = JSON.parse(tasteDataEl.textContent)
      drawRadarChart('taste-radar-canvas', tasteData)
    } catch (e) {
      console.error('Taste data parse error', e)
    }
  }

  // get insights
  const insightsEl = document.getElementById('insights-data')
  if (insightsEl) {
    try {
      const insights = JSON.parse(insightsEl.textContent)
      renderInsights('insights-container', insights)
    } catch (e) {
      console.error('Insights parse error', e)
    }
  }

  // animate progress rings
  animateProgressRings()

  // redraw on window resize
  window.addEventListener('resize', debounce(() => {
    const dnaDataEl = document.getElementById('dna-data')
    if (dnaDataEl) {
      try {
        const dnaData = JSON.parse(dnaDataEl.textContent)
        drawDonutChart('dna-donut-canvas', dnaData)
      } catch (e) {}
    }
  }, 300))

})