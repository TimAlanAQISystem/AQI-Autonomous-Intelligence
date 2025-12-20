# AQI GitHub Pages Custom Domain Setup Guide
## For Domain: scsdmc.com

**Date:** December 20, 2025
**Repository:** https://github.com/TimAlanAQISystem/AQI-Autonomous-Intelligence
**Target URL:** https://aqi.scsdmc.com (after setup)

---

## 🚨 CRITICAL DNS RECORDS TO ADD

### Step 1: TXT Record for Domain Verification
**Purpose:** Proves you own the domain before GitHub allows custom domain use

- **Type:** TXT
- **Name/Host:** `_github-pages-challenge-TimAlanAQISystem.scsdmc.com`
- **Value:** `0e68239849031bff57013226cfdafe`
- **TTL:** 3600 (or default)

### Step 2: CNAME Record for Custom Domain
**Purpose:** Points your custom domain to GitHub Pages

- **Type:** CNAME
- **Name/Host:** `aqi` (this makes it aqi.scsdmc.com)
- **Value:** `timalanaqisystem.github.io`
- **TTL:** 3600 (or default)

---

## 📋 WHERE TO MAKE THESE CHANGES

### Find Your DNS Settings:
1. **Go to your domain registrar** (where you bought scsdmc.com)
2. **Look for:** "DNS Management", "DNS Settings", "Name Servers", or "Zone Editor"
3. **Common locations:**
   - GoDaddy: "DNS" or "DNS Management"
   - Namecheap: "Advanced DNS"
   - Google Domains: "DNS" tab
   - Hostinger: "DNS Zone"

### If You Don't Know Your Registrar:
- Check your email for "scsdmc.com" receipts
- Or visit https://who.is and search for "scsdmc.com" to see registrar info

---

## 🔍 VERIFICATION STEPS

### After Adding Records:
1. **Wait 5-30 minutes** for DNS to update
2. **Test TXT record:** Run this command in terminal:
   ```
   nslookup -type=TXT _github-pages-challenge-TimAlanAQISystem.scsdmc.com
   ```
3. **Test CNAME record:** Run this command:
   ```
   nslookup aqi.scsdmc.com
   ```

### GitHub Verification:
1. Go to: https://github.com/TimAlanAQISystem/AQI-Autonomous-Intelligence/settings/pages
2. Under "Custom domain", enter: `aqi.scsdmc.com`
3. Click "Save"
4. GitHub will check your DNS records automatically

---

## 📞 GET HELP OPTIONS

### Option 1: Ask Someone Technical
- Give this document to a friend/family member who knows computers
- Or post on Reddit (r/dns, r/webdev, r/learnprogramming)

### Option 2: Contact Your Registrar Support
- Call/email your domain registrar's customer support
- Say: "I need to add TXT and CNAME records for GitHub Pages custom domain"
- Give them the exact details above

### Option 3: Professional Help
- Hire someone on Upwork/Fiverr for $10-20 to set this up
- Search for "DNS configuration" or "GitHub Pages setup"

---

## ✅ SUCCESS CHECKLIST

- [ ] TXT record added: `_github-pages-challenge-TimAlanAQISystem.scsdmc.com`
- [ ] CNAME record added: `aqi.scsdmc.com` → `timalanaqisystem.github.io`
- [ ] DNS changes propagated (wait 30+ minutes)
- [ ] GitHub Pages custom domain set to: `aqi.scsdmc.com`
- [ ] SSL certificate generated (GitHub does this automatically)
- [ ] Website loads at: https://aqi.scsdmc.com

---

## 🆘 TROUBLESHOOTING

**If records don't save:**
- Make sure you're in the correct DNS zone for scsdmc.com
- Check for typos in the record values
- Some registrars require the "@" symbol for root domain records

**If GitHub says "not verified":**
- Wait longer for DNS propagation
- Double-check TXT record is exactly as shown
- Try clearing DNS cache: `ipconfig /flushdns` (Windows)

**Need more help?** This guide has everything needed - just find someone technical to follow it!</content>
<parameter name="filePath">AQI_DNS_SETUP_GUIDE.md