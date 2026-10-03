let pending = { raw_transcript: "" };

async function api(path, opts = {}) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || r.statusText);
  }
  return r.json();
}

function showConfirm(label, transcript) {
  pending.raw_transcript = transcript || "";
  document.getElementById("confirm-card").classList.remove("hidden");
  const typeLabel = label.type === "payment_received" ? "payment" : "udhaar";
  document.getElementById("preview").textContent =
    `${label.customer} — ₹${label.amount ?? "?"} ${typeLabel}`;
  document.getElementById("f-customer").value = label.customer || "";
  document.getElementById("f-amount").value = label.amount ?? "";
  document.getElementById("f-type").value = label.type || "credit_given";
  document.getElementById("f-note").value = label.note || "";
  if (label.error) {
    document.getElementById("preview").textContent += ` (${label.error})`;
  }
}

async function refreshCustomers() {
  const list = await api("/customers");
  const ul = document.getElementById("customers");
  ul.innerHTML = list
    .map((c) => `<li><strong>${c.name}</strong>: ₹${c.balance} balance</li>`)
    .join("") || "<li>No customers yet</li>";
}

async function refreshReminders() {
  const list = await api("/reminders");
  const ul = document.getElementById("reminders");
  ul.innerHTML = list
    .map((r) => {
      const wa = r.whatsapp_url
        ? `<a class="wa" href="${r.whatsapp_url}" target="_blank" rel="noopener">WhatsApp link</a>`
        : "<span class='muted'>Add phone in DB for link</span>";
      return `<li>${r.name}: ₹${r.balance}<br/><small>${r.message}</small><br/>${wa}</li>`;
    })
    .join("") || "<li>No overdue reminders</li>";
}

async function refreshSummary() {
  const s = await api("/summary");
  document.getElementById("summary").innerHTML = `
    <p><strong>Total outstanding:</strong> ₹${s.total_outstanding}</p>
    <p><strong>Received this month (${s.month}):</strong> ₹${s.received_this_month}</p>
    <p><strong>Top dues:</strong></p>
    <ul>${(s.top_dues || []).map((t) => `<li>${t.name}: ₹${t.balance}</li>`).join("")}</ul>
  `;
}

document.getElementById("btn-parse").onclick = async () => {
  const transcript = document.getElementById("transcript").value.trim();
  const res = await api("/entry/parse", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript }),
  });
  const label = res.label;
  if (!label.amount && label.error) {
    alert("Amount missing: " + label.error);
  }
  showConfirm(label, res.transcript || transcript);
};

document.getElementById("btn-confirm").onclick = async () => {
  const amount = parseInt(document.getElementById("f-amount").value, 10);
  if (!amount || amount <= 0) {
    alert("Valid amount required");
    return;
  }
  await api("/entry/confirm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customer: document.getElementById("f-customer").value,
      amount,
      type: document.getElementById("f-type").value,
      note: document.getElementById("f-note").value || null,
      raw_transcript: pending.raw_transcript,
    }),
  });
  document.getElementById("confirm-card").classList.add("hidden");
  document.getElementById("transcript").value = "";
  await refreshCustomers();
  await refreshSummary();
};

document.getElementById("btn-cancel").onclick = () => {
  document.getElementById("confirm-card").classList.add("hidden");
};

let mediaRecorder;
let chunks = [];

document.getElementById("btn-mic").onclick = async () => {
  const btn = document.getElementById("btn-mic");
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    btn.textContent = "🎤 Mic";
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  chunks = [];
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(chunks, { type: "audio/webm" });
    const fd = new FormData();
    fd.append("file", blob, "clip.webm");
    try {
      const r = await fetch("/entry/parse-audio", { method: "POST", body: fd });
      const res = await r.json();
      if (!r.ok) throw new Error(res.detail || "Audio failed");
      document.getElementById("heard").textContent = "Heard: " + res.transcript;
      document.getElementById("transcript").value = res.transcript;
      showConfirm(res.label, res.transcript);
    } catch (e) {
      alert(e.message);
    }
    stream.getTracks().forEach((t) => t.stop());
  };
  mediaRecorder.start();
  btn.textContent = "⏹ Stop";
};

async function init() {
  const h = await api("/health");
  document.getElementById("status").textContent =
    `Mock: ${h.mock_mode} | Whisper: ${h.whisper_installed}`;
  await refreshCustomers();
  await refreshReminders();
  await refreshSummary();
}

init().catch((e) => {
  document.getElementById("status").textContent = "Error: " + e.message;
});
