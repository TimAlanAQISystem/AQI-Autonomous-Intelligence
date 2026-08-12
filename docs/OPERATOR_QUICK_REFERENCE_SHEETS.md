# Operator Quick Reference Sheets

Version: 1.0  
Effective date: 2026-08-08  
Classification: Internal use only

This file is the compressed live-call layer for the canonical handbook in [docs/MERCHANT_SERVICES_OPERATOR_HANDBOOK.md](docs/MERCHANT_SERVICES_OPERATOR_HANDBOOK.md).

## Contents

1. PCI & SAQ Types
2. Surcharging, Dual Pricing, And Cash Discounting
3. Chargebacks & Reason Codes
4. Fraud Tools & Decline Logic
5. Funding Delays & Reserves
6. Gateway Migration Paths
7. Troubleshooting Flow
8. Escalation Logic
9. Underwriting Red Flags
10. Compliance Boundaries
11. Objection Maps
12. Tone Frameworks
13. Discovery Trees
14. Role-Based Phrasing
15. Professional Openings
16. Professional Closings

---

## 1. PCI & SAQ Types

### Core rule

The less card data the merchant touches, the easier PCI becomes.

### Fast SAQ map

- `SAQ A`: fully hosted checkout, merchant never touches card data
- `SAQ A-EP`: merchant site affects checkout, but card data stays out of merchant systems
- `SAQ B`: simple standalone terminal environment
- `SAQ D`: direct storage, transmission, processing, or complex custom environment

### Scope-reduction levers

- Hosted payment pages
- Tokenization
- Hosted fields
- No card storage
- No custom checkout when avoidable

### PCI never say

- "You don’t need PCI."
- "Our gateway makes you compliant."
- "We guarantee PCI compliance."

### Funding safe phrasing

- "We can help reduce your PCI scope."
- "We can guide you to the correct SAQ."

---

## 2. Surcharging, Dual Pricing, And Cash Discounting

### Model split

- `Surcharging`: fee only on credit cards
- `Dual pricing`: separate cash and card prices shown up front
- `Cash discounting`: posted card price, discount for cash

### Surcharge rules

- Never on debit
- Never on prepaid, PIN debit, EBT, or gift cards
- Registration and disclosure required where applicable
- Uniform credit-card treatment required
- Use 3 percent cap in this operator framework unless stricter rule applies

### Best operator redirect

If merchant wants debit surcharging, move them to dual pricing.

### Funding never say

- "You can surcharge debit."
- "You can hide the fee."
- "You can charge any percentage you want."

---

## 3. Chargebacks & Reason Codes

### Three causes

- Fraud
- Service or product issue
- Processing error

### Fast reason-code families

- Visa: `10.x` fraud, `12.x` processing, `13.x` consumer disputes
- Mastercard: `48xx` fraud, `46xx` disputes, `49xx` processing
- Amex: `F` fraud, `C` disputes, `P` processing

### Evidence that works

- Fraud: AVS, CVV, 3-D Secure, IP, device, signed receipt, delivery proof
- Service: tracking, signed agreement, cancellation policy, communications
- Processing: auth logs, batch logs, corrected records

### Evidence that fails

- "The customer is lying."
- "We know this customer."
- "They signed up willingly."

### Operator anchor

"The bank only accepts evidence that matches the reason code."

---

## 4. Fraud Tools & Decline Logic

### Fraud types

- True fraud
- Friendly fraud
- Merchant-error fraud

### Core controls

- AVS
- CVV
- 3-D Secure
- Velocity checks
- IP geolocation
- Device fingerprinting
- BIN intelligence
- Recurring billing controls

### Decline logic reminders

- Declines can come from issuer, risk controls, gateway settings, or technical faults
- Do not assume every decline is processor-caused

### Safe phrasing

"Let’s identify whether this is stolen-card fraud, customer confusion, or a billing issue."

---

## 5. Funding Delays & Reserves

### Five root causes

- Batch closed after cutoff
- Bank processing window delay
- Risk review
- Reserve deduction
- Hold from unusual activity or thresholds

### What does not cause funding delay

- Gateway itself
- Terminal itself
- Merchant website itself

### Discovery questions

- When did the batch close?
- Any high-ticket transactions?
- Any recent chargebacks or refunds?
- Did volume spike?

### Migration never say

- "We guarantee funding tomorrow."
- "We can force the bank to release funds."

---

## 6. Gateway Migration Paths

### Universal flow

1. Current gateway
2. New gateway or processor
3. Integration type
4. Recurring billing exposure
5. Token migration support
6. Custom code exposure
7. Downtime tolerance

### Fast path reminders

- Authorize.net to NMI: token migration may be possible
- Authorize.net to Stripe: subscriptions usually rebuilt
- NMI to Authorize.net: profiles rebuilt
- Processor swap under same gateway: credentials and settings change

### Never say

- "We guarantee zero downtime."
- "All tokens will migrate."

---

## 7. Troubleshooting Flow

### Universal script

1. Clarify the issue
2. Identify environment
3. Determine scope
4. Check recent changes
5. Isolate domain
6. Guide next step
7. Escalate if needed

### Primary domains

- Terminal
- POS
- Gateway
- Processor
- Bank
- Network
- Merchant system

### Troubleshooting operator anchor

"Let’s walk through this step by step so we can isolate exactly where the issue is."

---

## 8. Escalation Logic

### Escalate early when

- funds are held
- reserves are disputed
- fraud patterns repeat
- underwriting is challenged
- legal or compliance edges appear

### Escalate later when

- issue is still reboot-level
- simple gateway or terminal checks have not been completed

### Escalation safe phrasing

- "I’ll escalate this to the right team."
- "They handle this type of review."
- "I’ll document everything so they have full context."

### Escalation never say

- "They’ll approve you."
- "They’ll release your funds."
- "They’ll remove the reserve."

---

## 9. Underwriting Red Flags

### Watch for

- hidden or changing business model
- high-ticket digital goods
- coaching programs
- supplements, CBD, firearms, adult, crypto, drop-shipping
- missing invoices or contracts
- recurring chargebacks or refunds
- inconsistent ticket and volume claims

### Safe operator line

"Underwriting reviews the business model, documentation, and transaction profile."

### Underwriting never say

- "We approve everyone."
- "We can override underwriting."
- "We can skip documentation."

---

## 10. Compliance Boundaries

### Never promise

- approval
- funding date you do not control
- reserve removal
- chargeback win
- fraud elimination
- gateway or bank override

### Never collect

- full card number
- CVV
- PIN
- full SSN or EIN

### Safe replacements

- "We can explain the process."
- "We can guide you to the right team."
- "We can help reduce risk or delay."

---

## 11. Objection Maps

### Objection flow

1. Acknowledge
2. Clarify
3. Reframe
4. Guide
5. Hold boundary

### Fast counterweights

- Funding: "Let’s verify the batch timing and funding schedule."
- Chargebacks: "Let’s gather evidence that matches the reason code."
- Fraud: "Let’s identify the fraud type first."
- Underwriting: "I can help prepare the documents underwriting needs."
- Technical: "Let’s isolate whether this is terminal, gateway, or bank-related."

---

## 12. Tone Frameworks

### Four tones

- Calm and reassuring
- Confident and directive
- Neutral and professional
- Warm and helpful

### Use by situation

- Funding, disputes, anxiety: calm and reassuring
- Technical guidance, migration: confident and directive
- Underwriting, risk, compliance: neutral and professional
- General help, onboarding: warm and helpful

### Discovery operator anchor

"I understand. Let’s take this step by step."

---

## 13. Discovery Trees

### Universal five questions

- What do you sell?
- How do customers pay?
- What is your average and high ticket?
- What is your monthly volume?
- What gateway, POS, or platform do you use?

### Follow-up branches

- Recurring billing?
- International customers?
- High-ticket transactions?
- Custom integration?
- Main challenge today?

---

## 14. Role-Based Phrasing

### Merchant

Simple, calm, clear.

### ISO

Portfolio, risk, and pricing focused.

### MSP

Technical and integration focused.

### VAR

Platform and merchant-fit focused.

### Gateway rep

Tokenization, fraud tools, and compatibility focused.

### Bank rep

Funding windows, settlement, and compliance focused.

---

## 15. Professional Openings

- "Thanks for reaching out. Let’s walk through this together."
- "Here’s what we’ll do. First I’ll clarify your setup, then we’ll identify the issue."
- "My role is to help you understand the process and guide you to the right team."
- "Happy to help. Let’s take a closer look at what’s going on."

---

## 16. Professional Closings

- "Let me know if you need anything else. I’m here to help."
- "If anything changes, reach out and we’ll walk through it together."
- "I’ve documented everything and the team will review and follow up."
- "We’ll make sure this gets to the right place."
