/**
 * Deterministic fallback when no LLM is configured or providers fail.
 */
export function mockAnalyzeIncident(data) {
  const people = data.detected_people || [];
  const aggressor =
    people.find((p) => /aggressive|attacker|offensive/i.test(String(p.motion || ''))) ||
    people[0] ||
    { id: 'A', position: 'unknown', motion: 'unknown' };

  const summary =
    data.violence === true
      ? `Physical altercation reported at ${data.location || 'the scene'}. ` +
        `Vision model confidence: ${((data.confidence ?? 0) * 100).toFixed(0)}%. ` +
        `Primary aggressor inferred as subject ${aggressor.id} from motion cues.`
      : `No violent behavior confirmed. Scene at ${data.location || 'unknown location'} appears stable.`;

  const behavior =
    data.violence === true
      ? ['pushing', 'striking motion', 'confrontation']
      : ['standing', 'walking'];

  return {
    summary,
    culprit: {
      id: data.violence === true ? String(aggressor.id ?? 'A') : String(aggressor.id ?? 'unknown'),
      confidence:
        data.violence === true
          ? Math.round(Math.min(0.95, 0.55 + (data.confidence ?? 0) * 0.35) * 1000) / 1000
          : Math.round(Math.min(0.35, 0.12 + (data.confidence ?? 0) * 0.22) * 1000) / 1000,
      reason:
        data.violence === true
          ? 'Initiated aggressive motion and forward movement toward the other party'
          : 'No clear aggressor; incident classified as non-violent',
    },
    behavior,
    risk_level: data.violence === true ? 'High' : 'Low',
    recommendation:
      data.violence === true
        ? 'Immediate police dispatch and continuous camera tracking recommended'
        : 'Continue routine monitoring; no escalation required',
  };
}
