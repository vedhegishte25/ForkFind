// ── ForkFind Group Decision Solver JavaScript ──

let sessionCode = null
let currentStep = 'start'
let pollInterval = null

document.addEventListener('DOMContentLoaded', () => {

  // ── Step navigation ──
  showStep('start')

  // ── Create session button ──
  const createBtn = document.getElementById('create-session-btn')
  if (createBtn) {
    createBtn.addEventListener('click', createSession)
  }

  // ── Join session button ──
  const joinBtn = document.getElementById('join-session-btn')
  if (joinBtn) {
    joinBtn.addEventListener('click', joinSession)
  }

  // ── Submit preferences button ──
  const prefsBtn = document.getElementById('submit-prefs-btn')
  if (prefsBtn) {
    prefsBtn.addEventListener('click', submitPreferences)
  }

  // ── Solve button ──
  const solveBtn = document.getElementById('solve-btn')
  if (solveBtn) {
    solveBtn.addEventListener('click', solveGroup)
  }

  // ── Copy session code ──
  const copyBtn = document.getElementById('copy-code-btn')
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      copyToClipboard(sessionCode)
    })
  }

  // ── Vibe chips in preferences form ──
  document.querySelectorAll('.vibe-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected')
    })
  })

  // ── Cuisine chips ──
  document.querySelectorAll('.cuisine-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected')
    })
  })


  // ── Create a new group session ──
  async function createSession() {
    try {
      createBtn.disabled = true
      createBtn.textContent = 'Creating...'

      const data = await apiFetch('/group/create', {
        method: 'POST'
      })

      sessionCode = data.session_code

      // show session code
      const codeDisplay = document.getElementById('session-code-display')
      if (codeDisplay) {
        codeDisplay.textContent = sessionCode
      }

      showStep('session-created')
      showToast('Session created! Share the code with friends', 'success')

      // start polling for members
      startPolling()

    } catch (error) {
      createBtn.disabled = false
      createBtn.textContent = 'Create Session'
    }
  }


  // ── Join an existing session ──
  async function joinSession() {
    const codeInput = document.getElementById('join-code-input')
    if (!codeInput) return

    const code = codeInput.value.trim().toUpperCase()
    if (!code || code.length !== 6) {
      showToast('Please enter a valid 6-character code', 'error')
      return
    }

    try {
      joinBtn.disabled = true
      joinBtn.textContent = 'Joining...'

      const data = await apiFetch('/group/join', {
        method: 'POST',
        body: JSON.stringify({ session_code: code })
      })

      sessionCode = data.session_code

      // show session code
      const codeDisplay = document.getElementById('session-code-display')
      if (codeDisplay) {
        codeDisplay.textContent = sessionCode
      }

      updateMembersCount(data.members.length)
      showStep('session-created')
      showToast(`Joined session ${sessionCode}`, 'success')

      // start polling
      startPolling()

    } catch (error) {
      joinBtn.disabled = false
      joinBtn.textContent = 'Join Session'
    }
  }


  // ── Submit preferences ──
  async function submitPreferences() {
    if (!sessionCode) {
      showToast('No active session', 'error')
      return
    }

    // gather selected vibes
    const selectedVibes = []
    document.querySelectorAll('.vibe-chip.selected').forEach(chip => {
      selectedVibes.push(chip.dataset.vibe)
    })

    // gather selected cuisines
    const selectedCuisines = []
    document.querySelectorAll('.cuisine-chip.selected').forEach(chip => {
      selectedCuisines.push(chip.dataset.cuisine)
    })

    const budget = document.getElementById('budget-input')?.value || 500
    const distance = document.getElementById('distance-input')?.value || 5
    const dietary = document.getElementById('dietary-select')?.value || 'non-veg'

    try {
      prefsBtn.disabled = true
      prefsBtn.textContent = 'Saving...'

      const data = await apiFetch('/group/preferences', {
        method: 'POST',
        body: JSON.stringify({
          session_code: sessionCode,
          budget: parseInt(budget),
          cuisines: selectedCuisines,
          distance: parseInt(distance),
          dietary: dietary,
          vibes: selectedVibes
        })
      })

      showToast('Preferences saved!', 'success')
      showStep('waiting-for-others')

      updatePrefsCount(data.members_submitted)

      // keep polling
      startPolling()

    } catch (error) {
      prefsBtn.disabled = false
      prefsBtn.textContent = 'Save My Preferences'
    }
  }


  // ── Solve group decision ──
  async function solveGroup() {
    if (!sessionCode) return

    try {
      solveBtn.disabled = true
      solveBtn.textContent = 'Finding perfect match...'

      showLoading('results-container', 'AI is finding the perfect place for everyone...')

      const city = document.body.dataset.city || 'Thane'
      let latitude = null
      let longitude = null

      try {
        const loc = await getUserLocation()
        latitude = loc.latitude
        longitude = loc.longitude
      } catch (e) {
        // use city name
      }

      const data = await apiFetch('/group/solve', {
        method: 'POST',
        body: JSON.stringify({
          session_code: sessionCode,
          city: city,
          latitude: latitude,
          longitude: longitude
        })
      })

      stopPolling()
      renderGroupResult(data)
      showStep('results')

    } catch (error) {
      solveBtn.disabled = false
      solveBtn.textContent = 'Find Our Match'
    }
  }


  // ── Render group results ──
  function renderGroupResult(data) {
    const container = document.getElementById('results-container')
    if (!container) return

    let html = ''

    // AI message
    if (data.ai_message) {
      html += renderAIMessage(data.ai_message)
    }

    // summary row
    html += `
      <div style="display:grid;grid-template-columns:repeat(3,1fr);
                  gap:1rem;margin-bottom:1.5rem">
        <div class="stat-card">
          <div class="stat-value" style="font-size:1.25rem">
            ${data.budget_range || '₹300-600'}
          </div>
          <div class="stat-label">Budget</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="font-size:1.25rem">
            ${(data.common_cuisines || []).join(', ') || 'Mixed'}
          </div>
          <div class="stat-label">Cuisines</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="font-size:1.25rem">
            ${(data.recommended_vibes || []).join(', ') || 'Casual'}
          </div>
          <div class="stat-label">Vibe</div>
        </div>
      </div>
    `

    // dietary note
    if (data.dietary_notes) {
      html += `
        <div class="insight-card" style="margin-bottom:1.25rem">
          <span class="insight-icon">🥗</span>
          <span class="insight-text">${data.dietary_notes}</span>
        </div>
      `
    }

    // restaurants
    if (data.restaurants && data.restaurants.length > 0) {
      html += `
        <div style="font-size:0.8rem;color:var(--text-muted);
                    margin-bottom:1rem;font-weight:600">
          ${data.restaurants.length} PLACES THAT WORK FOR EVERYONE
        </div>
        <div class="grid-3">
          ${data.restaurants.map(r => renderRestaurantCard(r)).join('')}
        </div>
      `
    } else {
      html += `
        <div class="empty-state">
          <div class="empty-icon">🤔</div>
          <h3>No perfect match found</h3>
          <p>Try adjusting your preferences</p>
        </div>
      `
    }

    container.innerHTML = html
  }


  // ── Poll session status ──
  function startPolling() {
    if (pollInterval) return

    pollInterval = setInterval(async () => {
      if (!sessionCode) return

      try {
        const data = await apiFetch(`/group/status/${sessionCode}`)
        updateMembersCount(data.members_count)
        updatePrefsCount(data.preferences_submitted)

        // enable solve button if 2+ submitted
        const solveBtn = document.getElementById('solve-btn')
        if (solveBtn && data.preferences_submitted >= 2) {
          solveBtn.disabled = false
          solveBtn.style.opacity = '1'
        }

      } catch (error) {
        // silently fail polling
      }
    }, 3000)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }


  // ── Update member count display ──
  function updateMembersCount(count) {
    const el = document.getElementById('members-count')
    if (el) el.textContent = count
  }

  function updatePrefsCount(count) {
    const el = document.getElementById('prefs-count')
    if (el) el.textContent = count
  }


  // ── Show a specific step ──
  function showStep(stepName) {
    currentStep = stepName

    document.querySelectorAll('.group-step').forEach(step => {
      step.style.display = 'none'
    })

    const activeStep = document.getElementById(`step-${stepName}`)
    if (activeStep) {
      activeStep.style.display = 'block'
      activeStep.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }


  // ── Clean up on page leave ──
  window.addEventListener('beforeunload', () => {
    stopPolling()
  })

})