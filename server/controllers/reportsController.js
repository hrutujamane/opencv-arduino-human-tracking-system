const Analysis = require('../models/Analysis');

/**
 * GET /api/reports/stats
 * Returns aggregate statistics for the platform
 */
async function getStats(req, res) {
  try {
    const total = await Analysis.countDocuments();
    const scams = await Analysis.countDocuments({ verdict: 'scam' });
    const suspicious = await Analysis.countDocuments({ verdict: 'suspicious' });
    const safe = await Analysis.countDocuments({ verdict: 'safe' });

    return res.json({ total, scams, suspicious, safe });
  } catch (err) {
    return res.status(500).json({ error: 'Failed to retrieve stats.' });
  }
}

/**
 * GET /api/reports/company?name=Acme
 * Returns community report count for a given company
 */
async function getCompanyReports(req, res) {
  const { name } = req.query;
  if (!name) return res.status(400).json({ error: 'Company name is required.' });

  try {
    const count = await Analysis.countDocuments({
      companyName: { $regex: new RegExp(name.trim(), 'i') },
      verdict: { $in: ['suspicious', 'scam'] },
    });
    return res.json({ company: name, reportCount: count });
  } catch (err) {
    return res.status(500).json({ error: 'Failed to retrieve company reports.' });
  }
}

module.exports = { getStats, getCompanyReports };
