/**
 * Pocket Cash Cards - GA4 Analytics & Conversion Tracking
 * Measurement ID: G-7S9BWRF1C4
 */

// Initialize Google Tag (gtag.js)
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-7S9BWRF1C4', {
  'send_page_view': true,
  'cookie_flags': 'SameSite=None;Secure'
});

// Outbound & Conversion Click Handler
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('a, button').forEach(el => {
    el.addEventListener('click', (e) => {
      const href = el.getAttribute('href') || '';
      const customEvent = el.dataset.gaEvent;
      const category = el.dataset.gaCategory || 'engagement';
      const label = el.dataset.gaLabel || el.innerText.trim();

      // Explicit data-ga-event tag
      if (customEvent) {
        gtag('event', customEvent, {
          event_category: category,
          event_label: label,
          link_url: href,
          transport_type: 'beacon'
        });
        return;
      }

      // Auto-detect outbound destination conversions
      if (href.includes('ebay.us') || href.includes('ebay.com')) {
        const cardParent = el.closest('.card-item');
        if (cardParent) {
          const cardNum = cardParent.getAttribute('data-number') || '';
          const cardPlayer = cardParent.getAttribute('data-player') || cardParent.getAttribute('data-name') || '';
          const cardTeam = cardParent.getAttribute('data-team') || 'PDC Darts';
          gtag('event', 'click_affiliate_card', {
            event_category: 'affiliate_epn',
            event_label: `#${cardNum} ${cardPlayer} (${cardTeam})`,
            card_number: cardNum,
            card_player: cardPlayer,
            card_team: cardTeam,
            link_url: href,
            transport_type: 'beacon'
          });
        } else {
          gtag('event', 'click_ebay_store', {
            event_category: 'outbound_ecommerce',
            event_label: label || 'eBay Store',
            link_url: href,
            transport_type: 'beacon'
          });
        }
      } else if (href.includes('amazon.com') || href.includes('amzn.to')) {
        gtag('event', 'click_affiliate_amazon', {
          event_category: 'affiliate_amazon',
          event_label: label || 'Amazon Associate Product',
          link_url: href,
          transport_type: 'beacon'
        });
      } else if (href.includes('supplies.html')) {
        gtag('event', 'click_supplies_guide', {
          event_category: 'internal_promotion',
          event_label: label || 'Supplies Guide Link',
          link_url: href,
          transport_type: 'beacon'
        });
      } else if (href.includes('litcards.store')) {
        gtag('event', 'click_litcards_exchange', {
          event_category: 'outbound_exchange',
          event_label: label || 'Litcards Marketplace',
          link_url: href,
          transport_type: 'beacon'
        });
      } else if (href.includes('maps.app.goo.gl') || href.includes('google.com/maps')) {
        gtag('event', 'click_google_maps_directions', {
          event_category: 'local_store',
          event_label: 'Ardmore Store Directions',
          link_url: href,
          transport_type: 'beacon'
        });
      } else if (href.startsWith('tel:')) {
        gtag('event', 'click_phone_call', {
          event_category: 'contact',
          event_label: href.replace('tel:', ''),
          transport_type: 'beacon'
        });
      } else if (href.startsWith('mailto:')) {
        gtag('event', 'click_email_contact', {
          event_category: 'contact',
          event_label: href.replace('mailto:', ''),
          transport_type: 'beacon'
        });
      } else if (href.includes('mailchi.mp') || href.includes('mailchimp')) {
        gtag('event', 'click_newsletter_signup', {
          event_category: 'lead_generation',
          event_label: label || 'Mailchimp VIP Join',
          link_url: href,
          transport_type: 'beacon'
        });
      } else if (href.includes('facebook.com')) {
        gtag('event', 'click_facebook_page', {
          event_category: 'social',
          event_label: 'Facebook Page',
          link_url: href,
          transport_type: 'beacon'
        });
      }
    });
  });

  // Track Checklist View Events
  if (window.location.pathname.includes('/checklists/')) {
    gtag('event', 'view_checklist_guide', {
      event_category: 'content_engagement',
      event_label: document.title,
      page_path: window.location.pathname
    });
  }
});
