import OpenAI from 'openai';
import { buildSystemPrompt, buildUserPrompt, sanitizeIncidentForLlm } from '../prompts.js';
import { normalizeLlmOutput, parseJsonLoose } from '../normalize.js';

function getClient() {
  const key = process.env.OPENAI_API_KEY;
  if (!key) return null;
  return new OpenAI({ apiKey: key });
}

export function isOpenAiConfigured() {
  return Boolean(process.env.OPENAI_API_KEY?.trim());
}

/**
 * @param {object} data - Raw incident context from the API
 */
export async function analyzeWithOpenAI(data, opts = {}) {
  const client = getClient();
  if (!client) throw new Error('OpenAI not configured');

  const repair = Boolean(opts.repair);
  const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';
  const payload = sanitizeIncidentForLlm(data);
  const temperature = Number(process.env.LLM_TEMPERATURE) || 0.15;
  const maxOutputTokens = Number(process.env.LLM_MAX_OUTPUT_TOKENS) || 600;

  const messages = [
    { role: 'system', content: buildSystemPrompt() },
  ];

  const userContent = [{ type: 'text', text: buildUserPrompt(payload, { repair }) }];

  // Step 9: If multimodal frames are provided, send them to GPT-4o
  if (data.frames && Array.isArray(data.frames) && data.frames.length > 0) {
    for (const frame of data.frames.slice(0, 2)) { // Send top 2 frames
      userContent.push({
        type: 'image_url',
        image_url: {
          url: `data:image/jpeg;base64,${frame}`,
          detail: 'low'
        }
      });
    }
  }

  messages.push({ role: 'user', content: userContent });

  const completion = await client.chat.completions.create({
    model,
    temperature,
    max_tokens: maxOutputTokens,
    messages,
    response_format: { type: 'json_object' },
  });

  const text = completion.choices[0]?.message?.content?.trim() || '{}';
  let parsed;
  try {
    parsed = parseJsonLoose(text);
  } catch (e1) {
    try {
      parsed = JSON.parse(text);
    } catch {
      throw new Error(`Invalid JSON from OpenAI: ${e1.message}`);
    }
  }
  return normalizeLlmOutput(parsed, data);
}
