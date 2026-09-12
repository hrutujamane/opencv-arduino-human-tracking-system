const express = require('express');
const router = express.Router();
const { getStats, getCompanyReports } = require('../controllers/reportsController');

// GET /api/reports/stats
router.get('/stats', getStats);

// GET /api/reports/company?name=Acme
router.get('/company', getCompanyReports);

module.exports = router;
