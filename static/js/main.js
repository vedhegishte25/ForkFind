// ── ForkFind Global JavaScript ──

// ── Toast Notifications ──
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container')
  if (!container) {
    container = document.createElement('div')
    container.className = 'toast-container'
    document.body.appendChild(container)
  }

  const toast = document.createElement('div')
  toast.className = `toast ${type}`
  toast.textContent = message
  container.appendChild(toast)

  setTimeout(() => {
    toast.style.animation = 'slideIn 0.3s ease reverse'
    setTimeout(() => toast.remove(), 300)
  }, 3000)
}


// ── Fetch Wrapper ──
async function apiFetch(url, options = {}) {
  try {
    const defaults = {
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin'
    }

    const config = {
      ...defaults,
      ...options,
      headers: { ...defaults.headers, ...options.headers }
    }

    const response = await fetch(url, config)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Something went wrong')
    }

    return data

  } catch (error) {
    showToast(error.message, 'error')
    throw error
  }
}


// ── Get User Location ──
function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'))
      return
    }

    navigator.geolocation.getCurrentPosition(
      position => resolve({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      }),
      error => reject(error),
      { timeout: 8000 }
    )
  })
}


// ── Format Price Level ──
function formatPriceLevel(level) {
  const symbols = ['', '₹', '₹₹', '₹₹₹', '₹₹₹₹']
  return symbols[level] || '₹₹'
}


// ── Format Rating Stars ──
function formatStars(rating) {
  const full  = Math.floor(rating)
  const half  = rating % 1 >= 0.5 ? 1 : 0
  const empty = 5 - full - half

  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty)
}


// ── Format Distance ──
function formatDistance(lat1, lon1, lat2, lon2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  const d = R * c

  if (d < 1) return `${Math.round(d * 1000)}m away`
  return `${d.toFixed(1)}km away`
}


// ── Render Restaurant Card ──
function renderRestaurantCard(restaurant, userLat, userLon) {
  const vibes = restaurant.vibe_tags || []
  const vibeHtml = vibes.slice(0, 3).map(v =>
    `<span class="vibe-tag">${v}</span>`
  ).join('')

  const distance = (userLat && userLon && restaurant.latitude && restaurant.longitude)
    ? formatDistance(userLat, userLon, restaurant.latitude, restaurant.longitude)
    : ''

  const imgHtml = restaurant.photo_url
    ? `<img src="${restaurant.photo_url}" alt="${restaurant.name}" loading="lazy"/>`
    : `<div style="font-size:3rem">🍽️</div>`

  return `
    <div class="restaurant-card"
         onclick="window.location.href='/restaurants/${restaurant.place_id}'">
      <div class="restaurant-card-img">${imgHtml}</div>
      <div class="restaurant-card-body">
        <div class="restaurant-card-name">${restaurant.name}</div>
        <div class="restaurant-card-meta">
          <span class="restaurant-card-rating">
            ★ ${restaurant.rating || restaurant.average_rating || 'N/A'}
          </span>
          <span>${restaurant.total_reviews || restaurant.total_ratings || 0} reviews</span>
          <span class="restaurant-card-price">
            ${formatPriceLevel(restaurant.price_level)}
          </span>
          ${distance ? `<span>${distance}</span>` : ''}
          ${restaurant.open_now === true
            ? '<span class="open-pill open">● Open</span>'
            : restaurant.open_now === false
            ? '<span class="open-pill closed">● Closed</span>'
            : ''}
        </div>
        <div class="restaurant-card-vibes">${vibeHtml}</div>
      </div>
    </div>
  `
}


// ── Render AI Message Banner ──
function renderAIMessage(message) {
  return `
    <div style="
      background: var(--pine-green);
      color: var(--cream);
      padding: 1rem 1.25rem;
      border-radius: var(--radius-lg);
      margin-bottom: 1.5rem;
      font-size: 0.9rem;
      line-height: 1.6;
    ">
      <span style="margin-right:0.5rem">🤖</span>${message}
    </div>
  `
}


// ── Show Loading State ──
function showLoading(containerId, message = 'Finding perfect places for you...') {
  const container = document.getElementById(containerId)
  if (!container) return

  container.innerHTML = `
    <div class="ai-loading">
      <div class="ai-dots">
        <div class="ai-dot"></div>
        <div class="ai-dot"></div>
        <div class="ai-dot"></div>
      </div>
      <div class="ai-loading-text">${message}</div>
    </div>
  `
}


// ── Copy to Clipboard ──
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard!', 'success')
  }).catch(() => {
    showToast('Could not copy', 'error')
  })
}


// ── Debounce ──
function debounce(fn, delay = 300) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}


// ── Active Nav Link ──
document.addEventListener('DOMContentLoaded', () => {
  const currentPath = window.location.pathname
  document.querySelectorAll('.navbar-nav a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active')
    }
  })
})


// ── Flash Message Auto Dismiss ──
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash-message').forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0'
      msg.style.transition = 'opacity 0.4s ease'
      setTimeout(() => msg.remove(), 400)
    }, 4000)
  })
})