# Source Playbook Authoring

Source playbooks are compact jurisdiction/domain checklists for general legal
research. They help the agent decide which source layers must be checked before
it treats a legal proposition as reliable.

Use a playbook when a recurring general-law topic has source-layer rules that
are easy to miss, such as delegated rules, agency guidance, implementation
notices, currentness checks, or controlling case law.

Do not add a playbook for a one-off question, a broad jurisdiction summary, or a
domain where `knowledge/general/source-map.md` already gives enough direction.
Prefer narrow playbooks that can be loaded on demand.

## Create A Draft

Run:

```bash
python3 scripts/create-source-playbook.py \
  --jurisdiction KR \
  --domain platform_service \
  --title "KR Platform Service"
```

The script creates:

```text
knowledge/general/playbooks/kr-platform-service.md
```

It also registers the file in:

```text
knowledge/general/source-playbook-index.json
```

Generated drafts intentionally contain TODO placeholders. Fill the required
sections before expecting local checks to pass.

## Allowed Values

Jurisdictions:

- `KR`
- `US`
- `EU`
- `JP`
- `UK`
- `MULTI`

Domains:

- `platform_service`
- `contracts_commercial`
- `administrative`
- `employment`
- `civil_liability`
- `consumer_ecommerce`
- `corporate`
- `tax`
- `general`

Statuses:

- `draft`
- `active`
- `deprecated`

Use `draft` while the source strategy is incomplete. Use `active` only when the
playbook is ready for agent use. Use `deprecated` when a playbook remains in the
index for history but should not guide new research.

## Write The Playbook

Keep the scope narrow. A good playbook describes one reusable source strategy,
not the entire law of a jurisdiction.

Every playbook must include these sections in order:

```text
## Metadata
## Scope
## Required Source Layers
## Official Source Entry Points
## Delegated Rule Checks
## Case Law Or Agency Decision Checks
## Currentness Checks
## Common Pitfalls
## Fallback Behavior
## Example Source Plan
```

`Required Source Layers`, `Currentness Checks`, and `Fallback Behavior` must be
substantive. They are the minimum safety sections.

## Good Source-Layer Entries

Good entries are specific about source hierarchy and stop conditions:

- Primary statute, then enforcement decree/rule when the statute delegates
  operative details.
- Regulator notices, FAQs, or enforcement positions when practical compliance
  depends on agency interpretation.
- Cases or administrative decisions when liability, remedy, or sanction
  thresholds are interpretation-driven.
- Current official version, effective date, pending amendment, and supersession
  check before assigning high confidence.

Weak entries are too broad:

- Check the law.
- Look for regulations.
- Search cases if needed.
- Use official sources.

## Fallback Behavior

Fallback behavior should say what the agent must do when a required layer cannot
be verified. Typical consequences:

- lower confidence;
- add a `coverage_gaps` entry;
- add visible limiting language;
- avoid a high-confidence answer;
- recommend targeted follow-up verification.

Do not let a missing source layer disappear silently.

## Reference Packs Are Different

Source playbooks guide source collection for recurring jurisdiction/domain
research. Reference packs guide drafting, tailoring, and quality control for a
specialist output.

Add or update a file under `references/packs/` when:

- a specialist skill needs detailed tables, templates, or pitfalls;
- the material is reusable across matters;
- the content is procedural rather than cached current law;
- the compact skill would become too long if the detail stayed inline.

Add or update a top-level `references/*.md` file when:

- a workflow needs a reusable schema, template, or cross-specialist control;
- more than one skill can use the same reference;
- the material is not tied to one specialist topic.

After adding a pack or reference, update the relevant validator:

```bash
python3 scripts/check-reference-catalog.py
python3 scripts/check-references-corpus.py
python3 scripts/check-reference-packs.py
python3 scripts/check-reference-links.py
```

Prefer the reference scaffold for new artifacts:

```bash
python3 scripts/create-reference-artifact.py \
  --kind reference \
  --id memo-sanity-check \
  --title "Memo Sanity Check"
```

The scaffold creates the draft Markdown file and registers it in
`references/reference-catalog.json`. Fill the draft, wire any skill load rule,
then run the validators above.

## Validate

Run the dedicated validator:

```bash
python3 scripts/check-source-playbooks.py
```

Run the full local preflight before submitting changes:

```bash
python3 scripts/run-local-checks.py
```

The source playbook validator checks the registry, required headings, allowed
vocabulary, unresolved placeholders, metadata/registry agreement, and
unregistered files.
