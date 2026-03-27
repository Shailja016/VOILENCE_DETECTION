import { mockAnalyzeIncident } from './mock.js';

export function clamp01(n) {
  if (typeof n !== 'number' || Number.isNaN(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

/**
 * Ensures culprit.id is one of known subject ids when possible.
 */
function coerceCulpritId(id, data) {
  const ids = (data.detected_people || []).map((p) => String(p.id ?? '').trim()).filter(Boolean);
  const s = String(id ?? '').trim();
  if (ids.length === 0) return s || 'unknown';
  if (ids.includes(s)) return s;
  const lower = s.toLowerCase();
  const match = ids.find((x) => x.toLowerCase() === lower);
  if (match) return match;
  return ids[0];
}

/**
 * Merges model output with safe fallbacks and fixes invalid culprit ids.
 */
export function normalizeLlmOutput(parsed, data) {
  const fallback = mockAnalyzeIncident(data);
  const raw = parsed && typeof parsed === 'object' ? parsed : {};

  const culpritId = coerceCulpritId(raw.culprit?.id, data);

  return {
    summary: typeof raw.summary === 'string' && raw.summary.trim() ? raw.summary.trim() : fallback.summary,
    culprit: {
      id: culpritId,
      confidence:
        Math.round(
          clamp01(
            typeof raw.culprit?.confidence === 'number'
              ? raw.culprit.confidence
              : fallback.culprit.confidence
          ) * 1000
        ) / 1000,
      reason:
        typeof raw.culprit?.reason === 'string' && raw.culprit.reason.trim()
          ? raw.culprit.reason.trim()
          : fallback.culprit.reason,
    },
    behavior: Array.isArray(raw.behavior) ? raw.behavior.map((b) => String(b)) : fallback.behavior,
    risk_level: ['Low', 'Medium', 'High'].includes(raw.risk_level)
      ? raw.risk_level
      : fallback.risk_level,
    recommendation:
      typeof raw.recommendation === 'string' && raw.recommendation.trim()
        ? raw.recommendation.trim()
        : fallback.recommendation,
  };
}

/**
 * Strips ```json fences and parses JSON from LLM text.
 */
export function parseJsonLoose(text) {
  const t = String(text ?? '').trim();
  if (!t) throw new Error('Empty LLM response');
  const fence = /^```(?:json)?\s*([\s\S]*?)```$/im.exec(t);
  const body = fence ? fence[1].trim() : t;
  return JSON.parse(body);
}
