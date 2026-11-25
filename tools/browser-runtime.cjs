// Shared browser setup. Install Playwright and its Chromium browser before use.
const { chromium } = require('playwright');

function launchBrowser() {
  return chromium.launch({
    headless: true,
    ...(process.env.BROWSER_EXECUTABLE
      ? { executablePath: process.env.BROWSER_EXECUTABLE }
      : {}),
  });
}

module.exports = { launchBrowser };
