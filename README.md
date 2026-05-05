<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>E-commerce Product Data Classifier</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0e17;--surface:#111827;--surface2:#1a2235;--border:#1e2d47;
  --accent:#00d4ff;--accent2:#7c3aed;--accent3:#10b981;--accent4:#f59e0b;
  --text:#e2e8f0;--muted:#64748b;
  --mono:'JetBrains Mono',monospace;--sans:'Sora',sans-serif;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.6}
.wrap{max-width:900px;margin:0 auto;padding:3rem 2rem}

/* Hero */
.hero{position:relative;padding:3rem 0 2.5rem;border-bottom:1px solid var(--border);margin-bottom:2.5rem}
.badge-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1.5rem}
.badge{font-family:var(--mono);font-size:11px;padding:3px 10px;border-radius:20px;letter-spacing:.04em}
.badge-blue{background:#0c1e35;color:#38bdf8;border:1px solid #1e4060}
.badge-purple{background:#1e1035;color:#a78bfa;border:1px solid #3d1f6e}
.badge-green{background:#0a2218;color:#34d399;border:1px solid #14432e}
.badge-amber{background:#251700;color:#fbbf24;border:1px solid #4a3000}
h1{font-size:2.4rem;font-weight:600;letter-spacing:-.03em;line-height:1.1;margin-bottom:.75rem}
h1 span{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-size:1rem;color:var(--muted);line-height:1.7;max-width:620px;font-weight:300}

/* Stats */
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:2.5rem 0}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem 1.1rem}
.stat-num{font-family:var(--mono);font-size:1.5rem;font-weight:600;color:var(--accent);line-height:1}
.stat-label{font-size:11.5px;color:var(--muted);margin-top:5px;letter-spacing:.02em}

/* Section headers */
.section{margin-bottom:2.5rem}
.sec-head{display:flex;align-items:center;gap:10px;margin-bottom:1.2rem;font-size:.7rem;font-family:var(--mono);color:var(--muted);letter-spacing:.12em;text-transform:uppercase}
.sec-head::after{content:'';flex:1;height:1px;background:var(--border)}

/* Pipeline */
.pipeline{display:grid;gap:2px}
.pipe-step{display:grid;grid-template-columns:28px 1fr;gap:14px;align-items:start;padding:14px 16px;background:var(--surface);border:1px solid var(--border);border-radius:8px;transition:.15s}
.pipe-step:hover{border-color:var(--accent2);background:var(--surface2)}
.pipe-num{font-family:var(--mono);font-size:11px;font-weight:600;color:var(--accent2);padding-top:2px}
.pipe-module{font-family:var(--mono);font-size:12px;color:var(--accent);margin-bottom:3px}
.pipe-desc{font-size:13px;color:var(--text);opacity:.85;line-height:1.5}
.pipe-tag{display:inline-block;font-family:var(--mono);font-size:10px;margin-top:5px;padding:2px 8px;border-radius:4px;background:#0a1a2e;color:#60a5fa;border:1px solid #1e3a5f}

/* Grid layouts */
.cols2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.cols3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.2rem}
.card-title{font-size:12px;font-weight:500;color:var(--muted);margin-bottom:.7rem;font-family:var(--mono);letter-spacing:.05em}

/* Categories */
.cat-item{display:flex;align-items:flex-start;gap:8px;margin-bottom:8px}
.dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;margin-top:6px}
.cat-name{font-size:13px;font-weight:500;color:var(--text);line-height:1.4}
.cat-sub{font-size:11px;color:var(--muted);line-height:1.4}

/* Classifier flow */
.flow-wrap{display:flex;align-items:center;gap:4px;flex-wrap:wrap;margin:0 0 .5rem}
.flow-box{font-family:var(--mono);font-size:11px;padding:4px 10px;border-radius:5px;white-space:nowrap}
.flow-arrow{color:var(--muted);font-size:12px}
.conf-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:.5rem}
.conf-item{border-radius:7px;padding:.7rem;text-align:center}
.conf-label{font-family:var(--mono);font-size:11px;font-weight:600}
.conf-desc{font-size:10px;margin-top:3px;opacity:.7}

/* CLI */
.cli-row{display:flex;flex-direction:column;gap:8px}
.cli-cmd{background:#080d14;border:1px solid var(--border);border-radius:7px;padding:10px 14px;font-family:var(--mono);font-size:12.5px;display:flex;align-items:flex-start;gap:10px}
.cli-prompt{color:#3a5068;flex-shrink:0}
.cli-text{color:var(--text);line-height:1.7}
.arg{color:var(--accent4)}
.str{color:var(--accent3)}
.cli-comment{color:#3a5068}

/* Output table */
.cols-table{width:100%;border-collapse:collapse;font-size:12.5px}
.cols-table th{text-align:left;padding:8px 12px;font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--muted);border-bottom:1px solid var(--border);font-weight:400}
.cols-table td{padding:7px 12px;border-bottom:1px solid #0f1a2b;vertical-align:top;line-height:1.4}
.cols-table tr:last-child td{border-bottom:none}
.td-col{font-family:var(--mono);font-size:11.5px;color:var(--accent)}
.td-src{font-size:11px;padding:2px 7px;border-radius:4px;background:#1a2235;color:var(--muted);white-space:nowrap}
.td-desc{color:#94a3b8}

/* Tech stack */
.tech-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.tech-pill{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.6rem .8rem;text-align:center}
.tech-name{font-family:var(--mono);font-size:12px;color:var(--text);font-weight:600}
.tech-note{font-size:10px;color:var(--muted);margin-top:3px}

/* Extensions */
.ext-row{display:flex;flex-direction:column;gap:6px}
.ext-item{display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--surface);border:1px solid var(--border);border-radius:7px;font-size:13px}
.ext-icon{font-family:var(--mono);font-size:10px;padding:2px 7px;border-radius:4px;background:#1e1035;color:#a78bfa;border:1px solid #3d1f6e;white-space:nowrap}
.ext-text{color:#94a3b8}

/* Inline code */
code{background:#111827;padding:1px 5px;border-radius:3px;color:#00d4ff;font-size:11.5px;font-family:var(--mono)}

/* Footer */
footer{border-top:1px solid var(--border);padding-top:1.5rem;margin-top:2rem;display:flex;align-items:center;justify-content:space-between}
.footer-badge{font-family:var(--mono);font-size:11px;padding:4px 12px;border-radius:20px;background:#0a1e10;color:#34d399;border:1px solid #14432e}
.footer-lic{font-size:12px;color:var(--muted)}

/* File tree */
.tree{font-family:var(--mono);font-size:12px;line-height:1.9;color:#94a3b8;background:#080d14;border:1px solid var(--border);border-radius:8px;padding:1.2rem 1.4rem}
.tree .dir{color:#38bdf8}
.tree .file{color:#94a3b8}
.tree .comment{color:#3a5068}

/* Input table */
.input-table{width:100%;border-collapse:collapse;font-size:12.5px}
.input-table th{text-align:left;padding:8px 12px;font-family:var(--mono);font-size:10px;letter-spacing:.08em;color:var(--muted);border-bottom:1px solid var(--border);font-weight:400}
.input-table td{padding:7px 12px;border-bottom:1px solid #0f1a2b;font-family:var(--mono);font-size:11.5px}
.input-table tr:last-child td{border-bottom:none}
.req-yes{color:#34d399}
.req-no{color:#3a5068}

@media(max-width:700px){
  .stats-row{grid-template-columns:repeat(2,1fr)}
  .cols2{grid-template-columns:1fr}
  .tech-grid{grid-template-columns:repeat(3,1fr)}
  .conf-grid{grid-template-columns:repeat(2,1fr)}
  h1{font-size:1.7rem}
}
</style>
</head>
<body>
<div class="wrap">

  <!-- Hero -->
  <div class="hero">
    <div class="badge-row">
      <span class="badge badge-blue">Python 3.9+</span>
      <span class="badge badge-green">41 unit tests</span>
      <span class="badge badge-purple">rule-based NLP</span>
      <span class="badge badge-amber">MIT license</span>
      <span class="badge badge-blue">pandas · numpy · re</span>
    </div>
    <h1>E-commerce Product<br><span>Data Classifier</span></h1>
    <p class="hero-sub">A production-grade ETL pipeline that ingests raw, messy product records — cleans, classifies, extracts attributes, and scores every record for data quality. No ML dependencies. Fully auditable rule-based logic.</p>
  </div>

  <!-- Stats -->
  <div class="stats-row">
    <div class="stat"><div class="stat-num">1200+</div><div class="stat-label">synthetic records generated</div></div>
    <div class="stat"><div class="stat-num">98%+</div><div class="stat-label">classification rate</div></div>
    <div class="stat"><div class="stat-num">~8%</div><div class="stat-label">duplicates removed</div></div>
    <div class="stat"><div class="stat-num">28</div><div class="stat-label">enriched output columns</div></div>
  </div>

  <!-- Pipeline -->
  <div class="section">
    <div class="sec-head">Pipeline</div>
    <div class="pipeline">
      <div class="pipe-step">
        <div class="pipe-num">01</div>
        <div>
          <div class="pipe-module">data_generator.py</div>
          <div class="pipe-desc">Generates 1200+ realistic, intentionally messy product records with randomized junk values and near-duplicates</div>
          <span class="pipe-tag">synthetic · seeded</span>
        </div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">02</div>
        <div>
          <div class="pipe-module">cleaner.py</div>
          <div class="pipe-desc">Removes exact &amp; near-duplicates, nullifies 1600+ junk placeholders ("N/A", "TBD", "???"), coerces types, standardizes fields</div>
          <span class="pipe-tag">dedup · normalize · coerce</span>
        </div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">03</div>
        <div>
          <div class="pipe-module">classifier.py</div>
          <div class="pipe-desc">Keyword-score classifier across 8 categories / 35 subcategories / 300+ keywords — every decision logged with its score</div>
          <span class="pipe-tag">rule-based · auditable · fallback</span>
        </div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">04</div>
        <div>
          <div class="pipe-module">extractor.py</div>
          <div class="pipe-desc">Regex extraction of brand, RAM, storage, size, color, and model from raw product name strings</div>
          <span class="pipe-tag">regex · RAM vs storage disambiguation</span>
        </div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">05</div>
        <div>
          <div class="pipe-module">quality_checker.py</div>
          <div class="pipe-desc">Composite 0–100 quality score. Flags each record as GOOD / ACCEPTABLE / POOR with human-readable issue list</div>
          <span class="pipe-tag">scoring · QA · reporting</span>
        </div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">06</div>
        <div>
          <div class="pipe-module">pipeline.py</div>
          <div class="pipe-desc">Orchestrates all steps, writes enriched CSV + poor-quality CSV, saves JSON quality report</div>
          <span class="pipe-tag">orchestrator · CLI · entry point</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Project structure -->
  <div class="section">
    <div class="sec-head">Project structure</div>
    <div class="tree">
<span class="dir">ecommerce-classifier/</span>
├── <span class="file">main.py</span>                         <span class="comment"># CLI entry point</span>
├── <span class="file">requirements.txt</span>
├── <span class="file">setup.py</span>
├── <span class="file">.gitignore</span>
│
├── <span class="dir">src/</span>
│   ├── <span class="file">__init__.py</span>
│   ├── <span class="file">data_generator.py</span>           <span class="comment"># Synthetic data generation</span>
│   ├── <span class="file">cleaner.py</span>                  <span class="comment"># Data cleaning pipeline</span>
│   ├── <span class="file">classifier.py</span>               <span class="comment"># Rule-based taxonomy classifier</span>
│   ├── <span class="file">extractor.py</span>                <span class="comment"># Regex attribute extraction</span>
│   ├── <span class="file">quality_checker.py</span>          <span class="comment"># Quality scoring and reporting</span>
│   └── <span class="file">pipeline.py</span>                 <span class="comment"># Main orchestrator</span>
│
├── <span class="dir">data/</span>
│   ├── <span class="dir">raw/</span>                        <span class="comment"># Raw input CSVs (git-ignored)</span>
│   ├── <span class="dir">processed/</span>                  <span class="comment"># Cleaned output CSVs (git-ignored)</span>
│   └── <span class="dir">taxonomy/</span>
│       └── <span class="file">taxonomy.json</span>           <span class="comment"># Category → subcategory → keywords</span>
│
├── <span class="dir">reports/</span>
│   └── <span class="file">quality_report.json</span>         <span class="comment"># QA summary (generated at runtime)</span>
│
└── <span class="dir">tests/</span>
    ├── <span class="file">test_cleaner.py</span>             <span class="comment"># 15 unit tests</span>
    ├── <span class="file">test_classifier.py</span>          <span class="comment"># 11 unit tests</span>
    └── <span class="file">test_extractor.py</span>           <span class="comment"># 15 unit tests</span>
    </div>
  </div>

  <!-- Quickstart -->
  <div class="section">
    <div class="sec-head">Quickstart</div>
    <div class="cli-row">
      <div class="cli-cmd">
        <span class="cli-prompt">$</span>
        <div class="cli-text">
          git clone <span class="str">https://github.com/YOUR_USERNAME/ecommerce-classifier.git</span><br>
          cd ecommerce-classifier &amp;&amp; pip install <span class="arg">-r</span> requirements.txt
        </div>
      </div>
      <div class="cli-cmd">
        <span class="cli-prompt">$</span>
        <div class="cli-text">python main.py <span class="cli-comment"># auto-generates 1200 records &amp; runs all 5 steps</span></div>
      </div>
      <div class="cli-cmd">
        <span class="cli-prompt">$</span>
        <div class="cli-text">python main.py <span class="arg">--input</span> <span class="str">path/to/your_products.csv</span> <span class="cli-comment"># use your own data</span></div>
      </div>
      <div class="cli-cmd">
        <span class="cli-prompt">$</span>
        <div class="cli-text">
          python main.py <span class="arg">--n</span> <span class="str">5000</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="cli-comment"># generate 5000 records</span><br>
          python main.py <span class="arg">--no-generate</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="cli-comment"># fail if raw CSV missing</span><br>
          python main.py <span class="arg">--taxonomy</span> <span class="str">custom.json</span> &nbsp;&nbsp;&nbsp;<span class="cli-comment"># custom taxonomy file</span>
        </div>
      </div>
      <div class="cli-cmd">
        <span class="cli-prompt">$</span>
        <div class="cli-text">pytest tests/ <span class="arg">-v</span> <span class="cli-comment"># run 41 unit tests</span></div>
      </div>
    </div>
  </div>

  <!-- Input columns -->
  <div class="section">
    <div class="sec-head">Input schema (required &amp; optional columns)</div>
    <table class="input-table">
      <thead><tr><th>Column</th><th>Required</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td>product_id</td><td class="req-yes">yes</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Unique record ID</td></tr>
        <tr><td>sku</td><td class="req-yes">yes</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Stock keeping unit</td></tr>
        <tr><td>product_name</td><td class="req-yes">yes</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Raw product name string</td></tr>
        <tr><td>brand</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Brand name (can be missing/junk)</td></tr>
        <tr><td>category</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Existing label (used as fallback)</td></tr>
        <tr><td>price</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Numeric price</td></tr>
        <tr><td>size</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Size string</td></tr>
        <tr><td>color</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Color string</td></tr>
        <tr><td>stock_quantity</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Integer stock count</td></tr>
        <tr><td>rating</td><td class="req-no">no</td><td style="color:#94a3b8;font-family:var(--sans);font-size:12.5px">Float 1.0–5.0</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Taxonomy + Classifier -->
  <div class="section">
    <div class="sec-head">Taxonomy — 8 categories · 35 subcategories · 300+ keywords</div>
    <div class="cols2">
      <div class="card">
        <div class="card-title">Categories</div>
        <div class="cat-item"><div class="dot" style="background:#00d4ff"></div><div><div class="cat-name">Electronics</div><div class="cat-sub">Mobile Phones, Laptops, Tablets, Headphones, Cameras, Televisions, Accessories</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#7c3aed"></div><div><div class="cat-name">Clothing</div><div class="cat-sub">Men's, Women's, Kids', Activewear, Winter Wear, Innerwear</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#10b981"></div><div><div class="cat-name">Footwear</div><div class="cat-sub">Sports, Casual, Formal, Sandals, Boots</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#f59e0b"></div><div><div class="cat-name">Home &amp; Kitchen</div><div class="cat-sub">Cookware, Appliances, Furniture, Bedding, Storage</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#ec4899"></div><div><div class="cat-name">Beauty &amp; Personal Care</div><div class="cat-sub">Skincare, Haircare, Makeup, Fragrances, Bath &amp; Body</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#ef4444"></div><div><div class="cat-name">Sports &amp; Fitness</div><div class="cat-sub">Gym Equipment, Sports Accessories, Outdoor, Yoga &amp; Wellness</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#60a5fa"></div><div><div class="cat-name">Books &amp; Stationery</div><div class="cat-sub">Books, Stationery, Art Supplies</div></div></div>
        <div class="cat-item"><div class="dot" style="background:#a78bfa"></div><div><div class="cat-name">Toys &amp; Games</div><div class="cat-sub">Educational Toys, Action Figures, Board Games</div></div></div>
      </div>
      <div class="card">
        <div class="card-title">Classifier logic</div>
        <div class="flow-wrap">
          <div class="flow-box" style="background:#0a1a2e;color:#38bdf8;border:1px solid #1e4060">product_name</div>
          <span class="flow-arrow">+</span>
          <div class="flow-box" style="background:#1e1035;color:#a78bfa;border:1px solid #3d1f6e">subcategory</div>
          <span class="flow-arrow">+</span>
          <div class="flow-box" style="background:#0a2218;color:#34d399;border:1px solid #14432e">brand</div>
          <span class="flow-arrow">→</span>
          <div class="flow-box" style="background:#251700;color:#fbbf24;border:1px solid #4a3000">text corpus</div>
        </div>
        <p style="font-size:12.5px;color:#94a3b8;line-height:1.7;margin-top:.5rem">Score every <code>(category, subcategory)</code> pair by counting whole-word keyword hits via regex. Pick highest score. Falls back to existing label if score is zero.</p>
        <div style="margin-top:1rem"><div class="card-title">Confidence levels</div></div>
        <div class="conf-grid">
          <div class="conf-item" style="background:#0a2218;border:1px solid #14432e"><div class="conf-label" style="color:#34d399">high</div><div class="conf-desc" style="color:#34d399">≥ 3 hits</div></div>
          <div class="conf-item" style="background:#0c1e35;border:1px solid #1e4060"><div class="conf-label" style="color:#38bdf8">medium</div><div class="conf-desc" style="color:#38bdf8">2 hits</div></div>
          <div class="conf-item" style="background:#251700;border:1px solid #4a3000"><div class="conf-label" style="color:#fbbf24">low</div><div class="conf-desc" style="color:#fbbf24">1 hit</div></div>
          <div class="conf-item" style="background:#1a0a0a;border:1px solid #3d1515"><div class="conf-label" style="color:#f87171">none</div><div class="conf-desc" style="color:#f87171">0 → fallback</div></div>
        </div>
        <p style="margin-top:1rem;font-size:11.5px;color:#3a5068;font-family:var(--mono)">Taxonomy is pure JSON — add a category with no code changes.</p>
      </div>
    </div>
  </div>

  <!-- Output columns -->
  <div class="section">
    <div class="sec-head">Output columns (28 total)</div>
    <table class="cols-table">
      <thead><tr><th>Column</th><th>Source</th><th>Description</th></tr></thead>
      <tbody>
        <tr><td class="td-col">product_id · sku · product_name</td><td><span class="td-src">Raw</span></td><td class="td-desc">Original identifiers, unchanged</td></tr>
        <tr><td class="td-col">brand · category · subcategory</td><td><span class="td-src">Cleaner</span></td><td class="td-desc">Standardized and normalized</td></tr>
        <tr><td class="td-col">price · stock_quantity · rating</td><td><span class="td-src">Cleaner</span></td><td class="td-desc">Coerced to correct types</td></tr>
        <tr><td class="td-col">cleaning_notes</td><td><span class="td-src">Cleaner</span></td><td class="td-desc">Human-readable log of what was fixed per record</td></tr>
        <tr><td class="td-col">has_missing_critical</td><td><span class="td-src">Cleaner</span></td><td class="td-desc">True if name / SKU / price is absent</td></tr>
        <tr><td class="td-col">classified_category · classified_subcategory</td><td><span class="td-src">Classifier</span></td><td class="td-desc">Taxonomy predictions</td></tr>
        <tr><td class="td-col">classification_confidence</td><td><span class="td-src">Classifier</span></td><td class="td-desc">high / medium / low / none</td></tr>
        <tr><td class="td-col">classification_reason</td><td><span class="td-src">Classifier</span></td><td class="td-desc">Keyword score or fallback reason — fully auditable</td></tr>
        <tr><td class="td-col">extracted_brand · extracted_ram · extracted_storage</td><td><span class="td-src">Extractor</span></td><td class="td-desc">Regex-parsed from product name</td></tr>
        <tr><td class="td-col">extracted_size · extracted_color · extracted_model</td><td><span class="td-src">Extractor</span></td><td class="td-desc">e.g. "XL", "Midnight Blue", "WH-1000XM5"</td></tr>
        <tr><td class="td-col">name_cleaned</td><td><span class="td-src">Extractor</span></td><td class="td-desc">Lowercased, whitespace-normalized name</td></tr>
        <tr><td class="td-col">quality_score</td><td><span class="td-src">QA</span></td><td class="td-desc">Composite 0–100 score</td></tr>
        <tr><td class="td-col">quality_issues</td><td><span class="td-src">QA</span></td><td class="td-desc">Pipe-separated issue flags for manual review</td></tr>
        <tr><td class="td-col">quality_tier</td><td><span class="td-src">QA</span></td><td class="td-desc">GOOD / ACCEPTABLE / POOR</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Tests -->
  <div class="section">
    <div class="sec-head">Tests — 41 unit tests across 3 files</div>
    <div class="cols3">
      <div class="card">
        <div class="card-title">test_cleaner.py — 15 tests</div>
        <p style="font-size:12.5px;color:#94a3b8;line-height:1.7">Junk value detection &amp; nullification, exact and near-duplicate removal, price / rating / stock coercion</p>
      </div>
      <div class="card">
        <div class="card-title">test_classifier.py — 11 tests</div>
        <p style="font-size:12.5px;color:#94a3b8;line-height:1.7">Keyword classification for 6+ product types, confidence level assignment, fallback behavior</p>
      </div>
      <div class="card">
        <div class="card-title">test_extractor.py — 15 tests</div>
        <p style="font-size:12.5px;color:#94a3b8;line-height:1.7">RAM vs storage disambiguation, volume &amp; apparel size extraction, model code regex, color normalization</p>
      </div>
    </div>
  </div>

  <!-- Tech stack -->
  <div class="section">
    <div class="sec-head">Tech stack</div>
    <div class="tech-grid">
      <div class="tech-pill"><div class="tech-name">pandas</div><div class="tech-note">data manipulation</div></div>
      <div class="tech-pill"><div class="tech-name">numpy</div><div class="tech-note">numeric ops</div></div>
      <div class="tech-pill"><div class="tech-name">re</div><div class="tech-note">regex extraction</div></div>
      <div class="tech-pill"><div class="tech-name">json</div><div class="tech-note">taxonomy loading</div></div>
      <div class="tech-pill"><div class="tech-name">pytest</div><div class="tech-note">41 unit tests</div></div>
    </div>
    <p style="font-size:12px;color:var(--muted);margin-top:.8rem;font-family:var(--mono)">No ML dependencies. Every classification decision is interpretable and logged.</p>
  </div>

  <!-- Extending -->
  <div class="section">
    <div class="sec-head">Extending this project</div>
    <div class="ext-row">
      <div class="ext-item"><span class="ext-icon">ML</span><span class="ext-text">Replace <code>classifier.py</code> with a fine-tuned model via <code>sentence-transformers</code> + cosine similarity against category descriptions</span></div>
      <div class="ext-item"><span class="ext-icon">API</span><span class="ext-text">Wrap <code>pipeline.py</code> in FastAPI — expose <code>/classify</code> and <code>/clean</code> endpoints for real-time enrichment</span></div>
      <div class="ext-item"><span class="ext-icon">DB</span><span class="ext-text">Replace CSV output in <code>pipeline.py</code> with a SQLAlchemy write to PostgreSQL or any RDBMS</span></div>
      <div class="ext-item"><span class="ext-icon">DATA</span><span class="ext-text">Point <code>--input</code> at a Shopify, WooCommerce, or any PIM system export CSV — no code changes needed</span></div>
    </div>
  </div>

  <!-- Footer -->
  <footer>
    <span class="footer-badge">MIT license</span>
    <span class="footer-lic">ecommerce-classifier · Python 3.9+ · no ML dependencies</span>
  </footer>

</div>
</body>
</html>
