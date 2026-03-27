import { ANALYSIS_JSON_SCHEMA } from './schema.js';

export function buildSystemPrompt() {
  return [
    'You are a senior security operations analyst assisting law enforcement and transit safety teams.',
    'You receive metadata from an automated violence-detection vision system (CNN/LSTM or similar).',
    'You must NOT invent subjects: only reference people listed in detected_people.',
    'If violence is false, state that clearly, keep culprit confidence low, and avoid blaming a specific person unless metadata supports it.',
    'Output must be a single JSON object only — no markdown, no commentary outside JSON.',
    'Tone: factual, concise, suitable for an incident report dashboard.',
  ].join(' ');
}

/**
 * @param {object} payload - Sanitized incident fields for the model
 */
export function buildUserPrompt(payload, opts = {}) {
  const repair = Boolean(opts.repair);
  return [
    'Task: Analyze the incident and produce JSON that matches this schema:',
    JSON.stringify(ANALYSIS_JSON_SCHEMA, null, 2),
    '',
    'Instructions:',
    '- summary: 2–4 sentences describing what likely happened and context (location, time if present).',
    '- culprit: who most likely initiated violence if violence is true; use detected_people[].id. confidence reflects how well metadata supports that identification (0–1).',
    '- behavior: short verb tags (e.g. hitting, pushing, chasing, grappling).',
    '- risk_level: Low | Medium | High based on severity and escalation potential.',
    '- recommendation: concrete next steps (dispatch, lockdown, continued monitoring, etc.).',
    '- Align risk_level and recommendation: High risk should not pair with "no action".',
    '',
    repair
      ? 'If your previous response was invalid JSON or did not match the schema, fix it now. Output ONLY valid JSON.'
      : '',
    'Incident payload:',
    JSON.stringify(payload, null, 2),
  ].join('\n');
}

/**
 * Payload sent to the LLM — avoids dumping huge frame blobs.
 */
export function sanitizeIncidentForLlm(data) {
  const ts = data.timestamp instanceof Date ? data.timestamp.toISOString() : data.timestamp;
  return {
    violence: Boolean(data.violence),
    vision_confidence: typeof data.confidence === 'number' ? data.confidence : 0,
    location: data.location || '',
    timestamp: ts || null,
    camera_id: data.camera_id || 'unknown',
    detected_people: Array.isArray(data.detected_people)
      ? data.detected_people
          .map((p) => ({
            id: p?.id == null ? '' : String(p.id),
            position: p?.position == null ? undefined : String(p.position),
            motion: p?.motion == null ? undefined : String(p.motion),
          }))
          .filter((p) => p.id.trim().length > 0)
          .slice(0, 10)
      : [],
    frame_sample_count: Array.isArray(data.frames) ? data.frames.length : 0,
  };
}
