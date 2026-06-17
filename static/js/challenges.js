// ── ForkFind Challenges Page JavaScript ──

document.addEventListener('DOMContentLoaded', () => {

  // ── Enroll in challenge ──
  document.querySelectorAll('.enroll-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const challengeId = btn.dataset.challengeId
      if (!challengeId) return

      try {
        btn.disabled = true
        btn.textContent = 'Enrolling...'

        const data = await apiFetch(`/challenges/enroll/${challengeId}`, {
          method: 'POST'
        })

        showToast(`Enrolled in ${data.challenge.name}!`, 'success')

        // replace enroll button with progress display
        const card = btn.closest('.badge-card')
        if (card) {
          btn.style.display = 'none'
          const enrolled = document.createElement('div')
          enrolled.innerHTML = `
            <div class="progress-bar-wrap" style="margin-top:0.75rem">
              <div class="progress-bar-fill" style="width:0%"></div>
            </div>
            <div style="font-size:0.75rem;color:var(--text-muted);
                        margin-top:0.375rem;text-align:center">
              0 / ${data.challenge.target_count}
            </div>
          `
          card.appendChild(enrolled)
        }

      } catch (error) {
        btn.disabled = false
        btn.textContent = 'Start Challenge'
      }
    })
  })


  // ── Check in to a challenge ──
  document.querySelectorAll('.checkin-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const challengeId = btn.dataset.challengeId
      const restaurantId = btn.dataset.restaurantId

      if (!challengeId) return

      // if no restaurant id, show restaurant picker
      if (!restaurantId) {
        showRestaurantPicker(challengeId)
        return
      }

      await doCheckin(challengeId, restaurantId, btn)
    })
  })


  // ── Perform checkin ──
  async function doCheckin(challengeId, restaurantId, btn) {
    try {
      if (btn) {
        btn.disabled = true
        btn.textContent = 'Checking in...'
      }

      const data = await apiFetch('/challenges/checkin', {
        method: 'POST',
        body: JSON.stringify({
          challenge_id: parseInt(challengeId),
          restaurant_id: parseInt(restaurantId)
        })
      })

      if (data.completed) {
        // badge unlock animation
        showBadgeUnlock(data.badge)
        showToast(data.message, 'success')

        // mark challenge card as completed
        const card = document.querySelector(
          `.challenge-card[data-challenge-id="${challengeId}"]`
        )
        if (card) {
          card.classList.add('completed')
          setTimeout(() => location.reload(), 2000)
        }

      } else {
        showToast(data.message, 'success')
        updateChallengeProgress(
          challengeId,
          data.progress.current_count,
          data.progress.target_count,
          data.progress.progress_percent
        )
      }

    } catch (error) {
      if (btn) {
        btn.disabled = false
        btn.textContent = 'Check In'
      }
    }
  }


  // ── Update challenge progress UI ──
  function updateChallengeProgress(challengeId, current, target, percent) {
    const card = document.querySelector(
      `.challenge-card[data-challenge-id="${challengeId}"]`
    )
    if (!card) return

    // update progress bar
    const bar = card.querySelector('.progress-bar-fill')
    if (bar) bar.style.width = `${percent}%`

    // update progress text
    const progressText = card.querySelector('.challenge-current')
    if (progressText) progressText.textContent = current

    // update progress ring
    const ring = card.querySelector('.progress-ring-fill')
    if (ring) {
      const radius = parseFloat(ring.getAttribute('r') || 30)
      const circumference = 2 * Math.PI * radius
      const offset = circumference - (percent / 100) * circumference
      ring.style.strokeDashoffset = offset
    }

    // update ring label
    const ringLabel = card.querySelector('.progress-ring-text')
    if (ringLabel) ringLabel.textContent = `${percent}%`
  }


  // ── Badge unlock animation ──
  function showBadgeUnlock(badgeName) {
    const overlay = document.createElement('div')
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.7);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      animation: fadeIn 0.3s ease;
    `

    overlay.innerHTML = `
      <div style="
        background: var(--cream);
        border-radius: var(--radius-xl);
        padding: 3rem 2.5rem;
        text-align: center;
        max-width: 320px;
        animation: popIn 0.4s cubic-bezier(0.16,1,0.3,1);
      ">
        <div style="font-size:4rem;margin-bottom:1rem">🏆</div>
        <h2 style="color:var(--pine-green);margin-bottom:0.5rem">
          Challenge Complete!
        </h2>
        <p style="color:var(--text-muted);margin-bottom:1.5rem">
          You earned the
        </p>
        <div style="
          background: var(--pine-green);
          color: var(--cream);
          padding: 0.75rem 1.5rem;
          border-radius: var(--radius-xl);
          font-weight:700;
          font-size:1.1rem;
          margin-bottom:1.5rem;
          display:inline-block;
        ">
          ${badgeName}
        </div>
        <p style="font-size:0.8rem;color:var(--text-muted)">
          Keep exploring to unlock more badges
        </p>
      </div>
    `

    document.body.appendChild(overlay)

    // add animations
    const style = document.createElement('style')
    style.textContent = `
      @keyframes fadeIn {
        from { opacity:0 }
        to   { opacity:1 }
      }
      @keyframes popIn {
        from { transform:scale(0.7); opacity:0 }
        to   { transform:scale(1);   opacity:1 }
      }
    `
    document.head.appendChild(style)

    // dismiss on click
    overlay.addEventListener('click', () => {
      overlay.style.opacity = '0'
      overlay.style.transition = 'opacity 0.3s ease'
      setTimeout(() => overlay.remove(), 300)
    })

    // auto dismiss after 4 seconds
    setTimeout(() => {
      if (overlay.parentNode) {
        overlay.style.opacity = '0'
        overlay.style.transition = 'opacity 0.3s ease'
        setTimeout(() => overlay.remove(), 300)
      }
    }, 4000)
  }


  // ── Restaurant picker modal ──
  function showRestaurantPicker(challengeId) {
    const modal = document.createElement('div')
    modal.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.5);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    `

    modal.innerHTML = `
      <div style="
        background: #fff;
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        width: 100%;
        max-width: 400px;
        max-height: 80vh;
        overflow-y: auto;
      ">
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:1rem">
          <h3 style="color:var(--text-primary)">Select Restaurant</h3>
          <button onclick="this.closest('.modal-overlay').remove()"
                  style="background:none;border:none;font-size:1.25rem;
                         cursor:pointer;color:var(--text-muted)">✕</button>
        </div>
        <div style="margin-bottom:1rem">
          <input
            type="text"
            id="restaurant-search"
            placeholder="Search restaurant name..."
            class="form-control"
          />
        </div>
        <div id="restaurant-picker-list">
          <div class="ai-loading">
            <div class="ai-dots">
              <div class="ai-dot"></div>
              <div class="ai-dot"></div>
              <div class="ai-dot"></div>
            </div>
          </div>
        </div>
      </div>
    `

    modal.classList.add('modal-overlay')
    document.body.appendChild(modal)

    // close on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove()
    })

    // load restaurants
    loadRestaurantsForPicker(challengeId, modal)
  }


  // ── Load restaurants for picker ──
  async function loadRestaurantsForPicker(challengeId, modal) {
    try {
      const city = document.body.dataset.city || 'Thane'
      const data = await apiFetch(`/restaurants/?city=${city}`)
      const list = modal.querySelector('#restaurant-picker-list')

      if (!list) return

      if (!data || data.length === 0) {
        list.innerHTML = `
          <div class="empty-state">
            <p>No restaurants found</p>
          </div>
        `
        return
      }

      list.innerHTML = data.map(r => `
        <div style="
          padding: 0.75rem;
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          margin-bottom: 0.5rem;
          cursor: pointer;
          transition: all 0.2s ease;
        "
        onmouseover="this.style.borderColor='var(--pine-green)'"
        onmouseout="this.style.borderColor='var(--border)'"
        onclick="handlePickerSelect(${challengeId}, ${r.id}, this)">
          <div style="font-weight:600;font-size:0.875rem;
                      color:var(--text-primary)">${r.name}</div>
          <div style="font-size:0.75rem;color:var(--text-muted)">
            ${r.cuisine_type || ''} · ★ ${r.average_rating || 'N/A'}
          </div>
        </div>
      `).join('')

      // search filter
      const searchInput = modal.querySelector('#restaurant-search')
      if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
          const query = e.target.value.toLowerCase()
          modal.querySelectorAll('#restaurant-picker-list > div').forEach(item => {
            const name = item.querySelector('div')?.textContent?.toLowerCase() || ''
            item.style.display = name.includes(query) ? 'block' : 'none'
          })
        }, 200))
      }

    } catch (error) {
      const list = modal.querySelector('#restaurant-picker-list')
      if (list) {
        list.innerHTML = `<p style="color:var(--text-muted);
                                    text-align:center;padding:1rem">
          Could not load restaurants
        </p>`
      }
    }
  }


  // ── Handle picker selection (global) ──
  window.handlePickerSelect = async function(challengeId, restaurantId, el) {
    const modal = el.closest('.modal-overlay')
    if (modal) modal.remove()
    await doCheckin(challengeId, restaurantId, null)
  }


  // ── Seed challenges button ──
  const seedBtn = document.getElementById('seed-challenges-btn')
  if (seedBtn) {
    seedBtn.addEventListener('click', async () => {
      try {
        seedBtn.disabled = true
        seedBtn.textContent = 'Seeding...'
        await apiFetch('/challenges/seed', { method: 'POST' })
        showToast('Challenges loaded!', 'success')
        setTimeout(() => location.reload(), 1000)
      } catch (error) {
        seedBtn.disabled = false
        seedBtn.textContent = 'Load Challenges'
      }
    })
  }

})