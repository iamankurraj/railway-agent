
// === SELECTORS ===
const $ = (sel) => document.querySelector(sel);
const messages = $("#messages");
const form = $("#form");
const input = $("#input");
const resultSection = $("#result-section");
const resultContainer = $("#result-container");

// === LOADER SETUP ===
const loader = document.createElement("div");
loader.className = "loader";
loader.style.display = "none";
resultContainer.before(loader);

function showLoader(show) {
  loader.style.display = show ? "block" : "none";
}

// === MESSAGE HANDLING ===
function addMessage(text, who = "ai") {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// === INFO CARD ===
function renderInfoCard(infoText) {
  const div = document.createElement("div");
  div.className = "result-card";

  // Replace markdown-like syntax with styled HTML
  let formatted = infoText
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // **bold**
    .replace(/\*(.*?)\*/g, "<em>$1</em>") // *italic*
    .replace(/\n/g, "<br>"); // line breaks

  // Add emojis spacing
  formatted = formatted.replace(/(🚆|🕓|💰)/g, "<span class='emoji'>$1</span>");

  div.innerHTML = `
    <div class="info-header">
      <h2>🚉 Smart Railway Query System</h2>
      <hr>
    </div>
    <p>${formatted}</p>
  `;
  return div;
}


// === TRAIN TABLE ===
function renderTrainTable(trains) {
  if (!Array.isArray(trains) || trains.length === 0) {
    return `
      <div class="no-results">
        <p style="color: gray; font-style: italic;">🚫 No trains found for this query.</p>
      </div>
    `;
  }

  let html = `
    <table class="train-table">
      <thead>
        <tr>
          <th>Train ID</th>
          <th>Name</th>
          <th>Origin → Destination</th>
          <th>Date</th>
          <th>Departure → Arrival</th>
          <th>Classes</th>
        </tr>
      </thead>
      <tbody>
  `;

  trains.forEach((t) => {
    if (!t) return;

    const classes = Array.isArray(t.classes)
      ? t.classes
          .map(
            (c) => `
              <div class="class-item">
                <b>${c.class_name || "-"}</b><br>
                ₹${c.price ?? "-"} — ${c.seats_available ?? 0} seats
              </div>
            `
          )
          .join("")
      : "<i>No class info</i>";

    html += `
      <tr>
        <td>${t.train_id ?? "-"}</td>
        <td>${t.train_name ?? "-"}</td>
        <td>${t.origin ?? "-"} → ${t.destination ?? "-"}</td>
        <td>${t.date ?? "-"}</td>
        <td>${t.departure_time ?? "-"} → ${t.arrival_time ?? "-"}</td>
        <td>${classes}</td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  return html;
}

// === FORM HANDLER ===
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  resultContainer.innerHTML = "";
  resultSection.classList.add("hidden");

  try {
    showLoader(true); // show spinner while fetching

    const res = await fetch(window.location.origin + "/invoke", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: text, thread_id: "ui" }),
    });

    showLoader(false); // hide spinner after response
    const full = await res.text();

    let jsonData;
    try {
      jsonData = JSON.parse(full);
    } catch {
      jsonData = null;
    }

    resultContainer.innerHTML = "";
    resultSection.classList.remove("hidden");

    if (!jsonData) {
      addMessage(full.trim() || "(No response)", "ai");
      return;
    }

    // 🟩 CASE 1: Info message
    if (Array.isArray(jsonData) && jsonData.length === 1 && jsonData[0].info) {
      resultContainer.appendChild(renderInfoCard(jsonData[0].info));
      return;
    }

    // 🟦 CASE 2: Train results
    if (Array.isArray(jsonData)) {
      if (jsonData.length === 0) {
        resultContainer.innerHTML = `
          <p style="color:gray; font-style:italic;">🚫 No trains found for this query.</p>
        `;
      } else {
        resultContainer.innerHTML = renderTrainTable(jsonData);
      }
      return;
    }

    // 🟨 CASE 3: Generic info object
    if (jsonData.info) {
      resultContainer.appendChild(renderInfoCard(jsonData.info));
      return;
    }

    // 🟥 CASE 4: Fallback for other JSON
    resultContainer.innerHTML = `
      <pre>${JSON.stringify(jsonData, null, 2)}</pre>
    `;
  } catch (err) {
    showLoader(false);
    addMessage(`Error: ${err}`, "ai");
  }

  // 🧭 Auto-scroll to results
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
});
