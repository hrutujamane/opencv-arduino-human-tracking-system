const mongoose = require('mongoose');

const RedFlagSchema = new mongoose.Schema({
  type: { type: String, required: true },
  description: { type: String, required: true },
  severity: { type: String, enum: ['low', 'medium', 'high'], default: 'medium' },
});

const AnalysisSchema = new mongoose.Schema(
  {
    // Input
    inputType: { type: String, enum: ['text', 'url'], required: true },
    companyName: { type: String, trim: true },
    jobTitle: { type: String, trim: true },
    listingText: { type: String },
    listingUrl: { type: String, trim: true },

    // Result
    trustScore: { type: Number, min: 0, max: 100 },
    verdict: {
      type: String,
      enum: ['safe', 'suspicious', 'scam'],
      default: 'suspicious',
    },
    summary: { type: String },
    redFlags: [RedFlagSchema],
    actionableSteps: [{ type: String }],

    // Meta
    ipAddress: { type: String },
    analysisVersion: { type: String, default: '1.0' },
  },
  { timestamps: true }
);

// Index for community report lookups by company
AnalysisSchema.index({ companyName: 1, verdict: 1 });
AnalysisSchema.index({ listingUrl: 1 });

module.exports = mongoose.model('Analysis', AnalysisSchema);
