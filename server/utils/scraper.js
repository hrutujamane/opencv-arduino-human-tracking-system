const axios = require('axios');
const cheerio = require('cheerio');

/**
 * Fetches and extracts readable text from a job listing URL
 * Works with most job boards (LinkedIn, Indeed, Internshala, etc.)
 */
async function scrapeListingUrl(url) {
  // Validate URL format
  try {
    new URL(url);
  } catch {
    throw new Error('Invalid URL format. Please provide a complete URL including https://');
  }

  const response = await axios.get(url, {
    timeout: 15000,
    headers: {
      'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      Accept: 'text/html,application/xhtml+xml',
      'Accept-Language': 'en-US,en;q=0.9',
    },
    maxRedirects: 5,
  });

  const $ = cheerio.load(response.data);

  // Remove noisy elements
  $('script, style, nav, header, footer, iframe, img, svg, [aria-hidden="true"]').remove();
  $('[class*="ad-"], [class*="cookie"], [class*="popup"], [id*="modal"]').remove();

  // Try to extract main content intelligently
  const contentSelectors = [
    'main',
    'article',
    '[class*="job-description"]',
    '[class*="listing-detail"]',
    '[class*="description"]',
    '[id*="description"]',
    '[class*="content"]',
    'body',
  ];

  let text = '';
  for (const selector of contentSelectors) {
    const el = $(selector).first();
    if (el.length) {
      text = el.text().replace(/\s+/g, ' ').trim();
      if (text.length > 200) break;
    }
  }

  if (!text || text.length < 100) {
    throw new Error(
      'Could not extract enough content from this URL. The page may require login or block scrapers. ' +
        'Try copying and pasting the listing text directly instead.'
    );
  }

  // Truncate to 8000 chars to stay within API limits
  return text.slice(0, 8000);
}

module.exports = { scrapeListingUrl };
