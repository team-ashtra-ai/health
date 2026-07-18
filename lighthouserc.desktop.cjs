module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run serve',
      startServerReadyPattern: 'Serving .* at',
      url: [
        'http://127.0.0.1:4173/',
        'http://127.0.0.1:4173/about.html',
        'http://127.0.0.1:4173/treatments.html',
        'http://127.0.0.1:4173/skin.html',
        'http://127.0.0.1:4173/laser.html',
        'http://127.0.0.1:4173/consultation.html',
        'http://127.0.0.1:4173/contact.html',
        'http://127.0.0.1:4173/faq.html',
        'http://127.0.0.1:4173/journal.html',
        'http://127.0.0.1:4173/journal/why-aesthetic-care-begins-with-consultation.html'
      ],
      numberOfRuns: 5,
      settings: {
        preset: 'desktop',
        chromeFlags: '--headless=new --no-sandbox --disable-dev-shm-usage',
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo']
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.95 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.95 }],
        'categories:seo': ['error', { minScore: 0.95 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2200 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 150 }]
      }
    },
    upload: {
      target: 'filesystem',
      outputDir: 'performance-reports/lhci/desktop'
    }
  }
};
