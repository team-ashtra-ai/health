const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const port = Number(process.argv[2]);
const outDir = process.argv[3];
const headed = process.argv[4] === "true";
const modes = JSON.parse(process.argv[5]);
const concepts = JSON.parse(process.argv[6]);

function urlFor(concept) {
  return `http://localhost:${port}/concepts/${encodeURIComponent(concept)}/index.html`;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });

  console.log(`Found ${concepts.length} concept homepages.`);
  console.log(`Port: ${port}`);
  console.log(`Output: ${outDir}`);
  console.log("");

  const browser = await chromium.launch({ headless: !headed });

  let completed = 0;
  let failed = 0;
  const failures = [];
  const totalJobs = concepts.length * modes.length;

  const contexts = {};

  if (modes.includes("desktop")) {
    contexts.desktop = await browser.newContext({
      viewport: { width: 1440, height: 1800 },
      deviceScaleFactor: 1,
    });
  }

  if (modes.includes("mobile")) {
    contexts.mobile = await browser.newContext({
      viewport: { width: 390, height: 1200 },
      isMobile: true,
      deviceScaleFactor: 1,
    });
  }

  for (const concept of concepts) {
    for (const mode of modes) {
      const jobNumber = completed + failed + 1;
      const url = urlFor(concept);
      const page = await contexts[mode].newPage();
      const screenshotPath = path.join(outDir, `${concept}-${mode}-full.png`);

      console.log(`[${jobNumber}/${totalJobs}] capturing ${concept} ${mode}...`);

      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
        await page.screenshot({ path: screenshotPath, fullPage: true });
        completed += 1;
        console.log(`[${jobNumber}/${totalJobs}] done ${concept} ${mode} -> ${screenshotPath}`);
      } catch (error) {
        failed += 1;
        failures.push({
          concept,
          mode,
          url,
          error: String(error && error.message ? error.message : error),
        });
        console.error(`[${jobNumber}/${totalJobs}] FAILED ${concept} ${mode}: ${error.message || error}`);
      } finally {
        await page.close().catch(() => {});
      }
    }
  }

  for (const context of Object.values(contexts)) {
    await context.close();
  }

  await browser.close();

  const report = {
    generatedAt: new Date().toISOString(),
    port,
    outDir,
    totalConcepts: concepts.length,
    modes,
    totalJobs,
    completed,
    failed,
    failures,
  };

  fs.writeFileSync(path.join(outDir, "capture-report.json"), JSON.stringify(report, null, 2));

  console.log("");
  console.log("Capture complete.");
  console.log(`Completed jobs: ${completed}/${totalJobs}`);
  console.log(`Failed jobs: ${failed}`);
  console.log(`Report: ${path.join(outDir, "capture-report.json")}`);

  if (failed > 0) {
    process.exitCode = 1;
  }
})();
