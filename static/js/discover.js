// ── ForkFind Discover Page JavaScript ──

let selectedMood = null
let userLocation = null

document.addEventListener('DOMContentLoaded', () => {

  // ── Try get user location on load ──
  tryGetLocation()

  // ── Mood card selection ──
  document.querySelectorAll('.mood-card').forEach(card => {
    card.addEventListener('click', () => {
      // deselect all
      document.querySelectorAll('.mood-card').forEach(c => {
        c.classList.remove('selected')
      })

      // select clicked
      card.classList.add('selected')
      selectedMood = {
        id: card.dataset.moodId,
        label: card.dataset.moodLabel
      }

      // show find button
      const findBtn = document.getElementById('find-btn')
      if (findBtn) {
        findBtn.style.opacity = '1'
        findBtn.style.pointerEvents = 'auto'
        findBtn.style.transform = 'translateY(0)'
      }
    })
  })


  // ── Find button click ──
  const findBtn = document.getElementById('find-btn')
  if (findBtn) {
    findBtn.addEventListener('click', () => {
      if (!selectedMood) {
        showToast('Please select a mood first', 'error')
        return
      }
      fetchRecommendations()
    })
  }


  // ── Fetch recommendations from AI ──
  async function fetchRecommendations() {
    const resultsSection = document.getElementById('results-section')
    const resultsContainer = document.getElementById('results-container')

    if (!resultsSection || !resultsContainer) return

    // show results section
    resultsSection.style.display = 'block'
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' })

    // show loading
    showLoading('results-container', `Finding ${selectedMood.label} spots for you...`)

    try {
      const city = document.getElementById('city-input')?.value ||
                   document.body.dataset.city || 'Thane'

      const payload = {
        mood_id: selectedMood.id,
        mood_label: selectedMood.label,
        city: city,
        latitude: userLocation?.latitude || null,
        longitude: userLocation?.longitude || null
      }

      const data = await apiFetch('/discover/mood', {
        method: 'POST',
        body: JSON.stringify(payload)
      })

      renderResults(data)

    } catch (error) {
      resultsContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">😕</div>
          <h3>Could not fetch recommendations</h3>
          <p>Please try again in a moment</p>
        </div>
      `
    }
  }


  // ── Render results ──
  function renderResults(data) {
    const container = document.getElementById('results-container')
    if (!container) return

    let html = ''

    // AI message
    if (data.ai_message) {
      html += renderAIMessage(data.ai_message)
    }

    // cuisine suggestions pills
    if (data.cuisine_suggestions && data.cuisine_suggestions.length > 0) {
      html += `
        <div style="margin-bottom:1.25rem">
          <div style="font-size:0.8rem;color:var(--text-muted);
                      margin-bottom:0.5rem;font-weight:600;">
            SUGGESTED CUISINES
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem">
            ${data.cuisine_suggestions.map(c => `
              <span class="vibe-chip selected">${c}</span>
            `).join('')}
          </div>
        </div>
      `
    }

    // restaurant results
    if (data.restaurants && data.restaurants.length > 0) {
      html += `
        <div style="font-size:0.8rem;color:var(--text-muted);
                    margin-bottom:1rem;font-weight:600;">
          ${data.restaurants.length} PLACES FOUND
        </div>
        <div class="grid-3">
          ${data.restaurants.map(r =>
            renderRestaurantCard(
              r,
              userLocation?.latitude,
              userLocation?.longitude
            )
          ).join('')}
        </div>
      `
    } else {
      html += `
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <h3>No places found</h3>
          <p>Try a different mood or expand your search area</p>
        </div>
      `
    }

    container.innerHTML = html
  }


  // ── Try get location ──
  async function tryGetLocation() {
    try {
      userLocation = await getUserLocation()

      // show location indicator
      const locIndicator = document.getElementById('location-indicator')
      if (locIndicator) {
        locIndicator.textContent = '📍 Using your location'
        locIndicator.style.color = 'var(--pine-green)'
      }

    } catch (error) {
      // silently fail — city name will be used instead
      const locIndicator = document.getElementById('location-indicator')
      if (locIndicator) {
        locIndicator.textContent = '📍 Using city name'
      }
    }
  }


  // ── Context based auto mood suggestion ──
  const contextMood = document.body.dataset.suggestedMood
  if (contextMood) {
    const matchingCard = document.querySelector(
      `.mood-card[data-mood-id="${contextMood}"]`
    )
    if (matchingCard) {
      // subtle highlight but don't auto select
      matchingCard.style.borderColor = 'var(--sky-blue)'
    }
  }

})