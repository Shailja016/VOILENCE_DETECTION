import { isOpenAiConfigured } from './providers/openai.js';

/**
 * Safe runtime info for /api/health (no secrets).
 */
export function getLlmRuntimeInfo() {
  return {
    provider: process.env.LLM_PROVIDER || 'auto',
    openai_configured: isOpenAiConfigured(),
    openai_model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
    ollama_base_url: process.env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434',
    ollama_model: process.env.OLLAMA_MODEL || 'llama3.2',
  };
}
