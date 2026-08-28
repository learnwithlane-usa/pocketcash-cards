# Pocket Cash Cards - Website & Hub

This is the production repository for **Pocket Cash Cards** ([getpocketcash.com](https://www.getpocketcash.com/)), hosted on **GitHub Pages**.

## Key Features
- **Mobile-First High Conversion Design**: Fast, responsive layout built with semantic HTML5 and Tailwind CSS.
- **3 Core Gateways**:
  1. 🏪 **Ardmore Retail Storefront** (`ardmore.html`) with complete `LocalBusiness` JSON-LD schema for local Google search ranking.
  2. 📦 **Daily eBay Slabs & Singles Store** with direct link tracking.
  3. 🌐 **Litcards Private Exchange** for rare imports, Japanese TCG, and unlisted exclusives.
- **"We Buy Cards & Collections"**: Dedicated local sourcing landing page (`sell-cards.html`).
- **GA4 Conversion Tracking**: Custom event listeners in `assets/js/analytics.js` tracking clicks to eBay, Litcards, Google Maps directions, phone calls, and VIP club signups.

## Domain & DNS Setup
To point your custom domain `getpocketcash.com` to GitHub Pages:
1. In your domain registrar (GoDaddy, Namecheap, Google Domains/Squarespace, Cloudflare):
   - Add **CNAME record**: `www` -> `<your-github-username>.github.io`
   - Add **A records** for `@` apex domain:
     - `185.199.108.153`
     - `185.199.109.153`
     - `185.199.110.153`
     - `185.199.111.153`
2. In GitHub Repository Settings -> **Pages**:
   - Source: Deploy from branch `main` / `root`
   - Custom domain: `getpocketcash.com`
   - Check **Enforce HTTPS**.
