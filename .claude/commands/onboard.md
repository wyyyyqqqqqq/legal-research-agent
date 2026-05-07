---
description: Run the onboarding wizard to create or update user-config.json with industry, area-of-law, jurisdictions, and output preferences. Optionally builds a starter knowledge directory.
argument-hint: "[--reset] [--build-knowledge] [--skip-knowledge]"
---

Apply `skills/onboarding.md`.

Argument handling:

- `--reset`: replace any existing `user-config.json` after explicit
  user confirmation. The wizard backs up the prior file to
  `user-config.previous.json` (also gitignored) and then re-asks
  every question.
- `--build-knowledge`: run the recipe-driven knowledge construction
  step even if Question 6 was previously answered `no` or `later`.
  Use this when the user has decided to populate a knowledge
  directory after the initial onboarding.
- `--skip-knowledge`: run the wizard but skip Question 6. Use this
  when the user just wants to refresh preferences without touching
  knowledge directories.
- No arguments: standard wizard run. Update existing config field
  by field, or create a new one if absent.

Skill output expectations:

1. After the wizard, print a one-paragraph summary listing
   industry, primary jurisdictions, default output mode, and
   language.
2. If a knowledge directory was built (Question 6 = `yes` or
   `--build-knowledge` flag), append the directory path, audit
   summary, and the `/review-knowledge <path>` reminder.
3. Remind the user that `user-config.json` and any generated
   knowledge directories are gitignored.

If `$ARGUMENTS` contains an unknown flag, stop and ask for a valid
flag or no flag.
