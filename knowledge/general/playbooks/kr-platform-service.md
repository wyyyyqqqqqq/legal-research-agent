# KR Platform Service

## Metadata

- id: kr-platform-service
- jurisdiction: KR
- domain: platform_service
- status: active
- owner: legal-research-agent
- last_reviewed: 2026-05-06

## Scope

Use this playbook for Korean general-law research about platform or online
service operators when the question concerns user-facing service terms,
service changes, account restrictions, user notices, consumer-facing platform
operations, or service-provider obligations that are not primarily
game-regulation issues.

This playbook does not replace specialist privacy, payment, tax, IP, labor, or
game-regulation research. It frames the platform-service source layers and
records handoff gaps when another specialist owns the deeper issue.

## Required Source Layers

- Controlling statute for the user/service issue.
- Enforcement decree or enforcement rule when the statute delegates operational
  requirements, exceptions, procedure, forms, or sanctions.
- Competent regulator guidance, notice, FAQ, standard terms position, or
  enforcement release when practical compliance depends on agency interpretation.
- Consumer or e-commerce source when the platform relationship affects
  cancellation, refund, disclosure, unfair terms, advertising, notice, or user
  remedy.
- Case law or agency decision when validity of terms, damages, unfairness,
  suspension, termination, or notice turns on interpretation.
- Currentness check for every controlling statute, delegated rule, and regulator
  position.

## Official Source Entry Points

- Official Korean statute and delegated-rule source for current text, article
  history, supplementary provisions, and effective dates.
- Competent ministry or regulator pages for notices, guidance, FAQs, standard
  terms positions, and enforcement materials.
- Fair Trade Commission or Korea Consumer Agency materials when the issue
  involves consumer protection, e-commerce, standard terms, unfair practices, or
  cancellation/refund rights.
- Official court or agency decision sources when interpretation, damages,
  invalidity, or sanctions are material.

## Delegated Rule Checks

Do not stop at the act when the issue concerns procedure, disclosure timing,
notice method, sanctions, reporting, recordkeeping, forms, or exemptions.

Check for:

- enforcement decree provisions that define scope, thresholds, exceptions, or
  penalty schedules;
- enforcement rule provisions that specify forms, filings, notice methods, or
  procedural detail;
- notices, guidelines, standard terms positions, or agency interpretations that
  explain how the regulator applies the rule in platform-service settings.

If no delegated rule appears material, say why before assigning high confidence.

## Case Law Or Agency Decision Checks

Check cases or agency decisions when the issue turns on:

- whether a platform term is invalid, unfair, or unenforceable;
- whether notice was sufficient before changing terms, restricting accounts, or
  ending service;
- whether damages, restitution, cancellation, or refund remedies are available;
- how regulators apply broad consumer, e-commerce, standard terms, or unfair
  practice provisions to platform operators;
- whether a sanction threshold depends on factual interpretation.

If no case or agency decision is checked, high confidence is appropriate only
when the statutory/delegated rule is direct and the issue is not
interpretation-driven.

## Currentness Checks

Before final analysis:

- confirm the current official version of every controlling act, decree, rule,
  notice, or guidance document;
- check supplementary provisions, article history, effective dates, and pending
  amendments when timing matters;
- verify that regulator guidance or FAQ material has not been superseded;
- record `temporal_status` or a `coverage_gaps` entry when currentness cannot be
  confirmed;
- avoid high confidence when the answer depends on a source with unknown,
  pending, repealed, or superseded status.

## Common Pitfalls

- Treating a platform's own policy or terms as law.
- Relying on English summaries when the official Korean text controls.
- Stopping at a statute even though enforcement decrees or rules define the
  operative obligation.
- Missing consumer/e-commerce or standard terms rules because the facts are
  framed as a platform operations question.
- Ignoring supplementary provisions that change effective dates or transitional
  treatment.
- Treating regulator press releases as binding law without checking the legal
  basis.

## Fallback Behavior

If a required source layer cannot be verified:

- lower the issue confidence according to
  `knowledge/general/domain-source-checklist.md`;
- add a `coverage_gaps` entry such as `delegated_rule_missing`,
  `agency_guidance_missing`, `case_law_missing`, `temporal_status`, or
  `secondary_only`;
- state the missing source layer in the result memo;
- avoid high-confidence conclusions for the affected issue;
- recommend targeted follow-up verification against the missing official source.

If the question is actually privacy, payment, IP, labor, tax, or game-law
centric, keep only the platform-service framing and record the specialist
handoff.

## Example Source Plan

For a Korean platform terms-change or account-restriction question:

1. Identify the service relationship issue and controlling statute.
2. Check the act plus enforcement decree/rule for notice, procedure, exceptions,
   sanction, or user-remedy detail.
3. Check FTC, KCA, or competent-regulator materials for standard terms,
   consumer/e-commerce, notice, unfair practice, or enforcement position.
4. Check cases or agency decisions if validity, damages, unfairness, or
   sufficient notice is interpretation-driven.
5. Confirm currentness and effective dates before assigning confidence.
6. Record any missing delegated-rule, guidance, case-law, or temporal layer in
   `coverage_gaps`.
