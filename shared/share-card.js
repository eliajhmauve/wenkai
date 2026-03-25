/**
 * ShareCard — Canvas 分享卡生成模組
 * 多模板 + 品牌浮水印 + Web Share API
 */
const ShareCard = (() => {
  const BRAND = '福青施老師';
  const BRAND_URL = 'eliajhmauve.github.io/wenkai';
  const COLORS = {
    bg: '#060708',
    bgAlt: '#0f1012',
    gold: '#c9a84c',
    goldLight: '#dfc06a',
    text: '#e8e4dc',
    textDim: '#706b62',
    accent: '#1a1610'
  };

  /**
   * 建立 Canvas 並設定 DPR
   */
  function createCanvas(w, h) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const canvas = document.createElement('canvas');
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return { canvas, ctx, w, h };
  }

  /**
   * 自動換行繪製文字
   */
  function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    const lines = [];
    let currentLine = '';
    for (const char of text) {
      const testLine = currentLine + char;
      if (ctx.measureText(testLine).width > maxWidth && currentLine) {
        lines.push(currentLine);
        currentLine = char;
      } else {
        currentLine = testLine;
      }
    }
    if (currentLine) lines.push(currentLine);
    lines.forEach((line, i) => {
      ctx.fillText(line, x, y + i * lineHeight);
    });
    return lines.length;
  }

  /**
   * 繪製圓角矩形
   */
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  /**
   * 繪製品牌浮水印
   */
  function drawWatermark(ctx, w, h) {
    ctx.save();
    ctx.font = '11px "Noto Sans TC", sans-serif';
    ctx.fillStyle = 'rgba(201, 168, 76, 0.35)';
    ctx.textAlign = 'center';
    ctx.fillText(`${BRAND} | ${BRAND_URL}`, w / 2, h - 16);
    ctx.restore();
  }

  /**
   * 繪製裝飾邊框
   */
  function drawBorder(ctx, w, h, padding = 16) {
    ctx.save();
    ctx.strokeStyle = 'rgba(201, 168, 76, 0.15)';
    ctx.lineWidth = 1;
    roundRect(ctx, padding, padding, w - padding * 2, h - padding * 2, 8);
    ctx.stroke();
    // 四角裝飾
    const cornerLen = 20;
    ctx.strokeStyle = COLORS.gold;
    ctx.lineWidth = 1.5;
    [[padding, padding, 1, 1], [w - padding, padding, -1, 1],
     [padding, h - padding, 1, -1], [w - padding, h - padding, -1, -1]
    ].forEach(([x, y, dx, dy]) => {
      ctx.beginPath();
      ctx.moveTo(x, y + cornerLen * dy);
      ctx.lineTo(x, y);
      ctx.lineTo(x + cornerLen * dx, y);
      ctx.stroke();
    });
    ctx.restore();
  }

  // ========== 模板 ==========

  /**
   * 模板 1：經典語錄卡（適用經文、金句）
   */
  function templateQuote({ title = '', content = '', source = '', category = '' }) {
    const { canvas, ctx, w, h } = createCanvas(600, 400);
    // 背景
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, '#0a0b0d');
    grad.addColorStop(1, '#121014');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    drawBorder(ctx, w, h);

    // 分類標籤
    if (category) {
      ctx.font = '500 12px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.gold;
      ctx.textAlign = 'center';
      ctx.fillText(category, w / 2, 52);
    }

    // 引號裝飾
    ctx.font = '60px serif';
    ctx.fillStyle = 'rgba(201, 168, 76, 0.12)';
    ctx.textAlign = 'center';
    ctx.fillText('\u201C', w / 2, 100);

    // 內容
    ctx.font = '400 18px "Noto Serif TC", serif';
    ctx.fillStyle = COLORS.text;
    ctx.textAlign = 'center';
    const contentLines = wrapText(ctx, content, w / 2, 130, w - 100, 32);

    // 來源
    const sourceY = 130 + contentLines * 32 + 24;
    ctx.font = '400 13px "Noto Sans TC", sans-serif';
    ctx.fillStyle = COLORS.textDim;
    ctx.fillText(source, w / 2, sourceY);

    // 分隔線
    ctx.strokeStyle = COLORS.gold;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(w / 2 - 30, sourceY + 16);
    ctx.lineTo(w / 2 + 30, sourceY + 16);
    ctx.stroke();

    // 標題
    if (title) {
      ctx.font = '700 14px "Noto Serif TC", serif';
      ctx.fillStyle = COLORS.goldLight;
      ctx.fillText(title, w / 2, sourceY + 42);
    }

    drawWatermark(ctx, w, h);
    return canvas;
  }

  /**
   * 模板 2：資訊卡（適用運勢、分析結果）
   */
  function templateInfo({ title = '', items = [], footer = '' }) {
    const cardH = Math.max(420, 120 + items.length * 50 + 60);
    const { canvas, ctx, w, h } = createCanvas(600, cardH);

    // 背景
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, w, h);

    // 頂部金色漸層帶
    const topGrad = ctx.createLinearGradient(0, 0, w, 0);
    topGrad.addColorStop(0, 'rgba(201,168,76,0.05)');
    topGrad.addColorStop(0.5, 'rgba(201,168,76,0.12)');
    topGrad.addColorStop(1, 'rgba(201,168,76,0.05)');
    ctx.fillStyle = topGrad;
    ctx.fillRect(0, 0, w, 80);

    drawBorder(ctx, w, h);

    // 標題
    ctx.font = '700 22px "Noto Serif TC", serif';
    ctx.fillStyle = COLORS.gold;
    ctx.textAlign = 'center';
    ctx.fillText(title, w / 2, 52);

    // 項目列表
    items.forEach((item, i) => {
      const y = 110 + i * 50;
      // label
      ctx.font = '400 13px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.textDim;
      ctx.textAlign = 'left';
      ctx.fillText(item.label, 50, y);
      // value
      ctx.font = '500 15px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.text;
      ctx.textAlign = 'right';
      ctx.fillText(item.value, w - 50, y);
      // 分隔線
      if (i < items.length - 1) {
        ctx.strokeStyle = 'rgba(255,255,255,0.04)';
        ctx.lineWidth = 0.5;
        ctx.beginPath();
        ctx.moveTo(50, y + 18);
        ctx.lineTo(w - 50, y + 18);
        ctx.stroke();
      }
    });

    // 底部
    if (footer) {
      ctx.font = '400 12px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.textDim;
      ctx.textAlign = 'center';
      ctx.fillText(footer, w / 2, h - 40);
    }

    drawWatermark(ctx, w, h);
    return canvas;
  }

  /**
   * 模板 3：評分卡（適用星座運勢、多維度評分）
   */
  function templateScore({ title = '', scores = [], summary = '', date = '' }) {
    const { canvas, ctx, w, h } = createCanvas(600, 500);

    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, w, h);
    drawBorder(ctx, w, h);

    // 日期
    if (date) {
      ctx.font = '400 12px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.textDim;
      ctx.textAlign = 'center';
      ctx.fillText(date, w / 2, 46);
    }

    // 標題
    ctx.font = '700 24px "Noto Serif TC", serif';
    ctx.fillStyle = COLORS.gold;
    ctx.textAlign = 'center';
    ctx.fillText(title, w / 2, 78);

    // 評分條
    scores.forEach((s, i) => {
      const y = 120 + i * 56;
      const barX = 160;
      const barW = 340;
      const barH = 8;

      // 標籤
      ctx.font = '400 14px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.text;
      ctx.textAlign = 'left';
      ctx.fillText(s.label, 50, y + 4);

      // 分數
      ctx.font = '700 14px "Noto Sans TC", sans-serif';
      ctx.fillStyle = COLORS.gold;
      ctx.textAlign = 'right';
      ctx.fillText(`${s.score}/100`, w - 40, y + 4);

      // 背景條
      roundRect(ctx, barX, y + 14, barW, barH, 4);
      ctx.fillStyle = 'rgba(255,255,255,0.05)';
      ctx.fill();

      // 填充條
      const fillW = (s.score / 100) * barW;
      if (fillW > 0) {
        const barGrad = ctx.createLinearGradient(barX, 0, barX + fillW, 0);
        barGrad.addColorStop(0, COLORS.gold);
        barGrad.addColorStop(1, COLORS.goldLight);
        roundRect(ctx, barX, y + 14, fillW, barH, 4);
        ctx.fillStyle = barGrad;
        ctx.fill();
      }
    });

    // 摘要
    if (summary) {
      const summaryY = 120 + scores.length * 56 + 20;
      ctx.font = '400 14px "Noto Serif TC", serif';
      ctx.fillStyle = COLORS.text;
      ctx.textAlign = 'center';
      wrapText(ctx, summary, w / 2, summaryY, w - 100, 26);
    }

    drawWatermark(ctx, w, h);
    return canvas;
  }

  // ========== 匯出功能 ==========

  /**
   * Canvas → PNG Blob
   */
  function toBlob(canvas) {
    return new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
  }

  /**
   * 下載 PNG
   */
  async function download(canvas, filename = 'share-card.png') {
    const blob = await toBlob(canvas);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Web Share API（fallback 為下載）
   */
  async function share(canvas, { title = '', text = '', filename = 'share-card.png' } = {}) {
    const blob = await toBlob(canvas);
    const file = new File([blob], filename, { type: 'image/png' });

    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({ title, text, files: [file] });
        return true;
      } catch (e) {
        if (e.name !== 'AbortError') {
          await download(canvas, filename);
        }
        return false;
      }
    } else {
      await download(canvas, filename);
      return false;
    }
  }

  /**
   * 預覽分享卡（插入到容器）
   */
  function preview(canvas, container) {
    container.innerHTML = '';
    canvas.style.maxWidth = '100%';
    canvas.style.height = 'auto';
    canvas.style.borderRadius = '8px';
    container.appendChild(canvas);
  }

  return {
    templateQuote,
    templateInfo,
    templateScore,
    toBlob,
    download,
    share,
    preview,
    createCanvas,
    wrapText,
    roundRect,
    drawBorder,
    drawWatermark,
    COLORS
  };
})();
