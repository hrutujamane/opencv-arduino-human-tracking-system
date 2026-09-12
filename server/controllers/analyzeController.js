const Analysis = require('../models/Analysis');
const { analyzeListingWithAI } = require('../utils/aiAnalyzer');
const { scrapeListingUrl } = require('../utils/scraper');

/**
 * POST /api/analyze
 * Main analysis endpoint — accepts text or URL input
 */
async function analyzeInternship(req, res) {
  const { inputType, companyName, jobTitle, listingText, listingUrl } = req.body;

  // ─── Validation ──────────────────────────────────────────────────────────
  if (!inputType || !['text', 'url'].includes(inputType)) {
    return res.status(400).json({ error: 'inputType must be "text" or "url"' });
  }

  if (inputType === 'text' && (!listingText || listingText.trim().length < 30)) {
    return res.status(400).json({
      error: 'Please provide at least 30 characters of listing description.',
    });
  }

  if (inputType === 'url' && (!listingUrl || !listingUrl.trim())) {
    return res.status(400).json({ error: 'Please provide a valid internship listing URL.' });
  }

  try {
    let textToAnalyze = '';

    // ─── Extract Text ───────────────────────────────────────────────────────
    if (inputType === 'url') {
      try {
        textToAnalyze = await scrapeListingUrl(listingUrl.trim());
      } catch (scrapeErr) {
        return res.status(422).json({
          error: scrapeErr.message || 'Failed to fetch content from the provided URL.',
        });
      }
    } else {
      textToAnalyze = listingText.trim();
    }

   // Local Pattern Matching Engine (No API Key Required)
const scamKeywords = ['processing fee', 'security deposit', 'whatsapp only', 'telegram', 'registration fee', 'security amount'];
let detectedFlags = [];
let score = 100;

scamKeywords.forEach(keyword => {
    if (textToAnalyze.toLowerCase().includes(keyword)) {
        score -= 25;
        detectedFlags.push(keyword.toUpperCase());
    }
});

const aiResult = {
    trustScore: Math.max(score, 0),
    verdict: score < 50 ? 'suspicious' : 'safe',
    summary: score < 50 ? "High-risk linguistic patterns detected in the description." : "No immediate scam patterns found.",
    redFlags: detectedFlags,
    actionableSteps: [
        "Verify company registration on MCA website",
        "Never pay any amount for 'processing' or 'laptops'",
        "Contact HR through official LinkedIn channels"
    ]
};
    // ─── Save to DB ─────────────────────────────────────────────────────────
    // Skip database save for demo
    const analysis = { ...aiResult, companyName, jobTitle, createdAt: new Date() };
    //    const analysis = await Analysis.create({
    //   inputType,
    //   companyName: companyName?.trim(),
    //   jobTitle: jobTitle?.trim(),
    //   listingText: inputType === 'text' ? listingText.trim() : textToAnalyze,
    //   listingUrl: inputType === 'url' ? listingUrl.trim() : undefined,
    //   trustScore: aiResult.trustScore,
    //   verdict: aiResult.verdict,
    //   summary: aiResult.summary,
    //   redFlags: aiResult.redFlags || [],
    //   actionableSteps: aiResult.actionableSteps || [],
    //   ipAddress: req.ip,
    // });

    // ─── Community Report Count ─────────────────────────────────────────────
    // Count how many other analyses flagged this company as suspicious/scam
    let communityReportCount = 0;
    if (companyName?.trim()) {
      // communityReportCount = await Analysis.countDocuments({
      //   companyName: { $regex: new RegExp(companyName.trim(), 'i') },
      //   verdict: { $in: ['suspicious', 'scam'] },
      //   _id: { $ne: analysis._id },
      // });
    }

    return res.status(201).json({
      id: analysis._id,
      trustScore: analysis.trustScore,
      verdict: analysis.verdict,
      summary: analysis.summary,
      redFlags: analysis.redFlags,
      actionableSteps: analysis.actionableSteps,
      companyName: analysis.companyName,
      jobTitle: analysis.jobTitle,
      communityReportCount,
      analyzedAt: analysis.createdAt,
    });
  } catch (err) {
    console.error('Analysis error:', err);

    if (err.message?.includes('ANTHROPIC_API_KEY')) {
      return res.status(503).json({ error: 'AI service not configured. Please set your API key.' });
    }

    if (err.name === 'SyntaxError') {
      return res.status(502).json({ error: 'AI returned an unexpected response. Please try again.' });
    }

    return res.status(500).json({ error: 'Analysis failed. Please try again.' });
  }
}

/**
 * GET /api/analyze/:id
 * Retrieve a previously saved analysis result
 */
async function getAnalysis(req, res) {
  try {
    const analysis = await Analysis.findById(req.params.id).lean();
    if (!analysis) return res.status(404).json({ error: 'Analysis not found.' });

    const communityReportCount = analysis.companyName
      ? await Analysis.countDocuments({
          companyName: { $regex: new RegExp(analysis.companyName, 'i') },
          verdict: { $in: ['suspicious', 'scam'] },
          _id: { $ne: analysis._id },
        })
      : 0;

    return res.json({ ...analysis, communityReportCount });
  } catch (err) {
    if (err.name === 'CastError') return res.status(400).json({ error: 'Invalid analysis ID.' });
    return res.status(500).json({ error: 'Failed to retrieve analysis.' });
  }
}

module.exports = { analyzeInternship, getAnalysis };
