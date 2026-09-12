const express = require('express');
const router = express.Router();
const { analyzeInternship, getAnalysis } = require('../controllers/analyzeController');

// POST /api/analyze — submit a listing for analysis
router.post('/', analyzeInternship);

// GET /api/analyze/:id — fetch a previous analysis by ID
router.get('/:id', getAnalysis);

module.exports = router;
