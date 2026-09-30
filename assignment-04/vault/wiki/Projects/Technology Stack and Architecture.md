---
title: Technology Stack and Architecture
aliases:
  - technology-stack-and-architecture
topic: Projects
summary: Describes the technologies used and the overall system architecture.
sources:
  - raw/Networking Tracker README.md
source_id: networking-tracker-readme
source_sha256: 74a345428e79e97dbf42f9cf77ea7d277df32dd213f6d22299cd07f2b222bae8
sections_used:
  - Technology stack and why
  - Architecture
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: networking-tracker-readme/technology-stack-and-architecture
plan_origin: model-retry
---
# Technology Stack and Architecture

## Summary

This note details the technology stack and overall system architecture for the project. The stack utilizes Next.js 16 on Vercel, with shadcn/ui and Tailwind CSS v4 for the UI, and Neon Postgres for data management. The architecture enforces security by ensuring the browser cannot bypass protection layers in the frontend, server, or database.

## Details

**Technology stack and why**
*   Next.js 16 with the App Router runs on Vercel, which is the assignment's required host and the path of least friction for a Next.js deploy.
*   The UI uses shadcn/ui components on Tailwind CSS v4, which gave me accessible dialogs and inputs without writing them from scratch and without a heavy component library.
*   On 2026-09-08 I replaced the default look with a visual system of its own, a Berkeley class directory with a blue and gold cover, white listing pages with hanging-indent entries, and the priority filter as a thumb index on the edge of the page.
*   The tokens and rules behind it are written down in `DESIGN.md`, and the product context that shaped it is in `PRODUCT.md`.
*   Neon Postgres holds the data, Neon's managed Better Auth issues sessions and JSON Web Tokens, and the Neon Data API exposes the contacts table over HTTPS as a PostgREST endpoint that the browser calls directly.
*   I chose that shape because it keeps the trust boundary in the database, which is where the assignment wants it, and because it means the deployed app never holds a Postgres connection string at all.
*   The single dependency for both auth and data is `@neondatabase/neon-js`.
*   Tests run on Node's built-in test runner, which strips TypeScript types natively on Node 22.18 and later, so there is no test framework to install.

**Architecture**
The architecture consists of a frontend, a thin server layer, and a database, and the browser cannot skip the protection in any of them.

*   **Browser:** Uses Next.js client components and shadcn/ui. The contacts page in `components/contacts-page.tsx` loads rows, sorts and filters them in memory, lays them out as directory entries in two columns on a laptop and one on a phone, and opens a dialog for add and edit. The sign-in and sign-up pages share one form.
*   **Next.js server on Vercel:** This layer handles authentication and data requests.
    *   The route handler at `app/api/auth/[...path]/route.ts` proxies every auth call to Neon's managed Better Auth service and rewrites the returned session cookie so it is first-party, HttpOnly, and signed with a secret that only the server knows.
    *   The `proxy.ts` middleware checks that cookie before the contacts page renders and redirects to the sign-in page otherwise.
*   **Database:** Ownership resides here. When the browser needs to read or write contacts, it first asks its own server for a short-lived JWT at `/api/auth/token`, which the proxy fetches from Neon Auth using the session cookie. The Data API client in `lib/neon.ts` caches that token until shortly before it expires and attaches it as a bearer token on every request. The Data API validates the signature against Neon Auth's public keys, connects to Postgres as the `authenticated` role, and exposes the token's `sub` claim through `auth.user_id()`. Every policy on the contacts table compares that value to the row's `user_id`, so a query can only ever see or change the caller's rows.
*   **Hosting:** Vercel is used for the Next.js app and Neon for everything else. The Vercel project holds three environment variables: the two public Neon URLs and the cookie secret. It does not hold `DATABASE_URL`, because nothing in the running app opens a direct database connection.

## Related

- [[Local Setup and Deployment Details]]: This note describes the technologies used and the overall system architecture

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "Technology stack and why", "Architecture"
