import { buildSystemPrompt, buildUserPrompt, sanitizeIncidentForLlm } from '../prompts.js';
import { normalizeLlmOutput, parseJsonLoose } from '../normalize.js';

function baseUrl() {
  return (process.env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434').replace(/\/$/, '');
}

/**
 * Chat completion against a local Ollama server (JSON mode).
 * @see https://github.com/ollama/ollama/blob/main/docs/api.md
 */
export async function analyzeWithOllama(data, opts = {}) {
  const model = process.env.OLLAMA_MODEL || 'llama3.2';
  const payload = sanitizeIncidentForLlm(data);
  const repair = Boolean(opts?.repair);
  const temperature = Number(process.env.LLM_TEMPERATURE) || 0.2;
  const numPredict = Number(process.env.OLLAMA_NUM_PREDICT || process.env.LLM_NUM_PREDICT) || 420;
  const requestTimeoutMs =
    Number(process.env.OLLAMA_TIMEOUT_MS) ||
    Number(process.env.LLM_REQUEST_TIMEOUT_MS) ||
    120000;
  const body = {
    model,
    stream: false,
    format: 'json',
    options: { temperature, num_predict: numPredict },
    messages: [
      { role: 'system', content: buildSystemPrompt() },
      { role: 'user', content: buildUserPrompt(payload, { repair }) },
    ],
  };

  const signal = AbortSignal.timeout(Math.max(5000, requestTimeoutMs));

  const res = await fetch(`${baseUrl()}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Ollama HTTP ${res.status}: ${errText.slice(0, 200)}`);
  }

  const json = await res.json();
  const text = json?.message?.content?.trim() || '';
  const parsed = parseJsonLoose(text);
  return normalizeLlmOutput(parsed, data);
}
