# Impeccable operating notes for assignment-01

Project facts only. Machine-level tooling notes live in ~/.claude/impeccable/.

The app styles through Tailwind v4 utilities and the tokens in app/globals.css, so the mechanical detector returns an empty array over the .tsx files. Compute contrast from the hex tokens by hand instead: gold #fdb515 on Berkeley Blue #003262 is about 7.2:1, muted foreground #5b6168 on white about 6.3:1, the input border #6f7780 on white above 4.5:1.

The dev server runs on port 3100 because 3000 is taken on this machine. Playwright's screenshots land in the repository root, not the app folder, so move them into .impeccable/review/ (gitignored) before handing them to a reviewer.

A throwaway review account exists in the shared Neon database, designreview@example.com, with five seeded entries covering all three priorities. It was created on 2026-09-08 for the redesign inspection and is fine to reuse for screenshots. The graded test accounts are usera@example.com and userb@example.com.

Surface mode for the whole app is operate, decided 2026-09-08. The visual world is The Class Directory (seed 9bae0f3a), recorded in DESIGN.md. Things that are correct and should not be re-fixed: the native select elements for priority and sort stay native because they work best on phones; the chrome is deliberately flat Berkeley Blue rather than a cloth texture; there is no dark theme by decision.
