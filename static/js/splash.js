// ── ForkFind Splash Screen JavaScript ──

document.addEventListener('DOMContentLoaded', () => {

  const splash = document.getElementById('splash-screen')
  const getStartedBtn = document.getElementById('get-started-btn')

  // ── Auto dismiss splash after 3.5 seconds ──
  // only if user is already logged in
  const isLoggedIn = document.body.dataset.loggedIn === 'true'

  if (isLoggedIn) {
    setTimeout(() => {
      dismissSplash('/home')
    }, 2500)
  }

  // ── Get Started button ──
  if (getStartedBtn) {
    getStartedBtn.addEventListener('click', () => {
      const destination = isLoggedIn ? '/home' : '/auth/register'
      dismissSplash(destination)
    })
  }

  // ── Dismiss splash with animation ──
  function dismissSplash(destination) {
    if (!splash) return

    splash.classList.add('hidden')

    setTimeout(() => {
      window.location.href = destination
    }, 600)
  }

  // ── Animate floating dots ──
  animateDots()

  function animateDots() {
    const dots = document.querySelectorAll('.dot')
    dots.forEach((dot, index) => {
      // randomise starting position slightly
      const randomX = (Math.random() - 0.5) * 20
      dot.style.transform = `translateX(${randomX}px)`
    })
  }

  // ── Keyboard shortcut — press Enter to continue ──
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      const destination = isLoggedIn ? '/home' : '/auth/register'
      dismissSplash(destination)
    }
  })

  // ── Preload home page in background ──
  function preloadNextPage() {
    const link = document.createElement('link')
    link.rel = 'prefetch'
    link.href = isLoggedIn ? '/home' : '/auth/register'
    document.head.appendChild(link)
  }

  // preload after splash animation completes
  setTimeout(preloadNextPage, 1500)

})