const axios = require('axios');

/**
 * Analyzes internship listing text using the Anthropic Claude API (via axios).
 * Returns a structured JSON object with trustScore, verdict, redFlags, actionableSteps.
 */
async function analyzeListingWithAI(listingText, companyName, jobTitle) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY environment variable is not set.');
  }

  const systemPrompt = `You are InternShield's AI scam detection engine. Your job is to analyze internship listings for signs of fraud, scams, and suspicious practices.

You must respond ONLY with a valid JSON object — no markdown backticks, no preamble, just raw JSON.

Analyze the listing for these red flags:
- Pay-to-join schemes (registration fees, equipment deposits, training fees)
- Vague or non-existent job descriptions
- Suspicious contact methods (only WhatsApp/Telegram/personal Gmail)
- Unrealistic compensation promises ("earn 50k/month from home")
- Unverifiable company information
- Requests for personal or banking info upfront
- Generic copy-paste listings with no specifics
- No verifiable company address or registration
- Pressure tactics or extreme urgency language
- Unprofessional grammar or suspicious formatting

Respond with EXACTLY this JSON structure (no extra fields):
{
  "trustScore": <integer 0-100, higher = more trustworthy>,
  "verdict": <"safe" | "suspicious" | "scam">,
  "summary": <one concise sentence summarizing your finding>,
  "redFlags": [
    {
      "type": <short descriptive flag name, e.g. "Pay-to-Join Scheme">,
      "description": <1-2 sentence explanation of why this is a red flag>,
      "severity": <"low" | "medium" | "high">
    }
  ],
  "actionableSteps": [<exactly 5 actionable strings the student should take>]
}

Score guide (strictly enforce):
- 0-40  → verdict must be "scam"
- 41-70 → verdict must be "suspicious"
- 71-100 → verdict must be "safe"

If no red flags are found, return an empty redFlags array.`;

  const userPrompt = `Analyze this internship listing and return only the JSON:

Company: ${companyName || 'Not provided'}
Job Title: ${jobTitle || 'Not provided'}

Listing Content:
---
${listingText}
---`;

  const response = await axios.post(
    'https://api.anthropic.com/v1/messages',
    {
      model: 'claude-opus-4-5',
      max_tokens: 1500,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }],
    },
    {
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      timeout: 45000,
    }
  );

  const rawText = response.data.content?.[0]?.text || '';

  // Strip any accidental markdown fences
  const cleaned = rawText.replace(/```json\s*/gi, '').replace(/```\s*/gi, '').trim();

  let parsed;
  try {
    parsed = JSON.parse(cleaned);
  } catch (e) {
    throw new SyntaxError(`AI returned non-JSON response: ${cleaned.slice(0, 200)}`);
  }

  // Clamp and validate score
  parsed.trustScore = Math.max(0, Math.min(100, Math.round(Number(parsed.trustScore) || 50)));

  // Enforce verdict <-> score alignment
  if (parsed.trustScore <= 40) parsed.verdict = 'scam';
  else if (parsed.trustScore <= 70) parsed.verdict = 'suspicious';
  else parsed.verdict = 'safe';

  // Ensure arrays exist
  if (!Array.isArray(parsed.redFlags)) parsed.redFlags = [];
  if (!Array.isArray(parsed.actionableSteps)) parsed.actionableSteps = [];

  return parsed;
}

module.exports = { analyzeListingWithAI };
