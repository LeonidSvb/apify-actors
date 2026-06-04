// Endpoint: GET https://api.apify.com/v2/users/me/limits  → current.monthlyUsageUsd, limits.maxMonthlyUsageUsd
// Endpoint: GET https://api.apify.com/v2/users/me         → email, username, effectivePlatformFeatures
// Remaining = limits.maxMonthlyUsageUsd - current.monthlyUsageUsd
// Run: node --env-file=.env check-apify-accounts.mjs

const ACCOUNTS = [
  { email: "leo@systemhustle.com",      key: process.env.APIFY_KEY_1 },
  { email: "standartdevelop@gmail.com", key: process.env.APIFY_KEY_2 },
  { email: "kadekwasriaty@gmail.com",   key: process.env.APIFY_KEY_3 },
  { email: "putu77193@gmail.com",       key: process.env.APIFY_KEY_4 },
  { email: "kadekputu2499@gmail.com",   key: process.env.APIFY_KEY_5 },
  { email: "pihtarsjurijs@gmail.com",   key: process.env.APIFY_KEY_6 },
];

const CRITICAL_FEATURES = ["ACTORS", "STORAGE"];

async function fetchJson(url, key) {
  const res = await fetch(url, { headers: { Authorization: `Bearer ${key}` } });
  return res.json();
}

async function checkAccount({ email, key }) {
  const name = email;
  const [limitsData, userData] = await Promise.all([
    fetchJson("https://api.apify.com/v2/users/me/limits", key),
    fetchJson("https://api.apify.com/v2/users/me", key),
  ]);

  const limits  = limitsData.data?.limits  ?? {};
  const current = limitsData.data?.current ?? {};
  const features = userData.data?.effectivePlatformFeatures ?? {};

  const maxUsd  = limits.maxMonthlyUsageUsd ?? 0;
  const usedUsd = current.monthlyUsageUsd   ?? 0;
  const remaining = +(maxUsd - usedUsd).toFixed(4);

  const blocked = Object.entries(features)
    .filter(([k, v]) => CRITICAL_FEATURES.includes(k) && !v.isEnabled)
    .map(([k, v]) => `${k}: ${v.disabledReason}`);

  const status = blocked.length > 0 ? "BLOCKED" : "OK";

  return { name, status, usedUsd: +usedUsd.toFixed(4), maxUsd, remaining, blocked };
}

async function main() {
  const results = await Promise.all(ACCOUNTS.map(a => checkAccount(a)));

  let totalMax       = 0;
  let totalRemaining = 0;

  console.log("\n=== Apify Account Status ===\n");

  for (const r of results) {
    const flag = r.status === "BLOCKED" ? "BLOCKED" : "OK";
    console.log(`[${flag}] ${r.name}`);
    console.log(`       used $${r.usedUsd} / $${r.maxUsd}  |  remaining: $${r.remaining}`);
    if (r.blocked.length) {
      for (const b of r.blocked) console.log(`       ! ${b}`);
    }
    console.log("");

    if (r.status === "OK") {
      totalMax       += r.maxUsd;
      totalRemaining += r.remaining;
    }
  }

  const blocked = results.filter(r => r.status === "BLOCKED").map(r => r.name);

  console.log("=== Summary ===");
  console.log(`Working accounts : ${results.length - blocked.length}/${results.length}`);
  if (blocked.length) console.log(`Blocked          : ${blocked.join(", ")}`);
  console.log(`Total limit (OK) : $${totalMax.toFixed(2)}`);
  console.log(`Total remaining  : $${totalRemaining.toFixed(4)}\n`);
}

main().catch(console.error);
