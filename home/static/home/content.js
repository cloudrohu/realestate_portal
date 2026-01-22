var swiper = new Swiper(".mySwiper", {
slidesPerView: 1,
spaceBetween: 20,
loop: true,
autoplay: {
    delay: 3000, // Auto slide every 3 seconds
    disableOnInteraction: false,
    pauseOnMouseEnter: true, // pause on hover
},
pagination: {
    el: ".swiper-pagination",
    clickable: true,
},
navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
},
breakpoints: {  
    640: { slidesPerView: 1.2 },
    768: { slidesPerView: 2 },
    1024: { slidesPerView: 3 },
},
});

// Swiper Init
function initSwiper() {
document.querySelectorAll(".mySwiper").forEach(swiperEl => {
    new Swiper(swiperEl, {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    pagination: {
        el: swiperEl.querySelector(".swiper-pagination"),
        clickable: true,
    },
    navigation: {
        nextEl: swiperEl.querySelector(".swiper-button-next"),
        prevEl: swiperEl.querySelector(".swiper-button-prev"),
    },
    breakpoints: {
        768: { slidesPerView: 2 },
        1024: { slidesPerView: 3 },
    },
    });
});
}
initSwiper();

// Tabs functionality
document.querySelectorAll(".tab-btn").forEach(btn => {
btn.addEventListener("click", function () {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    this.classList.add("active");

    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.add("hidden"));
    document.getElementById(this.dataset.tab).classList.remove("hidden");
});
});

new Swiper(".blogSwiper", { slidesPerView: 1, spaceBetween: 18, pagination: { el: ".swiper-pagination", clickable: true } });

var loanPartnerSwiper = new Swiper(".loanPartnerSwiper", {
slidesPerView: 2,
spaceBetween: 20,
loop: true,
autoplay: {
    delay: 2500,
    disableOnInteraction: false,
},
breakpoints: {
    640: { slidesPerView: 3 },
    768: { slidesPerView: 4 },
    1024: { slidesPerView: 5 },
},
});
document.addEventListener("DOMContentLoaded", function () {
  new Swiper(".loanPartnerSwiper", {
    loop: true,
    speed: 6000,
    spaceBetween: 22,

    // ✅ Continuous Smooth Auto Scroll
    freeMode: true,
    freeModeMomentum: false,

    autoplay: {
      delay: 0,
      disableOnInteraction: false,
      pauseOnMouseEnter: true
    },

    grabCursor: true,
    centeredSlides: false,

    // ✅ Wider Layout (Less slides => wider cards)
    breakpoints: {
      320:  { slidesPerView: 1.2 },
      480:  { slidesPerView: 1.6 },
      640:  { slidesPerView: 2.3 },
      768:  { slidesPerView: 3 },
      1024: { slidesPerView: 3.8 },
      1280: { slidesPerView: 4.5 }
    }
  });
});
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("commonModal");
  const title = document.getElementById("modalTitle");

  modal.addEventListener("show.bs.modal", function (event) {
    const btn = event.relatedTarget;
    title.innerText = btn.getAttribute("data-modal-title");
  });
});
  var swiper = new Swiper(".mySwiper", {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    pagination: { el: ".swiper-pagination", clickable: true },
    navigation: { nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev" },
    breakpoints: { 768: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } }
  });