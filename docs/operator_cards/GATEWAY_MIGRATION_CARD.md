# Gateway Migration Card

## Universal Flow

1. current gateway
2. new gateway or processor
3. integration method
4. recurring billing exposure
5. token migration support
6. custom code exposure
7. downtime tolerance

## Fast Migration Notes

- Authorize.net to NMI: token migration may be possible
- Authorize.net to Stripe: rebuild subscriptions
- NMI to Authorize.net: rebuild customer profiles
- same gateway, new processor: update credentials and settings

## Sensitive Check

Recurring billing is the most fragile part of migration.

## Never Say

- "We guarantee zero downtime."
- "All tokens can be transferred."
- "We can fix your code."
