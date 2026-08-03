# Privacy

Pilot Puppy stores only bounded semantic receipts. It rejects or omits:

- credentials and secret-shaped values;
- raw prompts, conversations, and provider payloads;
- absolute home or machine-specific paths;
- provider account, model, session, and billing data; and
- arbitrary commands in public receipts.

Decision and Chief-of-Staff projections also require closed proof entries:
`id`, `type`, `locator`, `verification_summary`, and `delivery`, with bounded
public text and supported type/delivery values.

Native-host attempt receipts keep test results equally closed: each entry is
only a bounded public `name` plus `pass`/`fail` status. Arbitrary host metadata
is rejected before it reaches project evidence.

The browser is loopback-only. Evidence stays inside the Git project under
`.pilot-puppy/evidence/`. There is no remote database, cloud executor,
credential relay, watcher, daemon, or background dispatch process.
