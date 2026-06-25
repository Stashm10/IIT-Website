<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IIT Spectrum Observatory</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #fff;
      color: #1a1a1a;
      font-family: Arial, Helvetica, sans-serif;
      min-height: 100vh;
    }

    /* ════════════════════════════════════════════════════════
       SITE-WIDE STICKY HEADER (institutional nav)
       Variables are scoped to .site-header so they never clash
       with the --ink / --base-red / etc. tokens used below for
       the allocation chart.
       ════════════════════════════════════════════════════════ */
    .site-header{
      --red: #cc0000;
      --red-dark: #a30000;
      --hdr-ink: #222;
      --hdr-bg: #f4f4f4;
      --h-top: 40px;
      --h-logo: 96px;
      --h-nav: 52px;

      position: sticky;
      top: 0;
      z-index: 150;
      background:#fff;
      font-family: "Source Sans Pro", Arial, Helvetica, sans-serif;
      color: var(--hdr-ink);
      transition: box-shadow .25s ease;
    }
    .site-header.is-scrolled{
      box-shadow: 0 2px 10px rgba(0,0,0,.15);
    }

    /* row 1: utility bar */
    .site-header .utility-bar{
      background: var(--hdr-bg);
      border-bottom: 1px solid #e0e0e0;
      height: var(--h-top);
      overflow: hidden;
      transition: height .25s ease, opacity .2s ease;
    }
    .site-header .utility-bar ul{
      list-style:none; display:flex; gap:20px; height:100%; align-items:center;
      justify-content:flex-end; padding:0 24px;
    }
    .site-header .utility-bar a{
      color:#444; text-decoration:none; font-size:.78rem; letter-spacing:.02em;
    }
    .site-header .utility-bar a:hover{ color: var(--red); text-decoration:underline; }
    .site-header.is-scrolled .utility-bar{ height:0; opacity:0; border-bottom:none; }

    /* row 2: logo + scrolled CTAs */
    .site-header .logo-row{
      height: var(--h-logo);
      display:flex; align-items:center; justify-content:space-between;
      padding: 0 24px;
      transition: height .25s ease;
    }
    .site-header.is-scrolled .logo-row{ height:64px; }

    .site-header .logo{
      display:flex; align-items:center; gap:8px;
      text-decoration:none; font-weight:800; letter-spacing:.02em;
      font-size: 1.9rem; color:#111;
      transition: font-size .25s ease;
    }
    .site-header.is-scrolled .logo{ font-size: 1.25rem; }
    .site-header .logo .accent{ color: var(--red); }

    .site-header .scrolled-actions{ display:none; align-items:center; gap:10px; }
    .site-header.is-scrolled .scrolled-actions{ display:flex; }

    .site-header .btn-cta{
      background: var(--red); color:#fff; border:none;
      padding:10px 16px; font-size:.85rem; font-weight:600;
      text-decoration:none; cursor:pointer; border-radius:2px;
    }
    .site-header .btn-cta:hover{ background: var(--red-dark); }

    .site-header .hamburger{
      background:none; border:none; cursor:pointer;
      width:32px; height:24px; position:relative;
    }
    .site-header .hamburger span,
    .site-header .hamburger span::before,
    .site-header .hamburger span::after{
      content:""; position:absolute; left:0; width:100%; height:3px;
      background:#222; transition:.2s;
    }
    .site-header .hamburger span{ top:50%; transform:translateY(-50%); }
    .site-header .hamburger span::before{ top:-9px; }
    .site-header .hamburger span::after{ top:9px; }

    /* row 3: red nav bar */
    .site-header .main-nav{
      background: var(--red);
      height: var(--h-nav);
      overflow:hidden;
      transition: height .25s ease, opacity .2s ease;
    }
    .site-header.is-scrolled .main-nav{ height:0; opacity:0; }
    .site-header .main-nav ul{
      list-style:none; display:flex; gap:4px; height:100%; align-items:center;
      padding:0 24px;
    }
    .site-header .main-nav li{ position:relative; height:100%; display:flex; align-items:center; }

    .site-header .nav-link, .site-header .nav-trigger{
      background:none; border:none; color:#fff; font-size:.95rem;
      font-weight:600; padding:10px 14px; cursor:pointer;
      text-decoration:none; display:flex; align-items:center; gap:6px;
      height:100%; font-family: inherit;
    }
    .site-header .nav-trigger::after{ content:"▾"; font-size:.7em; }
    .site-header .nav-link:hover, .site-header .nav-trigger:hover{ background: rgba(255,255,255,.15); }

    .site-header .sr-only{
      position:absolute; width:1px; height:1px; overflow:hidden;
      clip:rect(0,0,0,0); white-space:nowrap;
    }

    .site-header .search-btn{
      margin-left:auto; background:none; border:none; color:#fff;
      cursor:pointer; font-size:1.1rem;
    }

    .site-header .dropdown-panel{
      position:absolute; top:100%; left:0; background:#fff;
      color:#222; min-width:220px; box-shadow:0 8px 20px rgba(0,0,0,.18);
      padding:12px 0; display:none; z-index:50;
    }
    .site-header .dropdown-panel.open{ display:block; }
    .site-header .dropdown-panel a{
      display:block; padding:8px 18px; color:#222; text-decoration:none; font-size:.9rem;
    }
    .site-header .dropdown-panel a:hover{ background: var(--hdr-bg); color: var(--red); }

    .site-header .mobile-menu{
      display:none; position:absolute; top:100%; right:0; background:#fff;
      box-shadow:0 8px 20px rgba(0,0,0,.18); width:260px; padding:10px 0;
    }
    .site-header .mobile-menu.open{ display:block; }
    .site-header .mobile-menu a{ display:block; padding:10px 18px; color:#222; text-decoration:none; font-size:.92rem; }
    .site-header .mobile-menu a:hover{ background:var(--hdr-bg); color:var(--red); }

    @media (prefers-reduced-motion: reduce){
      .site-header, .site-header .utility-bar, .site-header .logo-row,
      .site-header .logo, .site-header .main-nav{ transition:none !important; }
    }

    /* ── Page banner (was the bare <header>, renamed so it no longer
       collides with the new institutional <header class="site-header">) ── */
    .page-banner {
      background: #fff;
      border-bottom: 3px solid #CC0000;
      padding: 1.25rem 2rem;
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }
    .iit-badge {
      background: #CC0000;
      color: #fff;
      font-weight: 900;
      font-size: 1.1rem;
      padding: 0.25rem 0.6rem;
      border-radius: 3px;
      letter-spacing: 0.05em;
      flex-shrink: 0;
    }
    .header-text h1 {
      font-size: 1.3rem;
      font-weight: 700;
      color: #1a1a1a;
      line-height: 1.2;
    }
    .header-text .subtitle {
      font-size: 0.8rem;
      color: #555;
      margin-top: 2px;
      letter-spacing: 0.02em;
    }

    /* ── Main layout ── */
    main {
      max-width: 1280px;
      margin: 0 auto;
      padding: 1.5rem 1.5rem 4rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    /* ── Section header ── */
    .section-title {
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #555;
      border-bottom: 1px solid #ddd;
      padding-bottom: 0.4rem;
      margin-bottom: 0.75rem;
    }

    /* ── Intro text ── */
    .intro {
      font-size: 0.85rem;
      color: #444;
      line-height: 1.6;
      max-width: 780px;
    }

    /* ── Allocation chart ── */
    :root {
      --ink: #171717;
      --line: #1c1c1c;
      --mobile: #e8cfdf;
      --fixed: #d4147f;
      --land-mobile: #0d9ca2;
      --amateur: #07906b;
      --radio-astronomy: #fff200;
      --base-red: #df334d;
      --base-green: #12a779;
      --black: #1b1b1b;
    }

    .chart-shell {
      overflow-x: auto;
      padding: 18px 36px 8px;
    }

    .chart {
      min-width: 1180px;
      position: relative;
      padding-top: 76px;
    }

    .ticks {
      position: absolute;
      inset: 0 0 auto 0;
      height: 76px;
      border-bottom: 4px solid var(--line);
      pointer-events: none;
    }

    .tick {
      position: absolute;
      bottom: 18px;
      transform: translateX(-50%) rotate(-90deg);
      transform-origin: center;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
    }

    .grid {
      display: flex;
      height: 365px;
      border: 4px solid var(--line);
      border-top: 0;
      background: #fff;
    }

    .column {
      appearance: none;
      display: grid;
      grid-template-rows: 44% 50% 6%;
      min-width: 22px;
      padding: 0;
      border: 0;
      border-right: 1px solid rgba(0,0,0,.7);
      background: transparent;
      cursor: pointer;
      color: var(--ink);
      transition: filter .12s ease, transform .12s ease;
    }

    .column:last-child { border-right: 0; }

    .column:hover {
      filter: brightness(1.07) saturate(1.08);
    }

    .column:focus-visible {
      outline: 4px solid #000;
      outline-offset: -8px;
      z-index: 3;
    }

    .cell {
      position: relative;
      display: grid;
      place-items: center;
      overflow: hidden;
      border-bottom: 1px solid rgba(0,0,0,.55);
    }

    .cell:last-child { border-bottom: 0; }

    .bg-mobile { background: var(--mobile); }
    .bg-fixed { background: var(--fixed); }
    .bg-land-mobile { background: var(--land-mobile); }
    .bg-amateur { background: var(--amateur); }
    .bg-radio-astronomy { background: var(--radio-astronomy); }
    .bg-base-red { background: var(--base-red); }
    .bg-base-green { background: var(--base-green); }
    .bg-black { background: var(--black); color: #fff; }

    .chart-label {
      display: block;
      max-width: 320px;
      font-size: clamp(12px, 1.15vw, 18px);
      line-height: 1;
      text-align: center;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .chart-label.vertical {
      transform: rotate(-90deg);
      transform-origin: center;
    }

    .chart-label.small { font-size: 13px; }
    .chart-label.tiny { font-size: 11px; }
    .chart-label.micro { font-size: 9px; }
    .chart-label.normal { text-transform: none; }

    .column[data-center="true"] .cell {
      justify-items: center;
      align-items: center;
    }

    .column[data-center="true"] .chart-label.vertical {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%) rotate(-90deg);
    }

    .below {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: start;
      gap: 20px;
      min-width: 1180px;
      padding-top: 16px;
      font-family: Georgia, "Times New Roman", serif;
    }

    .mhz {
      font-size: 44px;
      line-height: 1;
    }

    .ism {
      align-self: center;
      font-size: 23px;
      font-weight: 800;
      letter-spacing: 3px;
      white-space: nowrap;
    }

    /* ── Card ── */
    .card {
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 1.25rem 1.5rem;
    }

    /* ── Stats grid ── */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 0.75rem;
    }
    .stat-item {
      background: #f8f8f8;
      border: 1px solid #e0e0e0;
      border-radius: 3px;
      padding: 0.75rem 1rem;
    }
    .stat-label {
      font-size: 0.65rem;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      margin-bottom: 0.25rem;
    }
    .stat-value {
      font-size: 1.2rem;
      font-weight: 700;
      color: #1a1a1a;
    }
    .stat-unit { font-size: 0.7rem; color: #666; margin-left: 2px; }
    .stat-note { font-size: 0.65rem; color: #777; margin-top: 0.25rem; line-height: 1.4; }

    /* ── Loading ── */
    #loading-overlay {
      position: fixed; inset: 0;
      background: rgba(255,255,255,0.9);
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      z-index: 200; gap: 1rem;
      transition: opacity 0.3s;
    }
    #loading-overlay.hidden { opacity: 0; pointer-events: none; }
    .spinner {
      width: 40px; height: 40px;
      border: 3px solid #ddd;
      border-top-color: #CC0000;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    #loading-overlay p { font-size: 0.85rem; color: #666; }

    .caption {
      font-size: 0.75rem;
      color: #666;
      line-height: 1.5;
      margin-top: 0.75rem;
    }

    @media (max-width: 640px) {
      .page-banner { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
      .card { padding: 1rem; }
    }
  </style>
</head>
<body>

<div id="loading-overlay">
  <div class="spinner"></div>
  <p>Loading spectrum data…</p>
</div>

<!-- ════════════════════════════════════════════════════════
     SITE-WIDE STICKY HEADER (institutional nav)
     ════════════════════════════════════════════════════════ -->
<header class="site-header" id="siteHeader">

  <!-- row 1: utility links — each opens in a NEW TAB -->
  <div class="utility-bar">
    <ul>
      <li><a href="https://www.iit.edu/directory" target="_blank" rel="noopener">Directory</a></li>
      <li><a href="https://www.iit.edu/news" target="_blank" rel="noopener">News</a></li>
      <li><a href="https://www.iit.edu/alumni" target="_blank" rel="noopener">Alumni</a></li>
      <li><a href="https://www.iit.edu/events" target="_blank" rel="noopener">Events</a></li>
      <li><a href="https://www.iit.edu/giving" target="_blank" rel="noopener">Giving</a></li>
      <li><a href="https://www.iit.edu/mumbai" target="_blank" rel="noopener">Illinois Tech Mumbai</a></li>
      <li><a href="https://www.iit.edu/resources" target="_blank" rel="noopener">Resources for...</a></li>
    </ul>
  </div>

  <!-- row 2: logo (click -> home page) + scrolled-state CTAs -->
  <div class="logo-row">
    <a class="logo" href="https://www.iit.edu/" aria-label="Illinois Tech home page">
      <span class="accent">ILLINOIS</span><span>TECH</span>
    </a>

    <div class="scrolled-actions">
      <a class="btn-cta" href="https://www.iit.edu/admission-and-aid/request-info" target="_blank" rel="noopener">Request Info</a>
      <a class="btn-cta" href="https://www.iit.edu/visit" target="_blank" rel="noopener">Visit</a>
      <a class="btn-cta" href="https://www.iit.edu/apply" target="_blank" rel="noopener">Apply</a>
      <button class="hamburger" id="hamburgerBtn" aria-expanded="false" aria-controls="mobileMenu" aria-label="Open main menu">
        <span></span>
      </button>
    </div>
  </div>

  <!-- row 3: red nav bar -->
  <nav class="main-nav" aria-label="Primary">
    <ul>
      <li>
        <button class="nav-trigger" aria-expanded="false" aria-controls="panel-academics" data-menu="academics">
          Academics <span class="sr-only">Open the Academics menu</span>
        </button>
        <div class="dropdown-panel" id="panel-academics">
          <a href="/academics/undergraduate">Undergraduate Programs</a>
          <a href="/academics/graduate">Graduate Programs</a>
          <a href="/academics/colleges">Colleges</a>
        </div>
      </li>
      <li>
        <button class="nav-trigger" aria-expanded="false" aria-controls="panel-admission" data-menu="admission">
          Admission and Aid <span class="sr-only">Open the Admission and Aid menu</span>
        </button>
        <div class="dropdown-panel" id="panel-admission">
          <a href="/admission-and-aid/undergraduate">Undergraduate Admission</a>
          <a href="/admission-and-aid/graduate">Graduate Admission</a>
          <a href="/admission-and-aid/financial-aid">Financial Aid</a>
        </div>
      </li>
      <li>
        <button class="nav-trigger" aria-expanded="false" aria-controls="panel-student" data-menu="student">
          Student Experience <span class="sr-only">Open the Student Experience menu</span>
        </button>
        <div class="dropdown-panel" id="panel-student">
          <a href="/student-experience/housing">Housing</a>
          <a href="/student-experience/clubs">Clubs &amp; Organizations</a>
          <a href="/student-experience/athletics">Athletics</a>
        </div>
      </li>
      <li>
        <button class="nav-trigger" aria-expanded="false" aria-controls="panel-research" data-menu="research">
          Research <span class="sr-only">Open the Research menu</span>
        </button>
        <div class="dropdown-panel" id="panel-research">
          <a href="/research/centers">Research Centers</a>
          <a href="/research/faculty">Faculty Research</a>
        </div>
      </li>
      <li><a class="nav-link" href="/about">About</a></li>
      <li><button class="search-btn" aria-label="Open search">🔍</button></li>
    </ul>
  </nav>

  <!-- condensed menu shown via hamburger once scrolled -->
  <div class="mobile-menu" id="mobileMenu">
    <a href="/academics">Academics</a>
    <a href="/admission-and-aid">Admission and Aid</a>
    <a href="/student-experience">Student Experience</a>
    <a href="/research">Research</a>
    <a href="/about">About</a>
    <a href="https://www.iit.edu/directory" target="_blank" rel="noopener">Directory</a>
    <a href="https://www.iit.edu/news" target="_blank" rel="noopener">News</a>
  </div>

</header>

<!-- ════════════════════════════════════════════════════════
     PAGE BANNER (was the original bare <header>) — introduces
     this specific page, sits below the institutional nav.
     ════════════════════════════════════════════════════════ -->
<div class="page-banner">
  <span class="iit-badge">IIT</span>
  <div class="header-text">
    <h1>Spectrum Observatory — 30–54 MHz</h1>
    <div class="subtitle">Illinois Institute of Technology &nbsp;·&nbsp; Chicago, IL &nbsp;·&nbsp; January 1, 2018</div>
  </div>
</div>

<main>

  <p class="intro">
    Real radio frequency spectrum measurements collected by the IIT Spectrum Observatory,
    located on the rooftop of IIT Tower at 10 W. 35th Street, Chicago. Click any allocation
    segment below to explore its power distribution, spectrogram, and data matrix.
  </p>

  <!-- Allocation chart -->
  <div>
    <div class="section-title">Frequency Allocation — 30 to 54 MHz (NTIA)</div>
    <section class="chart-shell" aria-label="30 to 54 MHz frequency allocation chart">
      <div class="chart">
        <div class="ticks" aria-hidden="true">
          <span class="tick" style="left: 0%">30.0</span>
          <span class="tick" style="left: 2.333%">30.56</span>
          <span class="tick" style="left: 8.333%">32.0</span>
          <span class="tick" style="left: 12.5%">33.0</span>
          <span class="tick" style="left: 16.667%">34.0</span>
          <span class="tick" style="left: 20.833%">35.0</span>
          <span class="tick" style="left: 25%">36.0</span>
          <span class="tick" style="left: 29.167%">37.0</span>
          <span class="tick" style="left: 31.25%">37.5</span>
          <span class="tick" style="left: 33.333%">38.0</span>
          <span class="tick" style="left: 34.375%">38.25</span>
          <span class="tick" style="left: 37.5%">39.0</span>
          <span class="tick" style="left: 41.667%">40.0</span>
          <span class="tick" style="left: 50%">42.0</span>
          <span class="tick" style="left: 57.042%">43.69</span>
          <span class="tick" style="left: 69.167%">46.6</span>
          <span class="tick" style="left: 70.833%">47.0</span>
          <span class="tick" style="left: 81.667%">49.6</span>
          <span class="tick" style="left: 83.333%">50.0</span>
          <span class="tick" style="left: 100%">54.0</span>
        </div>

        <div class="grid">
          <button class="column" data-center="true" style="flex: 0.56" onclick="window.location.href='/square/mobile_30.0_30.56'">
            <span class="cell bg-mobile"><span class="chart-label vertical">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" style="flex: 1.44" onclick="window.location.href='/square/land_mobile_30.56_32.0'">
            <span class="cell bg-land-mobile"><span class="chart-label vertical">Land Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" style="flex: 1" onclick="window.location.href='/square/mobile_32.0_33.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" data-center="true" style="flex: 1" onclick="window.location.href='/square/land_mobile_33.0_34.0'">
            <span class="cell bg-land-mobile"><span class="chart-label vertical">Land Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" style="flex: 1" onclick="window.location.href='/square/mobile_34.0_35.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" data-center="true" style="flex: 1" onclick="window.location.href='/square/land_mobile_35.0_36.0'">
            <span class="cell bg-land-mobile"><span class="chart-label vertical">Land Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" style="flex: 1" onclick="window.location.href='/square/mobile_36.0_37.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" data-center="true" style="flex: .5" onclick="window.location.href='/square/land_mobile_fixed_37.0_37.5'">
            <span class="cell bg-land-mobile" style="grid-row: 1 / 3;">
              <span class="chart-label vertical small">Land Mobile</span>
            </span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" data-center="true" style="flex: .5" onclick="window.location.href='/square/fixed_37.5_38.0'">
            <span class="cell bg-land-mobile"><span class="chart-label vertical small">Land Mobile</span></span>
            <span class="cell bg-radio-astronomy"><span class="chart-label vertical small normal">Radio astronomy</span></span>
            <span class="cell bg-black"></span>
          </button>

          <button class="column" data-center="true" style="flex: .25; grid-template-rows: 28% 25% 47%;" onclick="window.location.href='/square/radio_astronomy_38.0_38.25'">
            <span class="cell bg-fixed"><span class="chart-label vertical tiny">Fixed</span></span>
            <span class="cell bg-mobile"><span class="chart-label vertical tiny">Mobile</span></span>
            <span class="cell bg-radio-astronomy"><span class="chart-label vertical micro">RADIO ASTRONOMY</span></span>
          </button>

          <button class="column" style="flex: .75" onclick="window.location.href='/square/land_mobile_38.25_39.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" data-center="true" style="flex: 1" onclick="window.location.href='/square/land_mobile_39.0_40.0'">
            <span class="cell bg-land-mobile" style="grid-row: 1 / 3;">
              <span class="chart-label vertical">Land Mobile</span>
            </span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" style="flex: 2" onclick="window.location.href='/square/mobile_40.0_42.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" style="flex: 1.69" onclick="window.location.href='/square/land_mobile_42.0_43.69'">
            <span class="cell bg-land-mobile"><span class="chart-label vertical">Land Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical">Fixed</span></span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" style="flex: 2.91" onclick="window.location.href='/square/mobile_43.69_46.6'">
            <span class="cell bg-land-mobile" style="grid-row: 1 / 3;">
              <span class="chart-label vertical">Land Mobile</span>
            </span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" data-center="true" style="flex: .4" onclick="window.location.href='/square/land_mobile_46.6_47.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical small">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical small">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" style="flex: 2.6" onclick="window.location.href='/square/mobile_47.0_49.6'">
            <span class="cell bg-land-mobile" style="grid-row: 1 / 3;">
              <span class="chart-label vertical">Land Mobile</span>
            </span>
            <span class="cell bg-base-green"></span>
          </button>

          <button class="column" data-center="true" style="flex: .4" onclick="window.location.href='/square/mobile_49.6_50.0'">
            <span class="cell bg-mobile"><span class="chart-label vertical small">Mobile</span></span>
            <span class="cell bg-fixed"><span class="chart-label vertical small">Fixed</span></span>
            <span class="cell bg-base-red"></span>
          </button>

          <button class="column" style="flex: 4" onclick="window.location.href='/square/amateur_50.0_54.0'">
            <span class="cell bg-amateur" style="grid-row: 1 / 4;">
              <span class="chart-label normal" style="font-size: 20px;">Amateur</span>
            </span>
          </button>
        </div>

        <div class="below">
          <div class="mhz">30 MHz</div>
          <div class="ism">ISM - 40.68 <small>+-.02 MHz</small></div>
          <div></div>
        </div>
      </div>
    </section>
  </div>

  <!-- Histogram -->
  <div class="card">
    <div class="section-title">Power Distribution — Full Band (30–54 MHz)</div>
    <div id="histogram"></div>
    <p class="caption">
      Distribution of all ~984,000 power readings across the full 30–54 MHz band.
      Click any allocation segment above to see its specific distribution.
    </p>
  </div>

  <!-- Heatmap -->
  <div class="card">
    <div class="section-title">Spectrogram — Power vs. Time and Frequency</div>
    <div id="heatmap"></div>
  </div>

  <!-- Stats -->
  <div class="card">
    <div class="section-title">Summary Statistics — Full Band</div>
    <div class="stats-grid" id="stats-grid"></div>
  </div>

</main>

<script>
// ════════════════════════════════════════════════════════
// STICKY HEADER BEHAVIOR
// ════════════════════════════════════════════════════════
(function(){
  const header    = document.getElementById('siteHeader');
  const hamburger = document.getElementById('hamburgerBtn');
  const mobileMenu = document.getElementById('mobileMenu');

  // 1. toggle condensed style on scroll
  const SCROLL_THRESHOLD = 60;
  let ticking = false;
  function onScroll(){
    if (!ticking){
      requestAnimationFrame(() => {
        header.classList.toggle('is-scrolled', window.scrollY > SCROLL_THRESHOLD);
        ticking = false;
      });
      ticking = true;
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  // 2. dropdown menus (Academics / Admission and Aid / Student Experience / Research)
  const triggers = document.querySelectorAll('.nav-trigger');
  function closeAllPanels(except){
    triggers.forEach(btn => {
      if (btn === except) return;
      btn.setAttribute('aria-expanded', 'false');
      document.getElementById(btn.getAttribute('aria-controls')).classList.remove('open');
    });
  }
  triggers.forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = document.getElementById(btn.getAttribute('aria-controls'));
      const isOpen = panel.classList.contains('open');
      closeAllPanels(btn);
      panel.classList.toggle('open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  // 3. hamburger menu (condensed state)
  if (hamburger){
    hamburger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', String(isOpen));
    });
  }

  // 4. click outside / Escape closes everything
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.main-nav')) closeAllPanels(null);
    if (!e.target.closest('.scrolled-actions')) mobileMenu.classList.remove('open');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape'){
      closeAllPanels(null);
      mobileMenu.classList.remove('open');
    }
  });
})();
</script>

<script>
// ════════════════════════════════════════════════════════
// SPECTRUM OBSERVATORY DASHBOARD (unchanged from your original)
// ════════════════════════════════════════════════════════
const LAYOUT_BASE = {
  paper_bgcolor: "#fff",
  plot_bgcolor:  "#fff",
  font: { color: "#1a1a1a", family: "Arial, Helvetica, sans-serif", size: 11 },
  margin: { t: 20, r: 20, b: 50, l: 65 },
  xaxis: { gridcolor: "#e8e8e8", zerolinecolor: "#ccc", linecolor: "#ccc" },
  yaxis: { gridcolor: "#e8e8e8", zerolinecolor: "#ccc", linecolor: "#ccc" },
};
const CONFIG = { responsive: true, displayModeBar: false };

async function loadHistogram() {
  const res = await fetch("/api/histogram");
  const d = await res.json();
  const edges = d.edges;
  const x = edges.slice(0, -1).map((e, i) => (e + edges[i+1]) / 2);
  Plotly.react("histogram", [{
    x, y: d.counts, type: "bar",
    marker: { color: "#CC0000" },
    hovertemplate: "%{x:.1f} dBm — %{y:,}<extra></extra>",
  }], {
    ...LAYOUT_BASE,
    xaxis: { ...LAYOUT_BASE.xaxis, title: { text: "Power (dBm)" } },
    yaxis: { ...LAYOUT_BASE.yaxis, title: { text: "Count" } },
    bargap: 0,
  }, CONFIG);
}

async function loadHeatmap() {
  const res = await fetch("/api/data");
  const d = await res.json();
  Plotly.react("heatmap", [{
    z: d.powers, x: d.freqs, y: d.timestamps,
    type: "heatmap",
    colorscale: "Viridis",
    colorbar: { title: { text: "dBm", side: "right" }, tickfont: { color: "#333" } },
    hovertemplate: "Freq: %{x:.2f} MHz<br>Time: %{y}<br>Power: %{z:.1f} dBm<extra></extra>",
  }], {
    ...LAYOUT_BASE,
    margin: { t: 20, r: 80, b: 50, l: 80 },
    xaxis: { ...LAYOUT_BASE.xaxis, title: { text: "Frequency (MHz)" }, range: [30, 54] },
    yaxis: { ...LAYOUT_BASE.yaxis, title: { text: "Time (Chicago)" }, autorange: "reversed" },
  }, CONFIG);
}

async function loadStats() {
  const res = await fetch("/api/stats");
  const d = await res.json();
  const items = [
    { label: "Frequency Range", value: "30–54", unit: "MHz" },
    { label: "Sweeps", value: d.num_sweeps },
    { label: "Min Power", value: d.min_power.toFixed(1), unit: "dBm" },
    { label: "Max Power", value: d.max_power.toFixed(1), unit: "dBm" },
    { label: "Mean Power", value: d.mean_power.toFixed(1), unit: "dBm" },
    { label: "Noise Floor (p10)", value: d.noise_floor.toFixed(1), unit: "dBm" },
    { label: "Spectral Occupancy", value: d.occupancy_pct.toFixed(1), unit: "%",
      note: "% of readings exceeding noise floor by >6 dB" },
  ];
  document.getElementById("stats-grid").innerHTML = items.map(it => `
    <div class="stat-item">
      <div class="stat-label">${it.label}</div>
      <div class="stat-value">${it.value}${it.unit ? `<span class="stat-unit">${it.unit}</span>` : ""}</div>
      ${it.note ? `<div class="stat-note">${it.note}</div>` : ""}
    </div>`).join("");
}

async function boot() {
  try {
    await Promise.all([loadHistogram(), loadHeatmap(), loadStats()]);
  } finally {
    const o = document.getElementById("loading-overlay");
    o.classList.add("hidden");
    setTimeout(() => o.remove(), 400);
  }
}
boot();
</script>
</body>
</html>
