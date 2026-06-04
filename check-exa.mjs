// Endpoint: POST https://api.exa.ai/search  → проверка активности + costDollars.total за запрос
// Баланс через API недоступен — требует отдельный service key (не обычный API key)
// Для проверки баланса: https://dashboard.exa.ai/

const ACCOUNTS = [
  { email: "unknown",                   key: "7bfb231b-28b1-4f1f-b5ce-2f55b33d22b4" },
  { email: "leo@systemhustle.com",      key: "58d10405-552d-4647-86bb-fe88e8310883" },
  { email: "standartdevelop@gmail.com", key: "bab59f53-72f4-4a22-8270-c831026584f0" },
];

async function checkAccount({ email, key }) {
  const res = await fetch("https://api.exa.ai/search", {
    method: "POST",
    headers: { "x-api-key": key, "Content-Type": "application/json" },
    body: JSON.stringify({ query: "test", numResults: 1 }),
  });

  if (res.status === 401 || res.status === 403) {
    return { email, status: "INVALID_KEY", costPerCall: null };
  }

  if (res.status === 402) {
    return { email, status: "NO_CREDITS", costPerCall: null };
  }

  if (!res.ok) {
    return { email, status: `ERROR_${res.status}`, costPerCall: null };
  }

  const json = await res.json();
  const costPerCall = json.costDollars?.total ?? null;

  return { email, status: "OK", costPerCall };
}

async function main() {
  const results = await Promise.all(ACCOUNTS.map(a => checkAccount(a)));

  console.log("\n=== Exa Account Status ===\n");

  for (const r of results) {
    if (r.status !== "OK") {
      console.log(`[${r.status}] ${r.email}\n`);
      continue;
    }
    console.log(`[OK] ${r.email}`);
    console.log(`     key active | cost per search call: $${r.costPerCall}`);
    console.log(`     balance check: https://dashboard.exa.ai/\n`);
  }

  const ok = results.filter(r => r.status === "OK");
  console.log("=== Summary ===");
  console.log(`Working accounts : ${ok.length}/${results.length}`);
  console.log(`NOTE: Exa balance requires dashboard — no public API endpoint for it\n`);
}

main().catch(console.error);
