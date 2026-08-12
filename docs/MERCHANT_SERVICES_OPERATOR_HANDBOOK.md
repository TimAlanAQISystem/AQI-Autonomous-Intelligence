# Merchant Services Operator Handbook

Version: 1.0  
Effective date: 2026-08-08  
Classification: Internal use only

## Purpose

This handbook consolidates the full operator-grade merchant services system into a single reference document for training, live support, escalation discipline, and conversational consistency.

It is designed to help operators:

- explain merchant-services concepts clearly
- diagnose issues accurately
- stay inside compliance boundaries
- escalate safely
- sound calm, structured, and professional

## How To Use This Handbook

- Use Sections 1-4 for high-impact operational topics.
- Use Sections 5-9 for live conversation performance and escalation control.
- Use Sections 10-13 for tone, discovery, objection handling, and role-based polish.
- Use the final appendices as fast lookup references during live calls.

## Core Operating Principles

- Diagnose before solving.
- Separate symptoms from causes.
- Never promise outcomes you do not control.
- Never override risk, underwriting, or compliance boundaries.
- Use calm, structured language under pressure.
- Escalate early when risk or compliance is involved.

## Table Of Contents

1. Chargebacks
2. Fraud Tools And Risk Controls
3. PCI Compliance, SAQ Types, And Scope Reduction
4. Surcharging, Dual Pricing, And Network Rules
5. Troubleshooting Playbooks
6. Funding Delays And Reserve Explanations
7. Gateway Migration Scripts
8. Underwriting Red-Flag Phrasing And Safe Operator Boundaries
9. Compliance-Safe Escalation Logic And Decision Trees
10. Tone Frameworks And Professional Phrasing
11. Objection Maps And Conversational Counterweights
12. Discovery Trees And Role-Based Phrasing
13. Role-Based Conversational Templates And Professional Closing Patterns
14. Quick Reference Appendices

---

## 1. Chargebacks

### What a chargeback is

A chargeback is a forced reversal initiated by the cardholder through their issuing bank. It is not a refund, gateway error, or normal processor adjustment.

Operator phrasing:

"Chargebacks come from the customer’s bank, not from us, and they follow strict card-network rules."

### Three root causes

- Fraud: true fraud or friendly fraud
- Service or product issues: not received, not as described, cancellation, recurring billing disputes
- Processing errors: duplicate transactions, incorrect amount, auth problems, late presentment

### Reason-code families

- Visa: `10.x` fraud, `13.x` consumer disputes, `12.x` processing errors
- Mastercard: `48xx` fraud, `46xx` cardholder disputes, `49xx` processing errors
- Amex: `F` fraud, `C` consumer disputes, `P` processing errors

### Evidence that works

- Fraud: AVS, CVV, 3-D Secure, IP consistency, device fingerprint, signed receipt, delivery confirmation
- Service issues: tracking, signed agreements, refund logs, communication history, proof of fulfillment
- Processing errors: batch logs, authorization logs, corrected transaction records, duplicate reversal proof

### Evidence that does not work

- "The customer is lying."
- "We know this customer."
- "They signed up willingly."
- "We already talked to them."

### Prevention controls

- Clear descriptors
- Clear refund and cancellation policies
- Receipts, tracking, and renewal reminders
- AVS, CVV, 3-D Secure, velocity, IP, and device controls
- Clean billing operations

### Response timeline

- Notice received
- Evidence gathered quickly
- Processor submits evidence
- Issuer reviews
- Decision returned
- Arbitration only when justified and cost-effective

### Chargeback compliance boundaries

Never say:

- "We can guarantee you’ll win."
- "We can stop chargebacks completely."
- "We can override the bank."

Safe phrasing:

- "We can help you respond with the strongest evidence."
- "We can help reduce future dispute exposure."

### Discovery questions

- "What type of chargebacks are you seeing?"
- "Are your descriptors clear and recognizable?"
- "Do you send receipts or tracking automatically?"
- "Do you use AVS, CVV, or 3-D Secure?"
- "Are these one-time or recurring transactions?"

### Escalate when

- merchant demands guaranteed wins
- merchant disputes bank authority
- repeated fraud exposure appears
- processor-level override is requested

---

## 2. Fraud Tools And Risk Controls

### Fraud types

- True fraud: stolen or unauthorized card use
- Friendly fraud: customer initiated, often descriptor confusion or avoidance behavior
- Merchant-error fraud: duplicate charges, wrong amounts, unclear descriptors, poor communication

### Core fraud tools

- AVS: verifies billing address
- CVV: verifies physical card possession
- 3-D Secure: adds authentication and can shift liability
- Velocity checks: limits attempts per card, IP, or device
- IP geolocation: compares billing, shipping, and origin location
- Device fingerprinting: detects repeat bad actors
- BIN intelligence: identifies issuer and card characteristics
- Recurring billing controls: retries, reminders, cancellation and renewal handling

### Processor-level risk controls

- Volume caps and transaction caps
- MCC-based risk profiles
- Transaction fraud scoring
- Threshold-based reviews on disputes, chargebacks, fraud, and refunds

### Fraud prevention practices

- Clear descriptors
- Strong authentication
- Delivery proof
- Clear customer communication
- Operational hygiene around timing and amount integrity

### Fraud-control compliance boundaries

Never say:

- "We can eliminate fraud."
- "We can guarantee no chargebacks."
- "We can approve any transaction."

Safe phrasing:

- "We can reduce fraud significantly."
- "We can strengthen your authentication and controls."

### Red flags

- high-risk MCCs
- digital goods with no proof of delivery
- recurring billing disputes
- mismatched IP and country patterns
- sudden volume spikes

---

## 3. PCI Compliance, SAQ Types, And Scope Reduction

### What PCI is

PCI DSS is the card-network security standard that governs how card data is processed, stored, and transmitted.

Operator phrasing:

"PCI is the security standard that protects cardholder data, and every merchant has some level of PCI responsibility."

### Core PCI principle

The less card data a merchant touches, the easier PCI becomes.

### Primary SAQ types

- SAQ A: hosted pages, merchant never touches card data
- SAQ A-EP: merchant site affects checkout but does not receive card data
- SAQ B: simple card-present terminal environments
- SAQ D: full scope, custom systems, direct storage, direct transmission, or direct processing

### Scope reduction methods

- Hosted payment pages
- Tokenization
- Hosted fields
- Avoiding custom checkout pages
- Avoiding card storage
- Using PCI-compliant gateways

### Common misunderstandings

- Processor PCI compliance does not automatically make the merchant compliant.
- Not storing cards does not remove PCI responsibilities.
- Using a gateway reduces scope but does not eliminate SAQ obligations.

### PCI compliance boundaries

Never say:

- "We guarantee PCI compliance."
- "You don’t need PCI because you use our gateway."
- "We can certify you."

Safe phrasing:

- "We can help reduce your PCI scope."
- "We can guide you toward the correct SAQ."

---

## 4. Surcharging, Dual Pricing, And Network Rules

### Three different models

- Surcharging: fee added only to credit cards
- Dual pricing: cash price and card price displayed side by side
- Cash discounting: posted card price with discount for cash

### Surcharging rules

- Credit cards only
- Never on debit, prepaid, PIN debit, EBT, or gift cards
- Registration required where network rules require it
- Clear disclosure required
- Uniform application required
- Cap at 3 percent in this training framework unless narrower state/network rule applies

### Dual pricing rules

- Both prices shown clearly before payment
- Card price not misleading
- Cash price not artificially manipulated

### Cash discounting rules

- Posted price is the card price
- Cash customer receives a discount
- Disclosure must be clear and consistent

### State restrictions noted in this framework

- Surcharging restricted or banned in Connecticut, Massachusetts, and Puerto Rico
- Dual pricing and cash discounting treated here as allowable nationwide

### Pricing-rule compliance boundaries

Never say:

- "You can surcharge debit cards."
- "You can surcharge without registering."
- "You can charge any percentage you want."

Safe phrasing:

- "We can help you choose the model that fits your business."
- "We can help you stay within card-network rules."

---

## 5. Troubleshooting Playbooks

### Troubleshooting mindset

- Diagnose before solving
- Separate symptoms from causes
- Stay neutral and calm

### Universal troubleshooting script

1. Clarify the problem
2. Identify the environment
3. Determine scope
4. Check recent changes
5. Isolate the domain
6. Give correct guidance
7. Escalate if needed

### Core categories

- Terminal and card-present issues
- Gateway and online checkout issues
- Funding and settlement issues
- Chargeback and dispute issues
- Recurring billing issues

### Troubleshooting compliance boundaries

Never say:

- "We can guarantee approval."
- "We can override declines."
- "We can force funding."

Safe phrasing:

- "We can help identify where the issue is."
- "We can guide you through the correct steps."
- "We can escalate this to the right team."

---

## 6. Funding Delays And Reserve Explanations

### What funding is

Funding is the movement of a merchant’s batch into their bank account. Timing depends on batch close, processor schedules, bank windows, holds, reserves, risk review, chargebacks, and unusual activity.

### Funding models

- Standard funding
- Next-day funding, cutoff dependent
- Same-day funding, rare and underwriting dependent

### Five root causes of delay

- Batch timing
- Bank processing windows
- Risk review
- Reserves
- Holds

### What does not cause funding delays

- the gateway itself
- the POS system itself
- the terminal itself
- the website itself

### Funding compliance boundaries

Never say:

- "We guarantee funding tomorrow."
- "We can override the bank."
- "We can remove your reserve."

Safe phrasing:

- "We can check the status of your batch."
- "We can explain why funding is delayed."
- "We can escalate this to the risk team."

---

## 7. Gateway Migration Scripts

### Migration mindset

- Reduce merchant anxiety
- Avoid technical overreach
- Maintain continuity

### Universal migration flow

1. Identify current gateway
2. Identify new gateway or processor
3. Identify integration method
4. Identify recurring billing and stored cards
5. Identify custom code
6. Identify downtime tolerance
7. Guide the migration path
8. Escalate when needed

### Common migration patterns

- Authorize.net to NMI: token migration possible, recurring logic review needed
- Authorize.net to Stripe: token migration not supported, subscriptions rebuilt
- NMI to Authorize.net: customer profiles rebuilt
- Processor swap under same gateway: update credentials, batch settings, and reporting paths
- WooCommerce plugin to Shopify app: no direct plugin migration, subscription and fraud flows must be rebuilt

### Compliance boundaries

Never say:

- "We guarantee zero downtime."
- "We can migrate all tokens."
- "We can fix your code."

Safe phrasing:

- "We can guide you through the migration process."
- "We can help you understand what transfers and what does not."

---

## 8. Underwriting Red-Flag Phrasing And Safe Operator Boundaries

### What underwriting evaluates

- business model
- MCC
- average and high ticket
- monthly volume
- chargeback, refund, and fraud exposure
- delivery method and recurring model
- legitimacy and documentation quality

### Risk categories

- Low risk
- Medium risk
- High risk

### Never say

- "We can approve anything."
- "We approve everyone."
- "We can override underwriting."
- "We can bypass documentation."

### Safe alternatives

- "Underwriting will review your business details."
- "Approval depends on your business model and documentation."
- "We can help you prepare what underwriting needs."

### Red-flag behaviors

- misrepresenting business model
- hiding high-risk activity
- showing suspicious patterns
- lacking core documentation
- carrying repeated dispute exposure

### Boundary phrasing

"My role is to help you prepare for underwriting. The final decision comes from the underwriting team."

---

## 9. Compliance-Safe Escalation Logic And Decision Trees

### Escalation mindset

- Escalate early when risk is involved
- Escalate late when the issue is still simple and local
- Escalate with neutral, safe phrasing

### Universal escalation flow

1. Diagnose the issue
2. Identify the domain
3. Determine whether escalation is required
4. Phrase escalation safely
5. Document cleanly
6. Transfer ownership cleanly

### Domain trees

- Funding and settlement: risk team, underwriting, funding department
- Chargebacks: chargeback specialists, risk team
- Fraud: risk team, fraud specialists
- Underwriting: underwriting, risk team
- Gateway and technical: gateway support, developer, integration specialists
- Bank and issuer: processor support, bank liaison

### Allowed phrasing

- "I’ll escalate this to the correct team."
- "They handle this type of issue."
- "I’ll document everything so they have full context."

### Not allowed

- "They’ll approve you."
- "They’ll release your funds."
- "They’ll remove your reserve."

---

## 10. Tone Frameworks And Professional Phrasing

### Four tones

- Calm and reassuring
- Confident and directive
- Neutral and professional
- Warm and helpful

### Core phrasing frameworks

- Step-by-step: "Here’s what we’ll do..."
- Clarify and guide: "Let’s clarify what’s happening..."
- Neutral compliance: "My role is to help you understand the process..."
- Reassurance without promises: "We’ll take a look at this together..."
- Boundary-safe: "I can help explain the process and connect you with the team that handles these decisions."

### Vocabulary guidance

Prefer verbs like `review`, `verify`, `confirm`, `clarify`, `escalate`, `document`, `guide`, and `coordinate`.

Avoid slang, blame, emotional exaggeration, and promises.

### Conversation structure

1. Acknowledge
2. Clarify
3. Diagnose
4. Guide
5. Escalate if needed
6. Close professionally

---

## 11. Objection Maps And Conversational Counterweights

### Objection framework

1. Acknowledge
2. Clarify
3. Reframe
4. Guide
5. Hold the boundary

### Major categories

- Confusion
- Frustration
- Fear
- Mistrust
- Misunderstanding
- Pressure

### Core counterweights

- Funding: "Let’s check your batch time and funding schedule so we can see exactly where things are in the process."
- Chargebacks: "The bank only accepts evidence that directly addresses the reason code. Let’s gather the strongest evidence."
- Fraud declines: "Let’s check whether this is terminal, gateway, or bank-related."
- Underwriting: "I can help you prepare the right documents so the process goes smoothly."
- Technical: "Let’s break this down step by step so we can isolate the issue."
- Pricing rules: "Dual pricing may fit better if surcharge rules create too much friction."

### Techniques

- Softening: "I understand." "I hear you."
- Redirecting: "Let’s take a closer look."
- Structuring: "First we’ll check X, then Y."
- Boundary setting: "My role is to help you prepare."
- Reassurance without promises

---

## 12. Discovery Trees And Role-Based Phrasing

### Universal discovery tree

1. Business model
2. Transaction flow
3. Average and high ticket
4. Volume
5. Tools in use

### Merchant discovery

- What they sell
- How customers pay
- Current gateway, POS, or platform
- Recurring, high-ticket, or international exposure
- Main challenge today

### ISO discovery

- portfolio verticals
- risk appetite
- preferred gateways and processors
- underwriting flow
- current processor pain points

### MSP discovery

- supported platforms
- API, plugin, or hosted-field use
- custom constraints
- support model

### VAR discovery

- software and hardware offered
- gateway connection method
- merchant verticals
- recurring revenue exposure

### Gateway discovery

- integration method
- token migration support
- fraud tooling
- processor compatibility

### Bank discovery

- funding windows
- ACH timing
- deposit-delay triggers
- communication patterns

### Role-based phrasing anchors

- Merchant: simple and calm
- ISO: portfolio and economics focused
- MSP: technical and integration focused
- VAR: solution and platform focused
- Gateway: compatibility and tokenization focused
- Bank: neutral and settlement focused

---

## 13. Role-Based Conversational Templates And Professional Closing Patterns

### Merchant template

- Opening: "Thanks for reaching out. Let’s walk through this together so I can understand your setup clearly."
- Guidance: "Here’s what we’ll do..."
- Closing: "Let me know if you need anything else. I’m here to help."

### ISO template

- Opening: "Let’s align your portfolio needs with the right processing setup."
- Closing: "If you want, we can map out a clean onboarding flow for your merchants."

### MSP template

- Opening: "Let’s make sure your technical stack aligns with the payment flow."
- Closing: "If you’d like, we can outline a clean migration or integration plan."

### VAR template

- Opening: "Let’s ensure your platform integrates cleanly with the payment stack."
- Closing: "If you want, we can build a recommended integration checklist."

### Gateway representative template

- Opening: "Let’s verify the integration method and tokenization requirements."
- Closing: "If you’d like, we can map out a clean migration path."

### Bank representative template

- Opening: "Let’s align funding windows and settlement behavior."
- Closing: "If needed, we can coordinate with the processor’s funding team."

### Approved opening patterns

- Calm and reassuring
- Structured and directive
- Neutral and compliance-safe
- Warm and helpful

### Approved closing patterns

- Supportive
- Structured
- Escalation-safe
- Merchant-calming
- Role-appropriate professional close

---

## 14. Quick Reference Appendices

### Appendix A: Never-Promise List

Never promise:

- approval
- funding by a specific uncontrollable date
- reserve removal
- chargeback wins
- fraud elimination
- downtime-free migration
- gateway or bank overrides

### Appendix B: Fast Escalation Map

- Funding holds and reserves: risk team, underwriting, funding department
- Chargebacks: dispute team, risk team
- Fraud spikes: fraud specialists, risk team
- Custom integrations: gateway support, developer, integration specialists
- Underwriting disputes: underwriting, risk team, compliance where needed
- Network-rule disputes: compliance and pricing specialists

### Appendix C: Tone Reminders

- Lower the emotional temperature first.
- Clarify before explaining.
- Give one structured next step at a time.
- Do not argue with a merchant’s emotion.
- Use calm certainty, not bluntness.

### Appendix D: Discovery Starters

- "What products or services do you sell?"
- "How do your customers typically pay?"
- "What gateway, POS, or platform are you using today?"
- "Are there any recurring, high-ticket, or international transactions involved?"
- "What’s the main challenge you want solved first?"

### Appendix E: Professional Closes

- "Let me know if you need anything else. I’m here to help."
- "If anything changes, reach out and we’ll walk through it together."
- "I’ve documented everything and the right team will review it."
- "We’ll make sure this gets to the right place."

## Maintenance Note

This handbook should be updated when:

- network rules change
- underwriting policy changes
- fraud or dispute workflows change
- approved tone, escalation, or discovery logic changes
- new gateway or migration patterns become standard

For training use, this document should be treated as the canonical operator-facing source of truth for the completed module set.
