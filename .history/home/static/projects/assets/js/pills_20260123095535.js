document.addEventListener("DOMContentLoaded", function () {

  /* ---------- RESTORE BHK ---------- */
  const bhkInput = document.getElementById("bhkInput");
  if (bhkInput && bhkInput.value) {
    bhkSelected = bhkInput.value.split(",");

    document.querySelectorAll(".bhk-pill").forEach(btn => {
      if (bhkSelected.includes(btn.dataset.value)) {
        btn.className = activeBhk();
        btn.innerText = "✓ " + btn.dataset.value;
      }
    });
  }

 // 1. Toggle Section Open/Close
  function toggleBhkSection() {
      const body = document.getElementById('bhkBody');
      const arrow = document.getElementById('bhkArrow');
      if (body.classList.contains('hidden')) {
          body.classList.remove('hidden');
          arrow.style.transform = 'rotate(180deg)';
      } else {
          body.classList.add('hidden');
          arrow.style.transform = 'rotate(0deg)';
      }
  }

  // 2. Toggle Selection (Active/Inactive)
  function toggleBhkPill(btn) {
      const value = btn.getAttribute('data-value');
      const input = document.getElementById('bhkInput');
      
      // Input string ko array me convert karein (comma se tod kar)
      let values = input.value ? input.value.split(',').map(v => v.trim()).filter(v => v) : [];

      if (values.includes(value)) {
          // Agar pehle se selected hai, to remove karein
          values = values.filter(v => v !== value);
          // Styling hatayein
          btn.classList.remove('bg-blue-50', 'border-blue-200', 'text-blue-600');
          btn.classList.add('bg-white', 'border-gray-200', 'text-gray-600');
      } else {
          // Agar selected nahi hai, to add karein
          values.push(value);
          // Styling lagayein
          btn.classList.remove('bg-white', 'border-gray-200', 'text-gray-600');
          btn.classList.add('bg-blue-50', 'border-blue-200', 'text-blue-600');
      }

      // Updated array ko wapas string banakar input me dalein
      input.value = values.join(',');
  }

  // 3. Clear All Selection
  function bhkClear() {
      document.getElementById('bhkInput').value = '';
      
      // Saare buttons se styling hata do
      document.querySelectorAll('.bhk-pill').forEach(btn => {
          btn.classList.remove('bg-blue-50', 'border-blue-200', 'text-blue-600');
          btn.classList.add('bg-white', 'border-gray-200', 'text-gray-600');
      });
  }

  // 4. Show More Button
  function showMoreBhk() {
      document.getElementById('bhkMore').classList.remove('hidden');
      document.getElementById('bhkMore').classList.add('flex'); // Add flex logic
      document.getElementById('bhkMoreBtn').classList.add('hidden');
  }

  /* ---------- RESTORE CONSTRUCTION ---------- */
  const csInput = document.getElementById("csInput");
  if (csInput && csInput.value) {
    csSelected = csInput.value.split(",");

    document.querySelectorAll(".cs-pill").forEach(btn => {
      if (csSelected.includes(btn.dataset.value)) {
        btn.className = csActive();
        btn.innerText = "✓ " + btn.dataset.value;
      }
    });
  }

  /* ---------- RESTORE AMENITIES ---------- */
  const amenInput = document.getElementById("amenInput");
  if (amenInput && amenInput.value) {
    amenSelected = amenInput.value.split(",");

    document.querySelectorAll(".amen-pill").forEach(btn => {
      if (amenSelected.includes(btn.dataset.value)) {
        btn.className = amenActive();
        btn.innerText = "✓ " + btn.dataset.value;
      }
    });
  }

  /* ---------- RESTORE FURNISHING ---------- */
  const furInput = document.getElementById("furInput");
  if (furInput && furInput.value) {
    furSelected = furInput.value.split(",");

    document.querySelectorAll(".fur-pill").forEach(btn => {
      if (furSelected.includes(btn.dataset.value)) {
        btn.className = furActive();
        btn.innerText = "✓ " + btn.dataset.value;
      }
    });
  }

  /* ---------- RESTORE RERA ---------- */
  const reraInput = document.getElementById("reraInput");
  if (reraInput && reraInput.value) {
    document.querySelectorAll(".rera-pill").forEach(btn => {
      if (btn.dataset.value === reraInput.value) {
        btn.className = reraActive();
        btn.innerText = "✓ " + btn.dataset.value;
      }
    });
  }

});

let selectedTypes = [];

/* 🔥 Smooth Accordion Toggle */
function toggleTypeProperty() {
  const body = document.getElementById('typeBody');
  const arrow = document.getElementById('typeArrow');

  if (body.classList.contains('max-h-0')) {
    body.classList.remove('max-h-0', 'opacity-0');
    body.classList.add('max-h-[500px]', 'opacity-100');
    arrow.classList.add('rotate-180');
  } else {
    body.classList.add('max-h-0', 'opacity-0');
    body.classList.remove('max-h-[500px]', 'opacity-100');
    arrow.classList.remove('rotate-180');
  }
}

/* Load property types */
function loadPropertyTypes() {
  const category = document.getElementById('categorySelect').value;
  const list = PROPERTY_TYPES[category];
  const container = document.getElementById('typePills');
  const moreBtn = document.getElementById('typeMoreBtn');

  container.innerHTML = '';
  selectedTypes = [];

  list.forEach((type, index) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.dataset.value = type;
    btn.onclick = () => selectType(btn);
    btn.className = baseType();
    btn.innerText = '+ ' + type;

    if (index >= 5) {
      btn.classList.add('hidden');
      btn.dataset.more = "1";
      moreBtn.classList.remove('hidden');
    }

    container.appendChild(btn);
  });

  autoOpen();
}

/* +1 more */
function toggleTypeMore() {
  document.querySelectorAll('[data-more="1"]').forEach(el => {
    el.classList.remove('hidden');
  });
  document.getElementById('typeMoreBtn').classList.add('hidden');
}

/* Select pill */
function selectType(btn) {
  const val = btn.dataset.value;

  if (selectedTypes.includes(val)) {
    selectedTypes = selectedTypes.filter(v => v !== val);
    btn.className = baseType();
    btn.innerText = '+ ' + val;
  } else {
    selectedTypes.push(val);
    btn.className = activeType();
    btn.innerText = '✓ ' + val;
  }

  document.getElementById('propertyTypeInput').value =
    selectedTypes.join(',');
}


/* Styles */
function baseType() {
  return `
    px-4 py-1.5 rounded-full border
    text-sm text-gray-700 bg-white
    hover:bg-gray-100 transition
  `;
}

function activeType() {
  return `
    px-4 py-1.5 rounded-full
    text-sm font-medium
    bg-orange-50 text-orange-600
    border border-orange-300
  `;
}

/* INIT */
document.addEventListener('DOMContentLoaded', loadPropertyTypes);

let bhkSelected = [];

/* accordion */
function toggleBhkSection() {
  const body = document.getElementById("bhkBody");
  const arrow = document.getElementById("bhkArrow");

  body.classList.toggle("hidden");
  arrow.classList.toggle("rotate-180");
}

/* + more */
function showMoreBhk() {
  document.getElementById("bhkMore").classList.remove("hidden");
  document.getElementById("bhkMoreBtn").classList.add("hidden");
}

/* pill select */
function toggleBhkPill(btn) {
  const val = btn.dataset.value;

  if (bhkSelected.includes(val)) {
    bhkSelected = bhkSelected.filter(v => v !== val);
    btn.className = baseBhk();
    btn.innerText = "+ " + val;
  } else {
    bhkSelected.push(val);
    btn.className = activeBhk();
    btn.innerText = "✓ " + val;
  }

  document.getElementById("bhkInput").value =
    bhkSelected.join(",");
}

/* styles */
function baseBhk() {
  return `
    bhk-pill px-4 py-1.5 rounded-full border
    text-sm text-gray-700 bg-white
    hover:bg-gray-100 transition
  `;
}

function activeBhk() {
  return `
    bhk-pill px-4 py-1.5 rounded-full
    text-sm font-medium
    bg-orange-50 text-orange-600
    border border-orange-300
  `;
}

let csSelected = [];

/* accordion */
function csToggle() {
  document.getElementById("csBody").classList.toggle("hidden");
  document.getElementById("csArrow").classList.toggle("rotate-180");
}

/* pill toggle */
function csPill(btn) {
  const val = btn.dataset.value;

  if (csSelected.includes(val)) {
    csSelected = csSelected.filter(v => v !== val);
    btn.className = csBase();
    btn.innerText = "+ " + val;
  } else {
    csSelected.push(val);
    btn.className = csActive();
    btn.innerText = "✓ " + val;
  }

  document.getElementById("csInput").value =
    csSelected.join(",");
}

/* styles */
function csBase() {
  return `
    cs-pill px-4 py-1.5 rounded-full border
    text-sm text-gray-700 bg-white
    hover:bg-gray-100 transition
  `;
}

function csActive() {
  return `
    cs-pill px-4 py-1.5 rounded-full
    text-sm font-medium
    bg-orange-50 text-orange-600
    border border-orange-300
  `;
}

/* init */
document.querySelectorAll(".cs-pill").forEach(b => {
  b.className = csBase();
});
/* accordion */
function locToggle() {
  document.getElementById("locBody").classList.toggle("hidden");
  document.getElementById("locArrow").classList.toggle("rotate-180");
}


/* search */
function filterLocalities() {
  const q = document.getElementById("locSearch").value.toLowerCase();
  document.querySelectorAll(".loc-item").forEach(item => {
    item.style.display =
      item.textContent.toLowerCase().includes(q) ? "flex" : "none";
  });
}
let amenSelected = [];

/* accordion */
function amenToggle() {
  document.getElementById("amenBody").classList.toggle("hidden");
  document.getElementById("amenArrow").classList.toggle("rotate-180");
}

/* pill toggle */
function amenPill(btn) {
  const val = btn.dataset.value;

  if (amenSelected.includes(val)) {
    amenSelected = amenSelected.filter(v => v !== val);
    btn.className = amenBase();
    btn.innerText = "+ " + val;
  } else {
    amenSelected.push(val);
    btn.className = amenActive();
    btn.innerText = "✓ " + val;
  }

  document.getElementById("amenInput").value =
    amenSelected.join(",");
}

/* show more */
function amenShowMore() {
  document.getElementById("amenMore").classList.remove("hidden");
  document.getElementById("amenMoreBtn").classList.add("hidden");
}

/* clear */
function amenClear() {
  amenSelected = [];
  document.getElementById("amenInput").value = "";
  document.querySelectorAll(".amen-pill").forEach(btn => {
    btn.className = amenBase();
    btn.innerText = "+ " + btn.dataset.value;
  });
}

/* styles */
function amenBase() {
  return `
    amen-pill px-4 py-1.5 rounded-full border
    text-sm text-gray-700 bg-white
    hover:bg-gray-100 transition
  `;
}

function amenActive() {
  return `
    amen-pill px-4 py-1.5 rounded-full
    text-sm font-medium
    bg-orange-50 text-orange-600
    border border-orange-300
  `;
}

/* init */
document.querySelectorAll(".amen-pill").forEach(btn => {
  btn.className = amenBase();
});
let furSelected = [];

/* accordion */
function furToggle() {
  document.getElementById("furBody").classList.toggle("hidden");
  document.getElementById("furArrow").classList.toggle("rotate-180");
}

/* pill toggle */
function furPill(btn) {
  const val = btn.dataset.value;

  if (furSelected.includes(val)) {
    furSelected = furSelected.filter(v => v !== val);
    btn.className = furBase();
    btn.innerText = "+ " + val;
  } else {
    furSelected.push(val);
    btn.className = furActive();
    btn.innerText = "✓ " + val;
  }

  document.getElementById("furInput").value =
    furSelected.join(",");
}

/* clear */
function furClear() {
  furSelected = [];
  document.getElementById("furInput").value = "";
  document.querySelectorAll(".fur-pill").forEach(btn => {
    btn.className = furBase();
    btn.innerText = "+ " + btn.dataset.value;
  });
}

/* styles */
function furBase() {
  return `
    fur-pill px-4 py-1.5 rounded-full border
    text-sm text-gray-700 bg-white
    hover:bg-gray-100 transition
  `;
}

function furActive() {
  return `
    fur-pill px-4 py-1.5 rounded-full
    text-sm font-medium
    bg-orange-50 text-orange-600
    border border-orange-300
  `;
}

/* init */
document.querySelectorAll(".fur-pill").forEach(btn => {
  btn.className = furBase();
});
let reraSelected = "";

/* accordion */
function reraToggle() {
  document.getElementById("reraBody").classList.toggle("hidden");
  document.getElementById("reraArrow").classList.toggle("rotate-180");
}

/* single select */
function reraSelect(btn) {
  const val = btn.dataset.value;

  reraSelected = val;
  document.getElementById("reraInput").value = val;

  document.querySelectorAll(".rera-pill").forEach(b => {
    b.className = reraBase();
    b.innerText = "+ " + b.dataset.value;
  });

  btn.className = reraActive();
  btn.innerText = "✓ " + val;
}

/* clear */
function reraClear() {
  reraSelected = "";
  document.getElementById("reraInput").value = "";

  document.querySelectorAll(".rera-pill").forEach(b => {
    b.className = reraBase();
    b.innerText = "+ " + b.dataset.value;
  });
}

/* styles */
function reraBase() {
  return `
    rera-pill px-4 py-1.5 rounded-full border
    text-sm text-gray-700 bg-white
    hover:bg-gray-100 transition
  `;
}

function reraActive() {
  return `
    rera-pill px-4 py-1.5 rounded-full
    text-sm font-medium
    bg-orange-50 text-orange-600
    border border-orange-300
  `;
}

/* init */
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".rera-pill").forEach(btn => {
    btn.className = reraBase();
  });
});
document.addEventListener("DOMContentLoaded", function () {

  /* helper */
  function autoOpen(bodyId, arrowId, inputId) {
    const input = document.getElementById(inputId);
    const body  = document.getElementById(bodyId);
    const arrow = document.getElementById(arrowId);

    if (!input || !body) return;

    if (input.value && input.value.trim() !== "") {
      body.classList.remove("hidden");

      /* special case: Type of property (animated) */
      if (bodyId === "typeBody") {
        body.classList.remove("max-h-0", "opacity-0");
        body.classList.add("max-h-[500px]", "opacity-100");
      }

      if (arrow) arrow.classList.add("rotate-180");
    }
  }

  /* ================= AUTO OPEN ALL FILTERS ================= */
  autoOpen("typeBody", "typeArrow", "propertyTypeInput");
  autoOpen("bhkBody", "bhkArrow", "bhkInput");
  autoOpen("csBody", "csArrow", "csInput");
  autoOpen("amenBody", "amenArrow", "amenInput");
  autoOpen("furBody", "furArrow", "furInput");
  autoOpen("reraBody", "reraArrow", "reraInput");

});
  // ================== BUDGET RANGE ==================
function budgetToggle() {
  const body = document.getElementById("budgetBody");
  const arrow = document.getElementById("budgetArrow");

  body.classList.toggle("hidden");

  // rotate arrow
  if (body.classList.contains("hidden")) {
    arrow.classList.remove("rotate-180");
  } else {
    arrow.classList.add("rotate-180");
  }
}

function budgetClear() {
  const minBudget = document.getElementById("minBudget");
  const maxBudget = document.getElementById("maxBudget");

  // clear inputs
  minBudget.value = "";
  maxBudget.value = "";

  // auto submit (optional)
  // document.getElementById("filterForm").submit();

  // close section after clear (optional)
  const body = document.getElementById("budgetBody");
  const arrow = document.getElementById("budgetArrow");
  body.classList.add("hidden");
  arrow.classList.remove("rotate-180");
}

// Auto open if values exist
document.addEventListener("DOMContentLoaded", () => {
  const minBudget = document.getElementById("minBudget");
  const maxBudget = document.getElementById("maxBudget");
  const body = document.getElementById("budgetBody");
  const arrow = document.getElementById("budgetArrow");

  if ((minBudget && minBudget.value) || (maxBudget && maxBudget.value)) {
    body.classList.remove("hidden");
    arrow.classList.add("rotate-180");
  }
});
