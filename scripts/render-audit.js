/**
 * render-audit.js — the checks that only a rendered page can answer.
 *
 * WHY THIS EXISTS
 * scripts/check_page.py reads the HTML file. It cannot compute a colour
 * contrast, measure a table against its container, or see that two words fused
 * because a line break sat between text and an element. Every defect this file
 * tests for shipped to production at least once despite the build passing, the
 * static check passing, and the CSS looking correct in source.
 *
 * The rule this encodes: measure the rendered page, do not trust the source.
 *
 * HOW TO RUN IT
 * Evaluate this file in the page context (any driver — a browser tool, devtools
 * console, or Playwright's page.evaluate), then call:
 *
 *     renderAudit({ viewport: 390, jargon: ['mpd', 'blended rate'] })
 *
 * Returns { pass, failures[], warnings[], measured{} }. Failures are defects.
 * Warnings need a human to decide — a numeric table scrolling sideways may be
 * fine; a table of sentences doing it is not.
 *
 * WHAT IT DELIBERATELY CANNOT DO
 * Judge whether the title is comprehensible, whether the cover explains
 * anything, or whether a chart encodes the variable its caption claims. Those
 * were the defects that actually mattered on this site, and they need a reader.
 * The /preflight skill walks those separately. Do not mistake a green run here
 * for a publishable page.
 */
(function () {
  'use strict';

  /** Words whose internal capital is legitimate, so the fused-word test skips them. */
  var BRAND_WORDS = [
    'KrisFlyer', 'KrisShop', 'KrisPay', 'MileLion', 'ThankYou', 'ShopBack',
    'YouTrip', 'PayNow', 'SimplyGo', 'PayAll', 'CardUp', 'TheEnoughPoint',
    'MoneySmart', 'SingSaver', 'PayLah', 'GrabPay', 'AirAsia', 'JetBlue',
  ];

  function toLinear(v) {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  }

  function luminance(rgb) {
    var p = rgb.match(/[\d.]+/g);
    if (!p || p.length < 3) return null;
    return 0.2126 * toLinear(+p[0]) + 0.7152 * toLinear(+p[1]) + 0.0722 * toLinear(+p[2]);
  }

  function isTransparent(c) {
    if (!c) return true;
    if (c === 'transparent') return true;
    var m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return false;
    var parts = m[1].split(',');
    return parts.length === 4 && parseFloat(parts[3]) === 0;
  }

  function alphaOf(c) {
    var m = c && c.match(/rgba?\(([^)]+)\)/);
    if (!m) return 1;
    var parts = m[1].split(',');
    return parts.length === 4 ? parseFloat(parts[3]) : 1;
  }

  /** Composite a translucent colour over what sits behind it. */
  function blend(over, under) {
    var f = over.match(/[\d.]+/g).map(Number);
    var b = under.match(/[\d.]+/g).map(Number);
    var a = f.length === 4 ? f[3] : 1;
    return 'rgb(' + [0, 1, 2].map(function (i) {
      return Math.round(f[i] * a + b[i] * (1 - a));
    }).join(', ') + ')';
  }

  /** The colour actually behind an element.
   *
   *  Must composite, not just find. A 10%-opacity gold highlight over white
   *  renders as pale cream, but reading its raw rgba() as if it were solid made
   *  this audit report eight false contrast failures on a table row that is
   *  comfortably legible at 5.9:1. Collect every translucent layer up the tree,
   *  then flatten them back down over white. */
  function effectiveBackground(el) {
    var layers = [], node = el;
    while (node && node !== document.documentElement) {
      var bg = getComputedStyle(node).backgroundColor;
      if (!isTransparent(bg)) {
        layers.push(bg);
        if (alphaOf(bg) === 1) break;
      }
      node = node.parentElement;
    }
    var out = 'rgb(255, 255, 255)';
    for (var i = layers.length - 1; i >= 0; i--) out = blend(layers[i], out);
    return out;
  }

  function contrast(fg, bg) {
    var a = luminance(fg), b = luminance(bg);
    if (a === null || b === null) return null;
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }

  /** WCAG AA: 3.0 for large text (>=24px, or >=18.66px bold), 4.5 otherwise. */
  function requiredContrast(cs) {
    var size = parseFloat(cs.fontSize);
    var weight = parseInt(cs.fontWeight, 10) || 400;
    var large = size >= 24 || (size >= 18.66 && weight >= 700);
    return large ? 3.0 : 4.5;
  }

  function describe(el) {
    var id = el.id ? '#' + el.id : '';
    var cls = (el.className && el.className.toString().trim())
      ? '.' + el.className.toString().trim().split(/\s+/).slice(0, 2).join('.')
      : '';
    return el.tagName.toLowerCase() + id + cls;
  }

  /** The nearest ancestor that paints a surface — a card, panel or table shell.
   *  Detected by what it renders rather than by class name, so it keeps working
   *  as components are added. */
  function nearestCard(el) {
    var node = el.parentElement;
    while (node && node !== document.body) {
      var cs = getComputedStyle(node);
      if (!isTransparent(cs.backgroundColor) || parseFloat(cs.borderLeftWidth) > 0) return node;
      node = node.parentElement;
    }
    return null;
  }

  /** Does this element sit inside something allowed to scroll sideways? */
  function inScrollableAncestor(el, root) {
    var node = el.parentElement;
    while (node && node !== root && node !== document.body) {
      var ox = getComputedStyle(node).overflowX;
      if (ox === 'auto' || ox === 'scroll') return node;
      node = node.parentElement;
    }
    return null;
  }

  window.renderAudit = function renderAudit(opts) {
    opts = opts || {};
    var rootSel = opts.root || '.post-content';
    var root = document.querySelector(rootSel) || document.body;
    var jargon = opts.jargon || [];
    var brandWords = BRAND_WORDS.concat(opts.allowWords || []);
    var minGutter = opts.minGutter == null ? 6 : opts.minGutter;

    var failures = [], warnings = [], measured = {};
    var vw = window.innerWidth;
    measured.viewport = vw;

    // ---- 1. the page itself must never scroll sideways -------------------
    var docW = document.documentElement.scrollWidth;
    measured.pageScrollWidth = docW;
    if (docW > vw + 1) {
      failures.push({
        check: 'page-overflow',
        detail: 'Page scrolls horizontally: ' + docW + 'px of content in a ' + vw + 'px viewport.',
      });
    }

    // ---- 2. nothing may spill past the viewport unless a scroller holds it
    var spillers = [];
    Array.prototype.forEach.call(root.querySelectorAll('*'), function (el) {
      var r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      if (r.right > vw + 1 && !inScrollableAncestor(el, root)) {
        spillers.push({ el: describe(el), right: Math.round(r.right) });
      }
    });
    if (spillers.length) {
      failures.push({
        check: 'content-spill',
        detail: spillers.length + ' element(s) extend past the viewport with nothing to scroll them.',
        elements: spillers.slice(0, 6),
      });
    }

    // ---- 3. horizontal scrollers are a fallback, not a layout ------------
    var scrollers = [];
    Array.prototype.forEach.call(root.querySelectorAll('*'), function (el) {
      var cs = getComputedStyle(el);
      if (cs.overflowX !== 'auto' && cs.overflowX !== 'scroll') return;
      if (el.scrollWidth > el.clientWidth + 1) {
        var overflowBy = el.scrollWidth - el.clientWidth;
        var text = (el.innerText || '').trim();
        // A wide numeric table is tolerable, and so is a chart — some diagrams
        // simply cannot be squeezed below a legible width. Sentences are the
        // problem: if the average table cell holds prose, scrolling sideways
        // loses the row label. Only judge elements that ARE tables; a chart has
        // no cells, and dividing by zero classed one as prose.
        var cells = el.querySelectorAll('td,th').length;
        var prose = cells > 0 && (text.split(/\s+/).length / cells) > 6;
        scrollers.push({
          el: describe(el), clientWidth: el.clientWidth, scrollWidth: el.scrollWidth,
          overflowBy: overflowBy, looksLikeProse: prose,
        });
      }
    });
    measured.horizontalScrollers = scrollers.length;
    scrollers.forEach(function (s) {
      var msg = s.el + ' scrolls sideways by ' + s.overflowBy + 'px (' +
        s.scrollWidth + ' in ' + s.clientWidth + ').';
      if (s.looksLikeProse && vw <= 480) {
        failures.push({
          check: 'prose-scroller',
          detail: msg + ' It holds sentences, so scrolling loses the row label — reflow it into cards instead.',
        });
      } else {
        warnings.push({ check: 'horizontal-scroller', detail: msg + ' Acceptable for a wide numeric table; check it reads.' });
      }
    });

    // ---- 4. contrast, including generated markers ------------------------
    var contrastFails = [];
    function checkContrast(el, pseudo) {
      var cs = getComputedStyle(el, pseudo || null);
      if (pseudo) {
        var content = cs.content;
        if (!content || content === 'none' || content === 'normal') return;
        // Decorative pseudo-elements carry an empty string: they paint a shape,
        // not text, so their colour contrast is meaningless. Counters and real
        // strings both survive this test.
        if (content === '""' || content === "''") return;
      } else {
        var hasOwnText = Array.prototype.some.call(el.childNodes, function (n) {
          return n.nodeType === 3 && n.textContent.trim().length > 1;
        });
        if (!hasOwnText) return;
      }
      if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return;
      var bg = effectiveBackground(el);
      if (!isTransparent(cs.backgroundColor) && alphaOf(cs.backgroundColor) === 1) bg = cs.backgroundColor;
      var ratio = contrast(cs.color, bg);
      if (ratio === null) return;
      var need = requiredContrast(cs);
      if (ratio < need) {
        contrastFails.push({
          el: describe(el) + (pseudo || ''), ratio: Math.round(ratio * 100) / 100,
          required: need, color: cs.color, background: bg,
          sample: ((pseudo ? cs.content : el.textContent) || '').trim().slice(0, 40),
        });
      }
    }
    Array.prototype.forEach.call(root.querySelectorAll('*'), function (el) {
      checkContrast(el, null);
      checkContrast(el, '::before');
      checkContrast(el, '::after');
    });
    if (contrastFails.length) {
      failures.push({
        check: 'contrast',
        detail: contrastFails.length + ' element(s) below the WCAG AA minimum.',
        elements: contrastFails.slice(0, 8),
      });
    }

    // ---- 5. fused words from .astro whitespace collapse ------------------
    // Normalise non-breaking spaces explicitly, or "S$1,000 a month" can read
    // as a single token to the fused-word test.
    var text = (root.innerText || '').replace(/ /g, ' ');
    var fused = (text.match(/[a-z][.,;:!?]?[A-Z][a-z]{2,}/g) || []).filter(function (hit) {
      return !brandWords.some(function (w) { return w.indexOf(hit.replace(/[.,;:!?]/, '')) !== -1 || hit.indexOf(w) !== -1; });
    });
    fused = fused.filter(function (v, i, a) { return a.indexOf(v) === i; });
    if (fused.length) {
      failures.push({
        check: 'fused-words',
        detail: 'Words run together — usually a line break between text and an element in a .astro template. Put a space on the same line or use {\' \'}.',
        elements: fused.slice(0, 10),
      });
    }

    // ---- 6. jargon the piece said it had removed -------------------------
    if (jargon.length) {
      var found = {};
      jargon.forEach(function (w) {
        var re = new RegExp('\\b' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'gi');
        var n = (text.match(re) || []).length;
        if (n) found[w] = n;
      });
      measured.jargon = found;
      if (Object.keys(found).length) {
        failures.push({
          check: 'jargon',
          detail: 'Terms on the banned list appear in the rendered page.',
          elements: found,
        });
      }
    }

    // ---- 7. ink must not sit on a card edge ------------------------------
    // Measure where the TEXT actually lands, not the element box. A <td> with
    // its own padding legitimately starts at its container's edge while the
    // words inside are comfortably inset — measuring boxes flagged 58 such
    // cells as defects on this site's own pages. A Range gives the ink.
    var tight = [];
    Array.prototype.forEach.call(root.querySelectorAll('p, li, td, h2, h3, div'), function (el) {
      var textNode = Array.prototype.filter.call(el.childNodes, function (n) {
        return n.nodeType === 3 && n.textContent.trim().length > 1;
      })[0];
      if (!textNode) return;
      var card = nearestCard(el);
      if (!card) return;
      var range = document.createRange();
      range.selectNodeContents(textNode);
      var r = range.getBoundingClientRect();
      if (r.width === 0) return;
      var cr = card.getBoundingClientRect();
      var left = r.left - cr.left, right = cr.right - r.right;
      if (left < minGutter || right < minGutter) {
        tight.push({
          el: describe(el), card: describe(card),
          left: Math.round(left), right: Math.round(right),
          sample: textNode.textContent.trim().slice(0, 32),
        });
      }
    });
    if (tight.length) {
      warnings.push({
        check: 'tight-gutter',
        detail: tight.length + ' element(s) sit within ' + minGutter + 'px of their container edge.',
        elements: tight.slice(0, 5),
      });
    }

    // ---- 8. title length -------------------------------------------------
    var title = (document.title || '').trim();
    measured.title = title;
    measured.titleLength = title.length;
    if (title.length > 60) {
      warnings.push({
        check: 'title-length',
        detail: 'Title is ' + title.length + ' characters; search results truncate near 60. Confirm the keyword half survives.',
      });
    }

    return {
      pass: failures.length === 0,
      failures: failures,
      warnings: warnings,
      measured: measured,
    };
  };
})();
