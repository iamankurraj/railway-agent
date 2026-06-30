// ================= TRANSLATIONS =================
const translations = {
  en: {
    title: "🚄 SMART RAILWAY QUERY SYSTEM",
    placeholder: "Ask about trains...",
    ask: "Ask",
    results: "📊 Results",
    listening: "🎧 Listening...",
    no_trains: "🚫 No trains found",
    train_id: "Train ID",
    name: "Name",
    route: "Origin → Destination",
    date: "Date",
    time: "Departure → Arrival",
    classes: "Classes"
  },
  hi: {
    title: "🚄 स्मार्ट रेलवे पूछताछ प्रणाली",
    placeholder: "ट्रेनों के बारे में पूछें...",
    ask: "पूछें",
    results: "📊 परिणाम",
    listening: "🎧 सुन रहा हूँ...",
    no_trains: "🚫 कोई ट्रेन नहीं मिली",
    train_id: "ट्रेन आईडी",
    name: "नाम",
    route: "प्रस्थान → गंतव्य",
    date: "तारीख",
    time: "समय",
    classes: "क्लास"
  },
  mr: {
    title: "🚄 स्मार्ट रेल्वे चौकशी प्रणाली",
    placeholder: "रेल्वेबद्दल विचारा...",
    ask: "विचारा",
    results: "📊 निकाल",
    listening: "🎧 ऐकत आहे...",
    no_trains: "🚫 कोणतीही ट्रेन सापडली नाही",
    train_id: "ट्रेन आयडी",
    name: "नाव",
    route: "प्रस्थान → गंतव्य",
    date: "तारीख",
    time: "वेळ",
    classes: "वर्ग"
  }
};

let currentLang = localStorage.getItem("lang") || "en";

// ================= APPLY TRANSLATIONS =================
function applyTranslations() {
  const t = translations[currentLang];
  document.getElementById("title").innerText = t.title;
  document.getElementById("input").placeholder = t.placeholder;
  document.getElementById("ask-btn").innerText = t.ask;
  document.getElementById("result-title").innerText = t.results;
}

// function setLanguage(lang) {
//   currentLang = lang;
//   localStorage.setItem("lang", lang);
//   applyTranslations();
//   if (typeof recognition !== "undefined" && recognition) {
//     recognition.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
//   }
// }

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("lang", lang);
  applyTranslations();
  if (typeof recognition !== "undefined" && recognition) {
    // ADD "mr" case
    recognition.lang = currentLang === "hi" ? "hi-IN"
                     : currentLang === "mr" ? "mr-IN"
                     : "en-IN";
  }
}
// ================= SIDEBAR TOGGLE =================
let sidebarOpen = true;

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const app = document.getElementById("app");
  const btn = document.getElementById("hamburger-btn");
  sidebarOpen = !sidebarOpen;
  if (sidebarOpen) {
    sidebar.classList.remove("collapsed");
    app.classList.remove("expanded");
    btn.classList.add("sidebar-open");
  } else {
    sidebar.classList.add("collapsed");
    app.classList.add("expanded");
    btn.classList.remove("sidebar-open");
  }
}

// ================= SELECTORS =================
const $ = (sel) => document.querySelector(sel);
const messages = $("#messages");
const form = $("#form");
const input = $("#input");
const resultSection = $("#result-section");
const resultContainer = $("#result-container");
const micBtn = document.getElementById("mic-btn");
const inputField = document.getElementById("input");

// ================= HISTORY =================
// Each entry: { text, timestamp, result }
// "result" is the raw jsonData returned by /invoke so we can replay it
let history = JSON.parse(localStorage.getItem("history")) || [];
let activeHistoryIndex = null;
let recognition;

// ================= LOADER =================
const loader = document.createElement("div");
loader.className = "loader";
loader.style.display = "none";
resultContainer.before(loader);

function showLoader(show) {
  loader.style.display = show ? "block" : "none";
}

// ================= MESSAGE =================
function addMessage(text, who = "ai") {
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// ================= DYNAMIC DATA TRANSLATOR =================
function tData(text) {
  if (!text) return text;
  if (currentLang === "hi" && translations.data && translations.data[text]) {
    return translations.data[text];
  }
  return text;
}

// ================= INFO CARD =================
function renderInfoCard(infoText) {
  const div = document.createElement("div");
  div.className = "result-card";

  let formatted = infoText
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");

  formatted = formatted.replace(/(🚆|🕓|💰)/g, "<span class='emoji'>$1</span>");

  div.innerHTML = `
    <div class="info-header">
      <h2>${translations[currentLang].title}</h2>
      <hr>
    </div>
    <p>${formatted}</p>
  `;
  return div;
}

// ================= TRAIN TABLE =================
function renderTrainTable(trains) {
  const t = translations[currentLang];

  if (!Array.isArray(trains) || trains.length === 0) {
    return `<p style="color: gray; font-style: italic;">${t.no_trains}</p>`;
  }

  let html = `
    <table class="train-table">
      <thead>
        <tr>
          <th>${t.train_id}</th>
          <th>${t.name}</th>
          <th>${t.route}</th>
          <th>${t.date}</th>
          <th>${t.time}</th>
          <th>${t.classes}</th>
        </tr>
      </thead>
      <tbody>
  `;

  trains.forEach((td) => {
    if (!td) return;
    let classes = "";
    let classSelectHtml = "";
    if (Array.isArray(td.classes) && td.classes.length) {
      classes = td.classes.map((c) => `
          <div class="class-item">
            <b>${tData(c.class_name) || "-"}</b><br>
            ₹${c.price ?? "-"} — ${c.seats_available ?? 0} seats
          </div>`).join("");

      // build select options for choosing class when reserving
      const opts = td.classes.map((c) => {
        const label = `${c.class_name} — ₹${c.price}`;
        return `<option value="${(c.class_name || "").replace(/\"/g, '&quot;')}">${label}</option>`;
      }).join("");

      classSelectHtml = `<div class="class-select-wrapper"><select class="class-select" data-train-id="${td.train_id || ''}">${opts}</select></div>`;
    } else {
      classes = "<i>No class info</i>";
    }

    html += `
      <tr>
        <td>${td.train_id ?? "-"}</td>
        <td>${tData(td.train_name) ?? "-"}</td>
        <td>${tData(td.origin) ?? "-"} → ${tData(td.destination) ?? "-"}</td>
        <td>${td.date ?? "-"}</td>
        <td>${td.departure_time ?? "-"} → ${td.arrival_time ?? "-"}</td>
        <td>${classes}</td>
        <td>
          ${classSelectHtml}
          <button class="reserve-btn" data-train='${JSON.stringify(td).replace(/'/g, "&#39;") }'>Reserve</button>
        </td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  return html;
}

// ================= RESERVATION HANDLING =================
document.addEventListener("click", async (e) => {
  if (!e.target.matches || !e.target.matches('.reserve-btn')) return;
  const btn = e.target;
  const td = JSON.parse(btn.getAttribute('data-train'));
  const className = Array.isArray(td.classes) && td.classes.length ? td.classes[0].class_name : "Sleeper";

  btn.disabled = true;
  btn.textContent = "Reserving...";

  try {
    // read selected class from the same row if present
    const row = btn.closest('tr');
    const select = row ? row.querySelector('.class-select') : null;
    const selectedClass = select ? select.value : className;

    const payload = {
      train_id: td.train_id || td.train_number || (td.trainNo || ""),
      train_name: td.train_name || td.trainName || td.train_name,
      date: td.date,
      class_name: selectedClass,
      passenger_name: "Demo Passenger"
    };

    const res = await fetch(window.location.origin + "/booking", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const rec = await res.json();
    if (res.status !== 200) {
      alert(rec.error || 'Reservation failed');
      return;
    }

    // show a small booking card with price
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
      <h3>Reservation Confirmed</h3>
      <p>PNR: <b>${rec.pnr}</b></p>
      <p>${rec.train_name} • ${rec.date} • ${rec.class} • ₹${rec.price}</p>
      <a href="/booking/${rec.pnr}/export">Download .ics</a>
      &nbsp;|&nbsp;
      <a href="/booking/${rec.pnr}/pdf">Download PDF</a>
    `;
    resultContainer.prepend(card);

  } catch (err) {
    console.error(err);
    alert('Reservation failed');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Reserve';
  }
});

// ================= DISPLAY RESULT =================
// Centralised so both live queries AND history restores use the same logic
function displayResult(jsonData) {
  resultContainer.innerHTML = "";
  resultSection.classList.remove("hidden");

  if (!jsonData) return;

  // Info message
  if (Array.isArray(jsonData) && jsonData.length === 1 && jsonData[0].info) {
    resultContainer.appendChild(renderInfoCard(jsonData[0].info));
    return;
  }
  // Train array
  if (Array.isArray(jsonData)) {
    if (jsonData.length === 0) {
      resultContainer.innerHTML = `<p style="color:gray; font-style:italic;">🚫 No trains found for this query.</p>`;
    } else {
      // Disambiguation: single object with disambiguation flag
      if (jsonData[0] && jsonData[0].disambiguation) {
        const box = document.createElement('div');
        box.className = 'result-card';
        const p = document.createElement('p');
        p.textContent = jsonData[0].prompt || 'Which train did you mean?';
        box.appendChild(p);

        const list = document.createElement('div');
        list.className = 'disambiguation-list';
        (jsonData[0].options || []).forEach(opt => {
          const btn = document.createElement('button');
          btn.className = 'disambiguation-option';
          btn.textContent = `${opt.index}. ${opt.train_name} — ${opt.origin || '-'} → ${opt.destination || '-'} @ ${opt.departure_time || '-'} `;
          btn.onclick = () => selectDisambiguationOption(opt);
          list.appendChild(btn);
        });
        box.appendChild(list);
        resultContainer.appendChild(box);
        return;
      }
      // If items are class-level matches (have class_name), render class table
      if (jsonData[0] && jsonData[0].class_name) {
        resultContainer.innerHTML = renderClassMatchesTable(jsonData);
      } else {
        resultContainer.innerHTML = renderTrainTable(jsonData);
      }
    }
    return;
  }
  // Booking confirmation object
  if (jsonData.booking) {
    resultContainer.appendChild(renderBookingCard(jsonData.booking));
    return;
  }
  // Single info object
  if (jsonData.info) {
    resultContainer.appendChild(renderInfoCard(jsonData.info));
    return;
  }
  // Fallback
  resultContainer.innerHTML = `<pre>${JSON.stringify(jsonData, null, 2)}</pre>`;
}

function renderBookingCard(booking) {
  const card = document.createElement('div');
  card.className = 'result-card booking-card';
  card.innerHTML = `
    <h3>Booking Confirmed</h3>
    <p><strong>PNR:</strong> ${booking.pnr}</p>
    <p><strong>${booking.train_name}</strong> • ${booking.date} • ${booking.class}</p>
    <p><strong>Passenger:</strong> ${booking.passenger}</p>
    <p><strong>Price:</strong> ₹${booking.price}</p>
    <p><a href="/booking/${booking.pnr}/export">Download .ics</a> &nbsp;|&nbsp; <a href="/booking/${booking.pnr}/pdf">Download PDF</a></p>
  `;
  return card;
}

// Render table for class-level matches
function renderClassMatchesTable(items) {
  const t = translations[currentLang];
  let html = `
    <table class="train-table">
      <thead>
        <tr>
          <th>${t.train_id}</th>
          <th>${t.name}</th>
          <th>${t.route}</th>
          <th>${t.date}</th>
          <th>Class</th>
          <th>Price</th>
          <th>Seats</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
  `;

  items.forEach((it) => {
    html += `
      <tr>
        <td>${it.train_id ?? "-"}</td>
        <td>${tData(it.train_name) ?? "-"}</td>
        <td>${tData(it.origin) ?? "-"} → ${tData(it.destination) ?? "-"}</td>
        <td>${it.date ?? "-"}</td>
        <td>${tData(it.class_name) ?? "-"}</td>
        <td>₹${it.price ?? "-"}</td>
        <td>${it.seats_available ?? 0}</td>
        <td><button class="reserve-btn" data-train='${JSON.stringify(it).replace(/'/g, "&#39;") }'>Reserve</button></td>
      </tr>
    `;
  });

  html += "</tbody></table>";
  return html;
}

// ================= DISAMBIGUATION SELECTION =================
async function selectDisambiguationOption(opt) {
  if (!opt) return;
  const identifier = opt.train_id || opt.train_number || opt.train_name;
  if (!identifier) return;

  // show as user action
  addMessage(`Selected: ${opt.train_name} (${identifier})`, 'user');

  try {
    showLoader(true);
    const res = await fetch(window.location.origin + '/invoke', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: String(identifier), thread_id: 'ui', lang: currentLang })
    });
    showLoader(false);

    let jsonData;
    try {
      jsonData = await res.json();
    } catch (parseErr) {
      console.error('Failed to parse JSON from /invoke:', parseErr);
      jsonData = null;
    }

    saveHistory(identifier, jsonData);
    displayResult(jsonData);
  } catch (err) {
    showLoader(false);
    console.error('Disambiguation selection failed', err);
    addMessage('Error selecting option', 'ai');
  }
}

// ================= SAVE HISTORY =================
// CHANGED: now accepts result so we can replay the full response later
function saveHistory(text, result = null) {
  const entry = { text, timestamp: Date.now(), result };
  history.unshift(entry);
  localStorage.setItem("history", JSON.stringify(history));
  renderHistory();
}

// ================= DATE GROUP LABEL =================
function getDateLabel(timestamp) {
  const now = new Date();
  const d = new Date(timestamp);
  const diffDays = Math.floor((now - d) / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return "Previous 7 Days";
  if (diffDays < 30) return "Last Month";
  return "Older";
}

// ================= RENDER HISTORY SIDEBAR =================
function renderHistory() {
  const container = document.getElementById("history-groups");
  if (!container) return;
  container.innerHTML = "";

  if (history.length === 0) {
    container.innerHTML = `<p style="color:#4b5563; font-size:0.8rem; padding:10px 8px;">No history yet.</p>`;
    return;
  }

  const groups = {};
  const order = [];

  history.forEach((entry, i) => {
    const text = typeof entry === "string" ? entry : entry.text;
    const ts = typeof entry === "object" && entry.timestamp ? entry.timestamp : Date.now();
    const label = getDateLabel(ts);
    if (!groups[label]) { groups[label] = []; order.push(label); }
    groups[label].push({ text, index: i });
  });

  order.forEach((label) => {
    const groupDiv = document.createElement("div");
    groupDiv.className = "history-date-group";

    const labelEl = document.createElement("div");
    labelEl.className = "history-date-label";
    labelEl.textContent = label;
    groupDiv.appendChild(labelEl);

    groups[label].forEach(({ text, index }) => {
      const item = document.createElement("div");
      item.className = "history-item" + (index === activeHistoryIndex ? " active" : "");
      item.innerHTML = `
        <span class="history-item-icon">🔍</span>
        <span class="history-item-text" title="${text}">${text}</span>
      `;

      // CHANGED: clicking a history item now also restores its saved result
      item.onclick = () => {
        activeHistoryIndex = index;
        const entry = history[index];
        const entryText = typeof entry === "string" ? entry : entry.text;
        const entryResult = typeof entry === "object" ? entry.result : null;

        document.getElementById("input").value = entryText;

        // Restore the result panel if we have saved result data
        if (entryResult) {
          displayResult(entryResult);
          resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          // Old entries without saved result — clear panel
          resultContainer.innerHTML = "";
          resultSection.classList.add("hidden");
        }

        renderHistory();
        document.getElementById("input").focus();
      };

      groupDiv.appendChild(item);
    });

    container.appendChild(groupDiv);
  });
}

// ================= NEW CHAT =================
function startNewChat() {
  activeHistoryIndex = null;
  document.getElementById("input").value = "";
  document.getElementById("messages").innerHTML = "";
  document.getElementById("result-container").innerHTML = "";
  document.getElementById("result-section").classList.add("hidden");
  renderHistory();
}

// ================= FORM HANDLER =================
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  resultContainer.innerHTML = "";
  resultSection.classList.add("hidden");

  try {
    showLoader(true);

    const res = await fetch(window.location.origin + "/invoke", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: text, thread_id: "ui", lang: currentLang }),
    });

    showLoader(false);
    const full = await res.text();

    let jsonData;
    try { jsonData = JSON.parse(full); } catch { jsonData = null; }

    // CHANGED: save both the query text AND the result together
    saveHistory(text, jsonData);

    displayResult(jsonData);

    if (!jsonData) {
      addMessage(full.trim() || "(No response)", "ai");
    }

  } catch (err) {
    showLoader(false);
    addMessage(`Error: ${err}`, "ai");
  }

  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
});

// ================= SPEECH RECOGNITION =================
let isListening = false;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  // recognition.lang = currentLang === "hi" ? "hi-IN" : "en-IN";
  recognition.lang = currentLang === "hi" ? "hi-IN"
                 : currentLang === "mr" ? "mr-IN"
                 : "en-IN";

  micBtn.addEventListener("click", () => {
    if (isListening) return;
    try {
      isListening = true;
      micBtn.textContent = translations[currentLang].listening;
      recognition.start();
    } catch (err) {
      console.error("Mic start error:", err);
      isListening = false;
      micBtn.textContent = "🎙";
    }
  });

  recognition.onresult = (event) => {
    inputField.value = event.results[0][0].transcript;
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
  };

  recognition.onend = () => {
    micBtn.textContent = "🎙";
    isListening = false;
    if (inputField.value.trim() !== "") form.requestSubmit();
  };
} else {
  micBtn.disabled = true;
  micBtn.textContent = "❌";
  console.warn("Speech Recognition not supported in this browser.");
}

// ================= INIT =================
applyTranslations();
document.getElementById("hamburger-btn").classList.add("sidebar-open");
renderHistory();