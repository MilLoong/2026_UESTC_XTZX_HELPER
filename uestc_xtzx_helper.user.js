// ==UserScript==
// @name         UESTC XueTangX Helper
// @namespace    https://www.xuetangx.com/
// @version      0.1.0
// @description  在学堂在线页面内刷当前视频或按区间发送 heartbeat
// @match        https://www.xuetangx.com/learn/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addStyle
// ==/UserScript==

(function () {
  'use strict';

  const HEARTBEAT_URL = 'https://www.xuetangx.com/video-log/heartbeat/';
  const STORAGE_KEY = 'xtzx-heartbeat-template';
  const DEFAULT_DURATION = 3000;
  const DEFAULT_WAIT_MS = 5000;

  function parseCookie(name) {
    const prefix = `${name}=`;
    const found = document.cookie.split(';').map((x) => x.trim()).find((x) => x.startsWith(prefix));
    return found ? decodeURIComponent(found.slice(prefix.length)) : '';
  }

  function parseCurrentVideo() {
    const url = new URL(window.location.href);
    const parts = url.pathname.split('/').filter(Boolean);
    const learnIndex = parts.indexOf('learn');
    if (learnIndex === -1) {
      return null;
    }

    let tail = parts.slice(learnIndex + 1);
    if (tail[0] === 'space') {
      tail = tail.slice(1);
    }

    if (tail.length < 5 || tail[3] !== 'video') {
      return null;
    }

    const sign = tail[0];
    const cid = tail[2];
    const videoId = Number(tail[4]);
    if (!sign || !cid || !Number.isFinite(videoId)) {
      return null;
    }

    return { sign, cid, videoId };
  }

  function normalizeCurlText(text) {
    return String(text || '')
      .replace(/\\\r?\n/g, ' ')
      .trim();
  }

  function parseCurlTokens(text) {
    const normalized = normalizeCurlText(text);
    const regex = /'[^']*'|"[^"]*"|\S+/g;
    const rawTokens = normalized.match(regex) || [];
    return rawTokens.map((token) => {
      if ((token.startsWith("'") && token.endsWith("'")) || (token.startsWith('"') && token.endsWith('"'))) {
        return token.slice(1, -1);
      }
      return token;
    });
  }

  function parseHeartbeatCurl(text) {
    const tokens = parseCurlTokens(text);
    if (!tokens.length || tokens[0] !== 'curl') {
      throw new Error('粘贴内容不是有效的 curl(bash)');
    }

    let dataRaw = '';
    for (let i = 1; i < tokens.length; i += 1) {
      const token = tokens[i];
      if ((token === '--data-raw' || token === '--data' || token === '--data-binary' || token === '-d') && i + 1 < tokens.length) {
        dataRaw = tokens[i + 1];
        break;
      }
    }

    if (!dataRaw) {
      throw new Error('没有在 curl 里找到 --data-raw');
    }

    let payload;
    try {
      payload = JSON.parse(dataRaw);
    } catch (error) {
      throw new Error('heartbeat 的 JSON 解析失败');
    }

    const first = payload && Array.isArray(payload.heart_data) ? payload.heart_data[0] : null;
    if (!first) {
      throw new Error('heartbeat 里没有 heart_data[0]');
    }

    const template = {
      d: Number(first.d) || DEFAULT_DURATION,
      u: Number(first.u) || 0,
      c: Number(first.c) || 0,
      skuid: Number(first.skuid) || 0,
      cc: String(first.cc || ''),
    };

    if (!template.u || !template.c || !template.skuid || !template.cc) {
      throw new Error('heartbeat 缺少 u/c/skuid/cc 关键字段');
    }

    return template;
  }

  function getStoredTemplate() {
    const saved = GM_getValue(STORAGE_KEY, '');
    if (!saved) {
      return null;
    }
    try {
      return JSON.parse(saved);
    } catch (error) {
      return null;
    }
  }

  function saveTemplate(template) {
    GM_setValue(STORAGE_KEY, JSON.stringify(template));
  }

  function createHeartData(template, context, videoId, duration) {
    const baseTs = Date.now();
    const heartData = [];
    const loops = Math.max(1, Math.floor(duration / 5));

    for (let i = 0; i < loops; i += 1) {
      heartData.push({
        c: template.c,
        cards_id: 0,
        cc: template.cc,
        classroomid: context.cid,
        cp: i * 5,
        d: duration,
        et: 'heartbeat',
        fp: 0,
        i: 5,
        lob: 'plat2',
        n: 'ali-cdn.xuetangx.com',
        p: 'web',
        pg: `${videoId}_vw2x`,
        skuid: template.skuid,
        slide: 0,
        sp: 1,
        sq: i + 1,
        t: 'video',
        tp: 1,
        ts: String(baseTs + i * 5000),
        u: template.u,
        uip: '',
        v: videoId,
        v_url: '',
      });
    }

    heartData.push({
      c: template.c,
      cards_id: 0,
      cc: template.cc,
      classroomid: context.cid,
      cp: loops * 5 + 5,
      d: duration,
      et: 'videoend',
      fp: 0,
      i: 5,
      lob: 'plat2',
      n: 'ali-cdn.xuetangx.com',
      p: 'web',
      pg: `${videoId}_vw2x`,
      skuid: template.skuid,
      slide: 0,
      sp: 1,
      sq: loops + 2,
      t: 'video',
      tp: 1,
      ts: String(baseTs + loops * 5000 + 5000),
      u: template.u,
      uip: '',
      v: videoId,
      v_url: '',
    });

    return { heart_data: heartData };
  }

  async function postHeartbeat(template, context, videoId, duration) {
    const response = await fetch(HEARTBEAT_URL, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'content-type': 'application/json',
        'x-csrftoken': parseCookie('csrftoken'),
        'x-requested-with': 'XMLHttpRequest',
        'xtbz': 'xt',
      },
      referrer: `${window.location.origin}/learn/space/${context.sign}/${context.sign}/${context.cid}/video/${videoId}`,
      body: JSON.stringify(createHeartData(template, context, videoId, duration)),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const text = await response.text();
    let json = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch (error) {
      json = null;
    }

    if (json && json.detail) {
      throw new Error(String(json.detail));
    }

    return json;
  }

  function sleep(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function addStyles() {
    GM_addStyle(`
      #xtzx-helper-panel {
        position: fixed;
        right: 16px;
        bottom: 16px;
        z-index: 999999;
        width: 340px;
        border-radius: 16px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.94));
        color: #e2e8f0;
        box-shadow: 0 20px 60px rgba(15, 23, 42, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.2);
        font: 14px/1.45 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      #xtzx-helper-panel * {
        box-sizing: border-box;
      }
      #xtzx-helper-panel .xtzx-header {
        padding: 14px 16px 8px;
        font-size: 15px;
        font-weight: 700;
      }
      #xtzx-helper-panel .xtzx-body {
        padding: 0 16px 16px;
      }
      #xtzx-helper-panel .xtzx-hint,
      #xtzx-helper-panel .xtzx-status,
      #xtzx-helper-panel .xtzx-meta {
        margin-bottom: 10px;
        color: #cbd5e1;
      }
      #xtzx-helper-panel .xtzx-meta {
        font-size: 12px;
      }
      #xtzx-helper-panel textarea,
      #xtzx-helper-panel input {
        width: 100%;
        border: 1px solid rgba(148, 163, 184, 0.25);
        background: rgba(15, 23, 42, 0.65);
        color: #f8fafc;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 10px;
      }
      #xtzx-helper-panel textarea {
        min-height: 96px;
        resize: vertical;
      }
      #xtzx-helper-panel .xtzx-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
      }
      #xtzx-helper-panel button {
        width: 100%;
        border: 0;
        border-radius: 10px;
        padding: 10px 12px;
        margin-top: 6px;
        background: linear-gradient(135deg, #f97316, #ea580c);
        color: white;
        font-weight: 700;
        cursor: pointer;
      }
      #xtzx-helper-panel button.xtzx-secondary {
        background: linear-gradient(135deg, #334155, #1e293b);
      }
      #xtzx-helper-panel button:disabled {
        opacity: 0.55;
        cursor: not-allowed;
      }
    `);
  }

  function buildPanel() {
    const context = parseCurrentVideo();
    if (!context) {
      return;
    }

    addStyles();

    const panel = document.createElement('div');
    panel.id = 'xtzx-helper-panel';
    panel.innerHTML = `
      <div class="xtzx-header">学堂在线助手</div>
      <div class="xtzx-body">
        <div class="xtzx-meta" id="xtzx-context"></div>
        <div class="xtzx-hint">先从 F12 复制一次当前视频的 heartbeat 请求为 curl(bash)，粘贴后保存模板。</div>
        <textarea id="xtzx-curl" placeholder="把 heartbeat 的 curl(bash) 粘贴到这里"></textarea>
        <div class="xtzx-row">
          <input id="xtzx-start" placeholder="起始视频 ID" />
          <input id="xtzx-end" placeholder="结束视频 ID" />
        </div>
        <div class="xtzx-row">
          <input id="xtzx-duration" placeholder="视频时长秒数，默认 3000" />
          <input id="xtzx-wait" placeholder="间隔毫秒，默认 5000" />
        </div>
        <button id="xtzx-save" class="xtzx-secondary">保存 heartbeat 模板</button>
        <button id="xtzx-current">刷当前视频</button>
        <button id="xtzx-range">刷起止区间</button>
        <div class="xtzx-status" id="xtzx-status">状态：待命</div>
      </div>
    `;
    document.body.appendChild(panel);

    const contextNode = panel.querySelector('#xtzx-context');
    const curlInput = panel.querySelector('#xtzx-curl');
    const startInput = panel.querySelector('#xtzx-start');
    const endInput = panel.querySelector('#xtzx-end');
    const durationInput = panel.querySelector('#xtzx-duration');
    const waitInput = panel.querySelector('#xtzx-wait');
    const saveButton = panel.querySelector('#xtzx-save');
    const currentButton = panel.querySelector('#xtzx-current');
    const rangeButton = panel.querySelector('#xtzx-range');
    const statusNode = panel.querySelector('#xtzx-status');

    const savedTemplate = getStoredTemplate();
    startInput.value = String(context.videoId);
    endInput.value = String(context.videoId);
    if (savedTemplate && savedTemplate.d) {
      durationInput.value = String(savedTemplate.d);
    }
    waitInput.value = String(DEFAULT_WAIT_MS);

    contextNode.textContent = `sign=${context.sign} | cid=${context.cid} | 当前视频=${context.videoId}`;

    const setStatus = (message) => {
      statusNode.textContent = `状态：${message}`;
    };

    const withLock = async (fn) => {
      const buttons = [saveButton, currentButton, rangeButton];
      buttons.forEach((button) => {
        button.disabled = true;
      });
      try {
        await fn();
      } finally {
        buttons.forEach((button) => {
          button.disabled = false;
        });
      }
    };

    function resolveTemplate() {
      const pasted = curlInput.value.trim();
      if (pasted) {
        const parsed = parseHeartbeatCurl(pasted);
        saveTemplate(parsed);
        return parsed;
      }
      const stored = getStoredTemplate();
      if (!stored) {
        throw new Error('还没有保存 heartbeat 模板');
      }
      return stored;
    }

    function resolveDuration(template) {
      const value = Number(durationInput.value || template.d || DEFAULT_DURATION);
      if (!Number.isFinite(value) || value <= 0) {
        throw new Error('视频时长必须是正数');
      }
      return Math.floor(value);
    }

    function resolveWait() {
      const value = Number(waitInput.value || DEFAULT_WAIT_MS);
      if (!Number.isFinite(value) || value < 0) {
        throw new Error('间隔毫秒不能小于 0');
      }
      return Math.floor(value);
    }

    async function runRange(startId, endId) {
      const template = resolveTemplate();
      const duration = resolveDuration(template);
      const waitMs = resolveWait();
      const from = Number(startId);
      const to = Number(endId);
      if (!Number.isInteger(from) || !Number.isInteger(to)) {
        throw new Error('起止视频 ID 必须是整数');
      }
      if (to < from) {
        throw new Error('结束视频 ID 不能小于起始视频 ID');
      }

      saveTemplate({ ...template, d: duration });

      for (let videoId = from; videoId <= to; videoId += 1) {
        setStatus(`正在提交视频 ${videoId}`);
        await postHeartbeat(template, context, videoId, duration);
        setStatus(`视频 ${videoId} 提交成功`);
        if (videoId < to && waitMs > 0) {
          await sleep(waitMs);
        }
      }

      setStatus(`完成，共提交 ${to - from + 1} 个视频`);
    }

    saveButton.addEventListener('click', () => withLock(async () => {
      const template = parseHeartbeatCurl(curlInput.value.trim());
      saveTemplate(template);
      durationInput.value = String(template.d || DEFAULT_DURATION);
      setStatus('heartbeat 模板已保存');
    }).catch((error) => {
      setStatus(`失败：${error.message}`);
    }));

    currentButton.addEventListener('click', () => withLock(async () => {
      await runRange(context.videoId, context.videoId);
    }).catch((error) => {
      setStatus(`失败：${error.message}`);
    }));

    rangeButton.addEventListener('click', () => withLock(async () => {
      await runRange(startInput.value.trim(), endInput.value.trim());
    }).catch((error) => {
      setStatus(`失败：${error.message}`);
    }));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildPanel, { once: true });
  } else {
    buildPanel();
  }
})();
