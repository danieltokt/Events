// Bird mascot animation controller
class BirdMascot {
  constructor() {
    this.bird = null
    this.leftWing = null
    this.rightWing = null
    this.isAnimating = false
    this.init()
  }

  init() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.setup())
    } else {
      this.setup()
    }
  }

  setup() {
    this.bird = document.getElementById("mascotBird")
    this.leftWing = document.getElementById("leftWing")
    this.rightWing = document.getElementById("rightWing")

    if (!this.bird) return

    this.bird.addEventListener("click", () => {
      this.wave()
    })

    this.startIdleAnimations()
  }

  wave() {
    if (this.isAnimating) return
    this.playAnimation("wave", 600)
  }

  happy() {
    if (this.isAnimating) return
    this.playAnimation("happy", 800)
  }

  sad() {
    if (this.isAnimating) return
    this.playAnimation("sad", 800)
  }

  angry() {
    if (this.isAnimating) return
    this.playAnimation("angry", 800)
  }

  error() {
    if (this.isAnimating) return
    this.angry()
  }

  loading() {
    if (!this.bird) return
    this.bird.classList.add("loading")
  }

  stopLoading() {
    if (!this.bird) return
    this.bird.classList.remove("loading")
  }

  flyAway() {
    if (!this.bird) return

    this.isAnimating = true

    // First show happy animation
    this.bird.classList.add("happy")

    setTimeout(() => {
      this.bird.classList.remove("happy")

      // Start fly away animation with wing flapping and tail swaying
      this.bird.classList.add("fly-away")

      // Listen for animation end event for precise timing
      const handleAnimationEnd = (e) => {
        if (e.animationName === "flyAway") {
          console.log("[v0] Bird fly away animation completed, redirecting...")
          this.bird.removeEventListener("animationend", handleAnimationEnd)
          window.location.href = "dashboard.html"
        }
      }

      this.bird.addEventListener("animationend", handleAnimationEnd)

      // Fallback timeout in case animationend doesn't fire (6s animation + 100ms buffer)
      setTimeout(() => {
        console.log("[v0] Fallback redirect triggered")
        window.location.href = "dashboard.html"
      }, 6100)
    }, 600)
  }

  playAnimation(animationName, duration) {
    if (!this.bird) return

    this.isAnimating = true
    this.bird.classList.add(animationName)

    setTimeout(() => {
      this.bird.classList.remove(animationName)
      this.isAnimating = false
    }, duration)
  }

  startIdleAnimations() {
    setInterval(() => {
      if (!this.isAnimating && Math.random() > 0.6) {
        this.wave()
      }
    }, 15000)
  }
}

// Create global instance
const birdMascot = new BirdMascot()

// Export for use in other scripts
window.birdMascot = birdMascot
