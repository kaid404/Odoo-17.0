document.addEventListener("DOMContentLoaded", () => {
  const themeToggleBtn = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("theme") || "light-theme";
  document.body.className = currentTheme;

  themeToggleBtn.addEventListener("click", () => {
    if (document.body.classList.contains("light-theme")) {
      document.body.className = "dark-theme";
      localStorage.setItem("theme", "dark-theme");
    } else {
      document.body.className = "light-theme";
      localStorage.setItem("theme", "light-theme");
    }
  });
document.querySelector('.edit-profile-btn').addEventListener('click', function() {
    alert('Edit profile feature is under development!');
});

});

let menuicn = document.querySelector(".menuicn");
let nav = document.querySelector(".navcontainer");

menuicn.addEventListener("click", () => {
  nav.classList.toggle("navclose");
});

function toggleFullscreen() {
    const elem = document.documentElement;
    const icon = document.getElementById("fullscreen-toggle");

    if (!document.fullscreenElement) {
        elem.requestFullscreen().then(() => {
            icon.classList.remove("fa-expand");
            icon.classList.add("fa-compress");
        }).catch((err) => {
            alert(`Error attempting to enable full-screen mode: ${err.message}`);
        });
    } else {
        document.exitFullscreen().then(() => {
            icon.classList.remove("fa-compress");
            icon.classList.add("fa-expand");
        }).catch((err) => {
            alert(`Error attempting to exit full-screen mode: ${err.message}`);
        });
    }
}
const slider = document.querySelector('.slider');
const slides = document.querySelectorAll('.slide');
const arrowLeft = document.querySelector('.arrow-left');
const arrowRight = document.querySelector('.arrow-right');
let currentIndex = 0;
const totalSlides = slides.length;

function updateSliderPosition() {
    const slideWidth = slides[0].clientWidth;
    slider.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
}

arrowLeft.addEventListener('click', () => {
    currentIndex = (currentIndex === 0) ? totalSlides - 4 : currentIndex - 1;
    updateSliderPosition();
});

arrowRight.addEventListener('click', () => {
    currentIndex = (currentIndex === totalSlides - 4) ? 0 : currentIndex + 1;
    updateSliderPosition();
});


