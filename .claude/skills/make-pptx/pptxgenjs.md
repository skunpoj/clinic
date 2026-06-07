# PptxGenJS — Create Presentations from Scratch

## Setup & Basic Structure

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';  // or 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE'
pres.author = 'Your Name';
pres.title = 'Presentation Title';

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "Presentation.pptx" });
```

## Layout Dimensions (coordinates in inches)

- `LAYOUT_16x9`: 10" × 5.625" (default)
- `LAYOUT_16x10`: 10" × 6.25"
- `LAYOUT_4x3`: 10" × 7.5"
- `LAYOUT_WIDE`: 13.3" × 7.5"

---

## Text & Formatting

```javascript
// Basic text
slide.addText("Simple Text", {
  x: 1, y: 1, w: 8, h: 2, fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true, align: "center", valign: "middle"
});

// Character spacing (use charSpacing, not letterSpacing — silently ignored)
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });

// Rich text arrays
slide.addText([
  { text: "Bold ", options: { bold: true } },
  { text: "Italic ", options: { italic: true } }
], { x: 1, y: 3, w: 8, h: 1 });

// Multi-line text (requires breakLine: true)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }
], { x: 0.5, y: 0.5, w: 8, h: 2 });

// Text box margin — set margin: 0 when aligning with shapes
slide.addText("Title", { x: 0.5, y: 0.3, w: 9, h: 0.6, margin: 0 });
```

---

## Lists & Bullets

```javascript
// ✅ CORRECT
slide.addText([
  { text: "First item",  options: { bullet: true, breakLine: true } },
  { text: "Second item", options: { bullet: true, breakLine: true } },
  { text: "Third item",  options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// ❌ WRONG — never use unicode bullets (creates double bullets)
slide.addText("• First item", { ... });

// Sub-items and numbered lists
{ text: "Sub-item", options: { bullet: true, indentLevel: 1 } }
{ text: "First",    options: { bullet: { type: "number" }, breakLine: true } }
```

---

## Shapes

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" }, line: { color: "000000", width: 2 }
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "0088CC", transparency: 50 }
});

// With shadow — use makeShadow() factory to avoid object-mutation bugs
const makeShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 });
slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 3, h: 2, fill: { color: "FFFFFF" }, shadow: makeShadow() });
```

Shadow properties:

| Property | Range | Notes |
|----------|-------|-------|
| `type` | `"outer"`, `"inner"` | |
| `color` | 6-char hex, no `#` | e.g. `"000000"` |
| `blur` | 0-100 pt | |
| `offset` | 0-200 pt | **Must be non-negative** |
| `angle` | 0-359 degrees | 135 = bottom-right, 270 = upward |
| `opacity` | 0.0-1.0 | Never encode opacity in color string |

---

## Images

```javascript
// From file path
slide.addImage({ path: "images/chart.png", x: 1, y: 1, w: 5, h: 3 });

// From URL
slide.addImage({ path: "https://example.com/image.jpg", x: 1, y: 1, w: 5, h: 3 });

// From base64
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });

// Sizing modes
{ sizing: { type: 'contain', w: 4, h: 3 } }  // fit inside, preserve ratio
{ sizing: { type: 'cover',   w: 4, h: 3 } }  // fill area, may crop
```

---

## Icons (react-icons → PNG)

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle } = require("react-icons/fa");

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);
slide.addImage({ data: iconData, x: 1, y: 1, w: 0.5, h: 0.5 });
```

Install: `npm install -g react-icons react react-dom sharp`

---

## Charts

```javascript
// Modern bar chart
slide.addChart(pres.charts.BAR, [{
  name: "Series", labels: ["A", "B", "C"], values: [40, 60, 80]
}], {
  x: 0.5, y: 1, w: 9, h: 4, barDir: "col",
  chartColors: ["0D9488", "14B8A6"],
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },
  catAxisLabelColor: "64748B",
  valAxisLabelColor: "64748B",
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },
  showValue: true,
  dataLabelColor: "1E293B",
  showLegend: false,
});
```

---

## Common Pitfalls

1. **NEVER use `#` with hex colors** — causes file corruption
   ```javascript
   color: "FF0000"   // ✅
   color: "#FF0000"  // ❌
   ```

2. **NEVER encode opacity in hex color strings** — use `opacity` property
   ```javascript
   shadow: { color: "00000020" }              // ❌ corrupts file
   shadow: { color: "000000", opacity: 0.12 } // ✅
   ```

3. **NEVER use unicode bullets** — use `bullet: true`

4. **NEVER reuse option objects across calls** — PptxGenJS mutates them in-place
   ```javascript
   const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
   // Call makeShadow() fresh for every shape
   ```

5. **Don't use `ROUNDED_RECTANGLE` with rectangular accent overlays** — corners won't align; use `RECTANGLE` instead

6. **Don't use `lineSpacing` with bullets** — use `paraSpaceAfter` instead

---

## Quick Reference

- **Shapes**: `RECTANGLE`, `OVAL`, `LINE`, `ROUNDED_RECTANGLE`
- **Charts**: `BAR`, `LINE`, `PIE`, `DOUGHNUT`, `SCATTER`
- **Layouts**: `LAYOUT_16x9` (10"×5.625"), `LAYOUT_WIDE` (13.3"×7.5")
- **Alignment**: `"left"`, `"center"`, `"right"`
