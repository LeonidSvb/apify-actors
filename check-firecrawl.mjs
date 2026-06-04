// Endpoint: GET https://api.firecrawl.dev/v1/team/credit-usage
// Response: data.remaining_credits, data.plan_credits, data.billing_period_start, data.billing_period_end
// Remaining = data.remaining_credits (уже готовое поле, не надо считать)

const ACCOUNTS = [
  { email: "leo@systemhustle.com",      key: "fc-4cc77eeeb8434465bc21610546311bcf" },
  { email: "standartdevelop@gmail.com", key: "fc-103432133c5c4a74b0ce3b707b5a9412" },
  { email: "pihtarsjurijs@gmail.com",   key: "fc-c4e06bd6c3304ddea774d383b3f7cb65" },
];

async function checkAccount({ email, key }) {
  const res = await fetch("https://api.firecrawl.dev/v1/team/credit-usage", {
    headers: { Authorization: `Bearer ${key}` },
  });

  if (!res.ok) {
    return { email, status: "ERROR", error: `HTTP ${res.status}` };
  }

  const json = await res.json();

  if (!json.success) {
    return { email, status: "ERROR", error: JSON.stringify(json) };
  }

  const { remaining_credits, plan_credits, billing_period_end } = json.data;
  const periodEnd = new Date(billing_period_end).toISOString().slice(0, 10);
  const usedCredits = plan_credits - remaining_credits;

  return {
    email,
    status: "OK",
    remaining: remaining_credits,
    planCredits: plan_credits,
    used: usedCredits,
    periodEnd,
  };
}

async function main() {
  const results = await Promise.all(ACCOUNTS.map(a => checkAccount(a)));

  let totalRemaining = 0;

  console.log("\n=== Firecrawl Account Status ===\n");

  for (const r of results) {
    if (r.status === "ERROR") {
      console.log(`[ERROR] ${r.email}`);
      console.log(`        ${r.error}\n`);
      continue;
    }

    console.log(`[OK] ${r.email}`);
    console.log(`     remaining: ${r.remaining.toLocaleString()} credits  |  plan/mo: ${r.planCredits.toLocaleString()}`);
    console.log(`     resets: ${r.periodEnd}\n`);

    totalRemaining += r.remaining;
  }

  const ok = results.filter(r => r.status === "OK");
  console.log("=== Summary ===");
  console.log(`Working accounts : ${ok.length}/${results.length}`);
  console.log(`Total remaining  : ${totalRemaining.toLocaleString()} credits\n`);
}

main().catch(console.error);
