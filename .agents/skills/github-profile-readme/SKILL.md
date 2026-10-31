---
name: github-profile-readme
description: Maintain the ccamel GitHub profile README, its markscribe template, generated activity sections, and badge-owned content. Use when changing README.md, README.md.gtpl, profile wording, featured projects, technologies, profile cards, or activity sections.
---

# Maintain the GitHub Profile README

## Sources of truth

| Content                                       | Edit                                      | Do not edit directly                                   |
| --------------------------------------------- | ----------------------------------------- | ------------------------------------------------------ |
| Static profile content and layout             | `README.md.gtpl`                          | `README.md` only                                       |
| Releases, blog posts, gists, stars, followers | markscribe directives in `README.md.gtpl` | generated values in `README.md`                        |
| Badge inventory                               | `my-badges/` via `Update Badges`          | the content between `my-badges` markers in `README.md` |
| Rendered profile                              | `README.md`                               | —                                                      |

`Update Activity` regenerates `README.md` weekly with `markscribe -write README.md README.md.gtpl`, repairs the badge marker syntax, then runs Prettier. The badge content in the template is only a potentially stale snapshot, not the source of truth; its `[!-- my-badges start --]` and `[!-- my-badges end --]` markers are deliberately repaired by the workflow. After a successful activity update, `Update Badges` refreshes the rendered badge range and `my-badges/`. Direct edits to generated content will be lost.

## Workflow

1. Read the relevant `README.md.gtpl` section and its rendered counterpart in `README.md` before changing either.
2. For static content, update `README.md.gtpl` and the corresponding static content in `README.md`, leaving generated activity and badges untouched. If regenerating instead, follow `.github/workflows/update-activity.yml`, including marker repair and `npx prettier@3.0.3 README.md --write`; regeneration can temporarily restore stale template badges, so refresh them with `Update Badges` and report any refresh not performed.
3. Follow the editorial posture and scope guidance below.
4. Preserve markscribe directives (`{{...}}`) unless the requested change concerns them. Do not replace dynamic data with snapshots.
5. Never hand-edit the badge-managed range or files under `my-badges/`; use `Update Badges` when badges must refresh.
6. Use the Nix devshell when available. For a rendered update, format with `npx prettier@3.0.3 README.md --write` as in the workflow, then run `markdownlint-cli2 README.md` when available.

## Scope

- Maintenance: make the smallest requested change, preserving unrelated content, structure, and links.
- Evolution or redesign: when the explicit goal calls for a broader improvement, reorganize, replace, or remove content and layout as needed; preserve unrelated intent and working generation.
- Do not add dependencies or workflow automation unless the goal requires them; avoid duplicate project cards.

## Editorial posture

This is a living technical self-portrait, not a résumé or a marketing page. It should make a technically literate visitor understand the person behind it: a senior builder and technical leader who ships, thinks architecturally, values open source, and remains hands-on.

- Write in first person where it makes the profile more personal; use concise, assured English.
- Favor concrete evidence over claims: roles, shipped systems, repositories, languages, architectural concerns, and durable technical principles.
- Never invent achievements, responsibilities, metrics, or project maturity. Distinguish experiments from production systems; ground technical claims in the actual repositories whenever possible. If a claim cannot be verified, omit it or ask the owner.
- Project confidence through specificity and calm pragmatism, never through hype, status signaling, superlatives, or generic AI/Web3/cloud jargon.
- Retain the profile's distinctive register: technically fluent, a little poetic and playful, with references to code, craft, the 80s, and hacker culture when they are genuine to the subject.
- Treat existing wording as a stylistic reference, not an untouchable editorial truth. Question or improve vague, inflated, or dated phrasing when the requested scope permits, without flattening the author's voice.
- Balance strategy and implementation. The profile should read as someone who can lead teams and also design, build, and reason about systems.
- Preserve the open-source, egoless-collaboration, simplicity, and mentorship posture expressed by the prime directives.
- Keep personal details warm but brief; they humanize the profile without competing with professional credibility.
- Prefer active, plain wording: “building”, “leading”, “exploring”, “shaping”. Replace vague claims such as “passionate”, “innovative”, “world-class”, or “results-driven” with verifiable detail.

## Invariants

- `README.md.gtpl` is the editable source for every static profile section.
- `README.md` must remain a faithful rendered copy of static template content plus current dynamic data.
- Keep external images meaningful: retain `alt` text and avoid adding decorative assets without a request.
- When retaining the `Codefield` table, preserve its paired `<td width="50%" valign="top">` layout; add cards as complete rows.
- Keep the badge delimiters valid HTML comments in the rendered README.

## Checks

- Confirm all edited links, image URLs, and Markdown/HTML delimiters are syntactically intact.
- Check `README.md` formatting with the workflow's pinned version: `npx prettier@3.0.3 README.md --check`. Do not run Prettier on the `.gtpl` template as though it were Markdown.
- A local rendered README cannot prove third-party images, GitHub cards, markscribe API data, or the badge workflow output; report those limits.
