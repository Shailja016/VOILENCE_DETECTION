import { mockAnalyzeIncident } from './mock.js';
import { analyzeWithOpenAI, isOpenAiConfigured } from './providers/openai.js';
import { analyzeWithOllama } from './providers/ollama.js';

function isStrictMode() {
  return String(process.env.LLM_STRICT || '').toLowerCase() === 'true';
}

function getMaxAttempts() {
  const retries = Number(process.env.LLM_RETRY_COUNT ?? 1);
  const r = Number.isFinite(retries) ? retries : 1;
  return Math.max(1, r + 1); // first attempt + retries
}

async function withRetries(fn) {
  const strict = isStrictMode();
  const maxAttempts = getMaxAttempts();
  let lastErr;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const repair = attempt > 0;
    try {
      return await fn({ repair });
    } catch (err) {
      lastErr = err;
      console.error('[llm] attempt failed:', attempt + 1, '/', maxAttempts, err?.message || err);
      if (strict) continue;
    }
  }

  if (strict && lastErr) throw lastErr;
  return null;
}

/**
 * @param {object} data - Incident context from vision pipeline / API
 * @returns {Promise<{summary:string, culprit:object, behavior:string[], risk_level:string, recommendation:string}>}
 */
export async function analyzeIncident(data) {
  const mode = (process.env.LLM_PROVIDER || 'auto').toLowerCase();
  const strict = isStrictMode();

  if (mode === 'mock') {
    return mockAnalyzeIncident(data);
  }

  if (mode === 'openai') {
    const ok = await withRetries((opts) => analyzeWithOpenAI(data, opts));
    if (ok) return ok;
    if (strict) throw new Error('OpenAI analysis failed in strict mode');
    return mockAnalyzeIncident(data);
  }

  if (mode === 'ollama') {
    const ok = await withRetries((opts) => analyzeWithOllama(data, opts));
    if (ok) return ok;
    if (strict) throw new Error('Ollama analysis failed in strict mode');
    return mockAnalyzeIncident(data);
  }

  if (mode !== 'auto') {
    console.warn('[llm] Unknown LLM_PROVIDER, using mock:', mode);
    if (strict) throw new Error(`Unknown LLM_PROVIDER: ${mode}`);
    return mockAnalyzeIncident(data);
  }

  // auto: OpenAI (if configured) -> Ollama -> mock
  if (isOpenAiConfigured()) {
    const ok = await withRetries((opts) => analyzeWithOpenAI(data, opts));
    if (ok) return ok;
    if (strict) throw new Error('OpenAI analysis failed in strict mode');
    console.error('[llm] OpenAI failed, trying Ollama...');
  }

  const okOllama = await withRetries((opts) => analyzeWithOllama(data, opts));
  if (okOllama) return okOllama;

  if (strict) throw new Error('Ollama analysis failed in strict mode');
  return mockAnalyzeIncident(data);
}

export { mockAnalyzeIncident } from './mock.js';
