/**
 * Pocket Cash Cards - Shared Site Header
 * Single source of truth for top navigation across all pages.
 * Edit this file once to update the header sitewide.
 */
(function () {
  var scriptEl = document.currentScript;
  var scriptSrc = (scriptEl && scriptEl.getAttribute('src')) || '';
  var baseMatch = scriptSrc.match(/^(.*?)assets\/js\/header\.js/);
  var base = baseMatch ? baseMatch[1] : '';

  var path = (window.location.pathname || '').toLowerCase();
  var active = 'home';
  if (path.indexOf('/checklists/') !== -1 || /\/checklists$/.test(path)) {
    active = 'checklists';
  } else if (/\/supplies(\.html)?$/.test(path)) {
    active = 'supplies';
  } else if (/\/shop(\.html)?$/.test(path)) {
    active = 'shop';
  } else if (/\/ardmore(\.html)?$/.test(path)) {
    active = 'ardmore';
  } else if (/\/(consignment|sell-cards)(\.html)?$/.test(path)) {
    active = 'consignment';
  }

  function desktopLinkClass(key, extra) {
    var baseCls = active === key
      ? 'text-brand-primary'
      : 'hover:text-brand-primary transition-colors';
    return extra ? baseCls + ' ' + extra : baseCls;
  }

  function mobileLinkClass(key, extra) {
    var baseCls = active === key
      ? 'block py-2 px-3 rounded-lg text-brand-primary font-bold text-sm bg-brand-primary/10'
      : 'block py-2 px-3 rounded-lg text-slate-200 hover:bg-slate-800 hover:text-brand-primary font-bold text-sm';
    return extra ? baseCls + ' ' + extra : baseCls;
  }

  function ariaCurrent(key) {
    return active === key ? ' aria-current="page"' : '';
  }

  var ebayUrl = 'https://ebay.us/dpjwTn';

  var affText = active === 'shop'
    ? 'As an eBay Partner Network Affiliate, Pocket Cash earns from qualifying purchases.'
    : 'As an eBay Partner Network Affiliate and Amazon Associate, Pocket Cash earns from qualifying purchases.';

  var headerHtml = [
    '<header id="pcSiteHeader" class="sticky top-0 z-50 bg-brand-navy/95 backdrop-blur-lg border-b border-brand-border">',
    '  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">',
    '    <a href="' + base + 'index.html" class="flex items-center space-x-3 shrink-0 group">',
    '      <img src="' + base + 'assets/images/logo.png" alt="Pocket Cash Cards Logo" class="h-12 sm:h-14 w-auto object-contain group-hover:scale-105 transition-transform duration-300">',
    '    </a>',
    '',
    '    <!-- Desktop Nav -->',
    '    <nav aria-label="Primary navigation" class="hidden lg:flex items-center gap-4 xl:gap-7 text-xs xl:text-sm font-bold text-slate-200 whitespace-nowrap">',
    '      <a href="' + base + 'index.html" class="' + desktopLinkClass('home') + '"' + ariaCurrent('home') + '>Home</a>',
    '      <a href="' + base + 'checklists/index.html" class="' + desktopLinkClass('checklists') + '"' + ariaCurrent('checklists') + '>Checklists &amp; Guides</a>',
    '      <a href="' + base + 'supplies.html" class="' + desktopLinkClass('supplies') + '"' + ariaCurrent('supplies') + '>Shop Supplies</a>',
    '      <a href="' + base + 'shop.html" class="' + desktopLinkClass('shop', 'flex items-center gap-1.5') + '"' + ariaCurrent('shop') + '>',
    '        <span>Shop</span>',
    '        <span class="text-[10px] bg-brand-primary/20 text-brand-primary font-bold px-1.5 py-0.5 rounded-full border border-brand-primary/30">Live</span>',
    '      </a>',
    '      <a href="' + base + 'ardmore.html" class="' + desktopLinkClass('ardmore') + '"' + ariaCurrent('ardmore') + '>Ardmore Shop</a>',
    '      <a href="' + base + 'consignment.html" class="' + (active === 'consignment' ? 'text-brand-primary' : 'text-amber-300 hover:text-amber-200 transition-colors') + ' flex items-center gap-1.5 font-black"' + ariaCurrent('consignment') + '>',
    '        <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>',
    '        <span>Local Consignment</span>',
    '        <span class="hidden xl:inline-block text-[10px] bg-amber-400/20 text-amber-300 font-bold px-1.5 py-0.5 rounded-full border border-amber-400/30">Keep up to 85%</span>',
    '      </a>',
    '      <a href="' + ebayUrl + '" target="_blank" rel="sponsored noopener noreferrer" class="text-brand-secondary hover:text-brand-secondaryHover transition-colors flex items-center gap-1">',
    '        <span>eBay Store</span>',
    '        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>',
    '      </a>',
    '    </nav>',
    '',
    '    <!-- Mobile Menu Button -->',
    '    <button id="pcMobileMenuBtn" type="button" aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="pcMobileMenu" class="lg:hidden p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-brand-primary">',
    '      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">',
    '        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>',
    '      </svg>',
    '    </button>',
    '  </div>',
    '',
    '  <!-- Mobile Drawer -->',
    '  <div id="pcMobileMenu" class="hidden lg:hidden bg-brand-navy border-b border-brand-border px-4 pt-3 pb-5 space-y-2">',
    '    <a href="' + base + 'index.html" class="' + mobileLinkClass('home') + '"' + ariaCurrent('home') + '>Home</a>',
    '    <a href="' + base + 'checklists/index.html" class="' + mobileLinkClass('checklists', 'flex items-center justify-between') + '"' + ariaCurrent('checklists') + '>',
    '      <span>Checklists &amp; Guides</span>',
    '      <span class="text-[10px] bg-brand-primary/20 text-brand-primary font-mono px-2 py-0.5 rounded-full border border-brand-primary/30">96 Sets</span>',
    '    </a>',
    '    <a href="' + base + 'supplies.html" class="' + mobileLinkClass('supplies', 'flex items-center justify-between') + '"' + ariaCurrent('supplies') + '>',
    '      <span>Shop Supplies</span>',
    '      <span class="text-[10px] bg-brand-primary/20 text-brand-primary font-mono px-2 py-0.5 rounded-full border border-brand-primary/30">Archival Gear</span>',
    '    </a>',
    '    <a href="' + base + 'shop.html" class="' + mobileLinkClass('shop', 'flex items-center justify-between') + '"' + ariaCurrent('shop') + '>',
    '      <span>Shop</span>',
    '      <span class="text-[10px] bg-brand-primary/20 text-brand-primary font-bold px-1.5 py-0.5 rounded-full border border-brand-primary/30">Live</span>',
    '    </a>',
    '    <a href="' + base + 'ardmore.html" class="' + mobileLinkClass('ardmore') + '"' + ariaCurrent('ardmore') + '>Ardmore Retail Shop</a>',
    '    <a href="' + base + 'consignment.html" class="' + (active === 'consignment' ? 'block py-2 px-3 rounded-lg text-brand-primary font-bold text-sm bg-brand-primary/10 flex items-center justify-between' : 'block py-2 px-3 rounded-lg text-amber-300 hover:bg-slate-800 font-bold text-sm flex items-center justify-between') + '"' + ariaCurrent('consignment') + '>',
    '      <span>Local eBay Consignment</span>',
    '      <span class="text-[10px] bg-amber-400/20 text-amber-300 font-bold px-1.5 py-0.5 rounded-full border border-amber-400/30">Keep up to 85%</span>',
    '    </a>',
    '    <a href="' + ebayUrl + '" target="_blank" rel="sponsored noopener noreferrer" class="block py-2 px-3 rounded-lg bg-brand-secondary/15 text-brand-secondary hover:bg-brand-secondary/25 font-bold text-sm">',
    '      Shop Daily eBay Drops ↗',
    '    </a>',
    '  </div>',
    '</header>',
    '<div aria-label="Affiliate disclosure" class="bg-slate-950/90 border-b border-brand-border/50 px-4 py-1 text-center text-[11px] text-slate-400">',
    '  <span><strong class="text-brand-cream">Affiliate Disclosure:</strong> ' + affText + '</span>',
    '</div>'
  ].join('\n');

  if (scriptEl && scriptEl.parentNode) {
    scriptEl.insertAdjacentHTML('afterend', headerHtml);
  } else if (document.body) {
    document.body.insertAdjacentHTML('afterbegin', headerHtml);
  }

  var btn = document.getElementById('pcMobileMenuBtn');
  var menu = document.getElementById('pcMobileMenu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var isHidden = menu.classList.toggle('hidden');
      btn.setAttribute('aria-expanded', isHidden ? 'false' : 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.classList.contains('hidden')) {
        menu.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }
})();
