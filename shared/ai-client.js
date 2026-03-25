/**
 * AI Client — Gemini API 封裝
 * 支援直接呼叫 Gemini / Cloudflare Worker 代理
 * API key 存在 localStorage，不進入原始碼
 */
const AIClient = (() => {
  const STORAGE_KEY = 'wenkai_ai_config';
  const GEMINI_BASE = 'https://generativelanguage.googleapis.com/v1beta/models';
  const DEFAULT_MODEL = 'gemini-2.0-flash-lite';

  function getConfig() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch { return {}; }
  }

  function saveConfig(cfg) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cfg));
  }

  function setApiKey(key) {
    const cfg = getConfig();
    cfg.apiKey = key;
    saveConfig(cfg);
  }

  function setWorkerUrl(url) {
    const cfg = getConfig();
    cfg.workerUrl = url;
    saveConfig(cfg);
  }

  function getApiKey() {
    return getConfig().apiKey || '';
  }

  function getWorkerUrl() {
    return getConfig().workerUrl || '';
  }

  function isConfigured() {
    const cfg = getConfig();
    return !!(cfg.apiKey || cfg.workerUrl);
  }

  /**
   * 呼叫 AI
   * @param {string} prompt - 使用者輸入
   * @param {string} systemPrompt - 系統指令
   * @param {object} opts - { route, temperature, maxTokens }
   * @returns {Promise<string>} AI 回應文字
   */
  async function chat(prompt, systemPrompt = '', opts = {}) {
    const cfg = getConfig();
    const { route, temperature = 0.7, maxTokens = 2048 } = opts;

    // 優先用 Worker 代理
    if (cfg.workerUrl && route) {
      const res = await fetch(`${cfg.workerUrl}${route}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, systemPrompt, temperature, maxTokens })
      });
      if (!res.ok) throw new Error(`Worker error: ${res.status}`);
      const data = await res.json();
      return data.text || data.response || '';
    }

    // 直接呼叫 Gemini
    if (!cfg.apiKey) {
      throw new Error('NO_API_KEY');
    }

    const model = opts.model || DEFAULT_MODEL;
    const url = `${GEMINI_BASE}/${model}:generateContent?key=${cfg.apiKey}`;

    const contents = [];
    if (systemPrompt) {
      contents.push({ role: 'user', parts: [{ text: systemPrompt }] });
      contents.push({ role: 'model', parts: [{ text: '好的，我會按照指示回應。' }] });
    }
    contents.push({ role: 'user', parts: [{ text: prompt }] });

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents,
        generationConfig: {
          temperature,
          maxOutputTokens: maxTokens
        }
      })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error?.message || `Gemini error: ${res.status}`);
    }

    const data = await res.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || '';
  }

  /**
   * 快取包裝：先查 localStorage，沒有才呼叫 AI
   */
  async function cachedChat(cacheKey, prompt, systemPrompt = '', opts = {}) {
    const ttl = opts.cacheTTL || 86400000; // 預設 24hr
    const cached = localStorage.getItem(`ai_cache_${cacheKey}`);
    if (cached) {
      try {
        const { text, ts } = JSON.parse(cached);
        if (Date.now() - ts < ttl) return text;
      } catch {}
    }
    const text = await chat(prompt, systemPrompt, opts);
    localStorage.setItem(`ai_cache_${cacheKey}`, JSON.stringify({ text, ts: Date.now() }));
    return text;
  }

  /**
   * 建立 API 設定 UI（插入到指定容器）
   */
  function renderConfigUI(container) {
    const cfg = getConfig();
    container.innerHTML = `
      <div style="padding:20px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;margin-bottom:20px;">
        <h3 style="font-family:'Noto Serif TC',serif;color:#c9a84c;margin-bottom:12px;font-size:0.95rem;">AI 設定</h3>
        <div style="margin-bottom:10px;">
          <label style="display:block;font-size:0.8rem;color:#706b62;margin-bottom:4px;">Gemini API Key</label>
          <input type="password" id="ai-api-key" value="${cfg.apiKey || ''}" placeholder="AIzaSy..."
            style="width:100%;padding:8px 12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e8e4dc;font-size:0.85rem;">
        </div>
        <div style="margin-bottom:12px;">
          <label style="display:block;font-size:0.8rem;color:#706b62;margin-bottom:4px;">Worker URL（選填）</label>
          <input type="text" id="ai-worker-url" value="${cfg.workerUrl || ''}" placeholder="https://your-worker.workers.dev"
            style="width:100%;padding:8px 12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e8e4dc;font-size:0.85rem;">
        </div>
        <button id="ai-save-config" style="padding:8px 20px;background:#c9a84c;color:#060708;border:none;border-radius:6px;cursor:pointer;font-size:0.82rem;font-weight:500;">儲存設定</button>
        <span id="ai-config-status" style="margin-left:10px;font-size:0.8rem;color:#706b62;"></span>
      </div>
    `;
    container.querySelector('#ai-save-config').addEventListener('click', () => {
      setApiKey(container.querySelector('#ai-api-key').value.trim());
      setWorkerUrl(container.querySelector('#ai-worker-url').value.trim());
      container.querySelector('#ai-config-status').textContent = '已儲存';
      setTimeout(() => { container.querySelector('#ai-config-status').textContent = ''; }, 2000);
    });
  }

  return { chat, cachedChat, setApiKey, setWorkerUrl, getApiKey, getWorkerUrl, isConfigured, renderConfigUI, getConfig, saveConfig };
})();
