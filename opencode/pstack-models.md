---
description: pstack per-role model choices (overrides skill defaults)
alwaysApply: true
---
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model`). Alias entries in a panel list still count toward its fan-out.
# budget: pinned to sol (every role uses openai/gpt-5.6-sol; no per-role effort ladder)
feature, refactoring: openai/gpt-5.6-sol
bug-fix: openai/gpt-5.6-sol
perf-issue: openai/gpt-5.6-sol
hillclimb: openai/gpt-5.6-sol
judgment and prose: openai/gpt-5.6-sol
hardest tasks: openai/gpt-5.6-sol
how explorer: openai/gpt-5.6-sol
how explainer: openai/gpt-5.6-sol
why investigators: openai/gpt-5.6-sol
why synthesizer: openai/gpt-5.6-sol
reflect tooling: openai/gpt-5.6-sol
reflect judgment, divergent, synthesizer: openai/gpt-5.6-sol
arena runners: openai/gpt-5.6-sol, openai/gpt-5.6-sol
arena cross-judge pool: openai/gpt-5.6-sol, openai/gpt-5.6-sol
swarm workers: openai/gpt-5.6-sol
architect runners: openai/gpt-5.6-sol, openai/gpt-5.6-sol
interrogate reviewers: openai/gpt-5.6-sol, openai/gpt-5.6-sol
