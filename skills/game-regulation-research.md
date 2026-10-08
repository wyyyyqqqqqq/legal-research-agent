---
name: game-regulation-research
description: Use in `game_regulation` mode and for the game-law core of `game_plus_general`.
disable-model-invocation: true
---

# Game-Regulation Research

Use this skill in `game_regulation` mode and for the game-law core of `game_plus_general`.

## Core Questions

Begin from the specific product, business model, parties, users, technologies, transactions, distribution channels, commercial relationships, and jurisdictions involved.

Ask:

- What is the relevant product, service, feature, transaction, or business activity?
- Which jurisdiction(s) and legal layers matter?
- What product mechanics, monetization models, user interactions, platform arrangements, technologies, or commercial relationships may create legal risk?
- Which legal issues are clearly material, which require factual confirmation, and which appear low relevance?
- Are there material legal issues that fall outside the repository's predefined game-regulation categories or specialist skills?
- Which issues require game-specific analysis, and which require use of the general source-first workflow?
- Which regulators, courts, tribunals, official bodies, contractual frameworks, industry rules, or other legal authorities may be relevant?

## Workflow Additions

At intake:

- apply `game-library.md`;
- load only matching compact game knowledge files;
- use knowledge files as planning orientation, not citable authority.

Before source collection:

- identify likely regulators, courts, tribunals, official bodies, or other relevant authorities using `knowledge/game-regulation/regulatory-map.md` when available;
- consult `knowledge/game-regulation/issue-taxonomy.md` as an issue-spotting and planning aid without treating it as exhaustive;
- apply `jurisdiction-source-playbook.md` for jurisdiction profiles and source minimums;
- prepare jurisdiction-specific source plans;
- identify additional authoritative sources where the predefined registry or knowledge files do not adequately cover a material issue.

## Adjacent Law Boundary

Legal issues should remain within `game_regulation` when they arise materially from the development, publishing, distribution, launch, operation, monetization, marketing, maintenance, or commercial exploitation of a game product or related digital service.

This may include consumer protection, advertising, youth protection, platform rules, virtual goods, payments, refunds, privacy, intellectual property, contracts, tax, employment, competition, financial regulation, online safety, accessibility, sanctions, foreign investment, AI-related issues, or other areas of law where the connection to the game business is substantive.

These categories are illustrative rather than exhaustive.

Use `game_plus_general` only where there is a distinct legal workstream that is substantially independent of the game product or game-business context and is better handled through the general research workflow.

Do not exclude, downgrade, or ignore a material legal issue merely because it falls outside the repository's predefined game-regulation taxonomy, specialist skills, knowledge files, or source registry.

## Privacy Handoff

If `co_running_agents` includes a data-protection specialist:

- do not duplicate detailed privacy analysis already delegated to that specialist;
- identify the game-law facts that trigger privacy review;
- mark privacy as a handoff issue in `issue_map`;
- preserve any game-specific legal interaction that materially affects the privacy analysis;
- state that detailed privacy analysis is delegated to the co-running specialist.

If no data-protection specialist is running and privacy is material to the matter, research the issue through the applicable source-first workflow rather than treating privacy as out of scope.

## Multi-Jurisdiction Structure

For multi-jurisdiction game questions:

1. Provide jurisdiction-by-jurisdiction findings.
2. Use common issue categories where they improve comparison, without forcing every jurisdiction into a fixed taxonomy.
3. Identify common compliance themes and material jurisdiction-specific differences.
4. Include `comparison_matrix` when it clarifies differences.
5. State source limitations, unresolved conflicts, and coverage gaps by jurisdiction.

Do not synthesize "global game law" before each jurisdiction has sufficient authoritative support for the material issues being compared.

Where the same business feature is regulated differently across jurisdictions, preserve those different legal characterizations rather than forcing them into one universal category.

## Output Expectations

- Use `knowledge/game-regulation/issue-taxonomy.md` as an orientation and issue-spotting aid, not as a closed taxonomy or limit on the scope of research.
- Include material issues identified from the facts even where no matching taxonomy category or specialist skill exists, and research them through the general source-first workflow where necessary.
- Do not mimic a long legacy pipeline when a focused memo answers the question.
- Map each material game-related issue to source IDs.
- Distinguish controlling or primary law, official guidance, administrative materials, court or tribunal decisions, contractual or platform rules, and secondary commentary where relevant.
- Use a comparison matrix for multi-jurisdiction answers when it clarifies regulator, source, obligation, procedure, enforcement, or risk differences.
- Include counter-analysis where the legal characterization is genuinely contestable or materially affects the conclusion.
- Record factual uncertainty, jurisdictional uncertainty, source gaps, and unresolved legal issues explicitly rather than inferring certainty.