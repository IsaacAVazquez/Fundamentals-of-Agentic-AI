# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary user is me, an MBA student at Berkeley Haas, keeping a private list of the people I want to stay connected with. I reach it in two situations. The first is right after a mixer, a panel, or a class, usually on my phone, when I want to write down who I just met, where, and why they matter before I forget. The second is a quiet moment at a laptop, scanning the list to decide who to follow up with, which is where the priority and the notes do their work.

The secondary audience is whoever evaluates the app as a portfolio piece, meaning the course grader for Assignment 1 of Fundamentals of Agentic AI and, later, a hiring manager or interviewer I link it to. They arrive cold, sign in with a test account or create one, and judge in under a minute whether this reads like a real product or a class exercise.

## Product Purpose

The app keeps a personal networking list with a name, company, role, where we met, a note, and a priority of high, medium, or low for each person, and it makes that list survive a refresh, a new tab, or a different device. Success for me is that adding a person takes seconds on a phone and that the list is fast to scan on a laptop. Success for the portfolio audience is that the app looks and behaves like something a person would actually use every week, with every state handled and nothing that reads as scaffolding.

## Positioning

Every account sees only its own contacts, and that promise is enforced inside Postgres with Row Level Security rather than in application code. A request that skips the UI and talks to the database API directly still gets only the caller's rows, and a request that tries to plant a row under someone else's id is refused by the database itself. The deployed app never holds a Postgres connection string. That is the mechanism a neighboring CRM template could not truthfully claim.

## Operating Context

Sign up, sign in, and sign out run on email and password through Neon's managed Better Auth, proxied through the app's own `/api/auth` route so the session cookie is first party. Contacts are read and written from the browser straight to the Neon Data API with a short lived JWT. The list sorts by name, company, priority, or date added, filters by search text and by priority, and add and edit happen in a dialog. Delete asks for confirmation. Below 768px the table stacks into labeled cards. The app is deployed on Vercel at https://networking-tracker-lyart.vercel.app and graded from that alias. The README in this directory is the written companion the grader reads alongside the app.

## Capabilities and Constraints

The feature set is fixed at what ships on 2026-09-08. Design work reworks how the existing features feel, not what they do, so no follow-up log, no last contacted date, no schema change, and no new fields. The stack is Next.js 16 with the App Router, React 19, Tailwind CSS v4, shadcn/ui components on Base UI, lucide icons, sonner toasts, and `@neondatabase/neon-js` for auth and data. Validation lives in two layers, `lib/contacts.ts` in the browser and CHECK constraints in `db/schema.sql`, and the UI maps Postgres error codes to plain sentences. Loading, empty, filtered to nothing, error with retry, and success each have their own visible treatment and must keep one. The terminology is contacts, priority, and where met. There is no email verification and no password reset, which is a known limitation and not something the interface should pretend otherwise about.

## Brand Commitments

The product name is Networking Tracker. The page description reads "A private list of the people you want to stay connected with at Berkeley." The written voice across the app and README is first person and plain. There are no logo, color, or typeface commitments yet, and the current look is the shadcn default, which I have decided to replace rather than refine. Berkeley is a real place in the product's story, not a decorative reference.

## Evidence on Hand

Screenshots of the live site and the local walkthrough are in `docs/screenshots`, including the sign in page, the contacts list at desktop and at 390px, the add and edit dialogs, a rejected blank name, the delete confirmation, and a second account seeing an empty list. The README carries a transcript of the two account privacy check run against the Data API with real JWTs on 2026-09-01, and the output of the five test cases in `tests/contacts.test.ts`. Test accounts are usera@example.com, which owns two contacts, and userb@example.com, which owns none. There are no testimonials, user counts, or customer names, and none should be invented.

## Product Principles

Privacy is the product, so nothing on screen should imply the list is shared or social. The phone after an event is the harder scene, so capture has to be fast with a thumb and the list has to read on a narrow screen without losing the fields. The laptop scan is where priority earns its place, so high, medium, and low have to be distinguishable at a glance and sortable without thought. Every state that exists in code stays visible and deliberate, because the portfolio reader will look for the seams. Berkeley and Haas are the real setting, and the design can draw on that world without turning into a university brand exercise.

## Accessibility & Inclusion

Dialogs, sortable headers, form errors, and the loading region already carry ARIA roles and labels, and the redesign keeps them. Contrast has to hold at WCAG AA in whatever palette replaces the default, and the native select elements stay native because they work best on phones.
