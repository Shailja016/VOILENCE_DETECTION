/**
 * Canonical shape returned by analyzeIncident (stored in Incident.ai_analysis).
 */
export const ANALYSIS_JSON_SCHEMA = {
  type: 'object',
  required: ['summary', 'culprit', 'behavior', 'risk_level', 'recommendation'],
  properties: {
    summary: { type: 'string', description: '2–4 sentences, neutral law-enforcement tone' },
    culprit: {
      type: 'object',
      required: ['id', 'confidence', 'reason'],
      properties: {
        id: { type: 'string', description: 'Must be one of detected_people[].id when list is non-empty' },
        confidence: { type: 'number', minimum: 0, maximum: 1 },
        reason: { type: 'string' },
      },
    },
    behavior: { type: 'array', items: { type: 'string' } },
    risk_level: { type: 'string', enum: ['Low', 'Medium', 'High'] },
    recommendation: { type: 'string' },
  },
};
