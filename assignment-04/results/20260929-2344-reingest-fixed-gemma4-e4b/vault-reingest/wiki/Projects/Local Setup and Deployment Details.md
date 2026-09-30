---
title: Local Setup and Deployment Details
aliases:
  - local-setup-and-deployment-details
topic: Projects
summary: Instructions for local setup, environment variables, and deployment process.
sources:
  - raw/Networking Tracker README.md
source_id: networking-tracker-readme
source_sha256: 74a345428e79e97dbf42f9cf77ea7d277df32dd213f6d22299cd07f2b222bae8
sections_used:
  - Local setup
  - Environment variables
  - Publishable versus secret values
  - Deployment
  - Evidence
  - Two-account privacy check
  - No secrets in the repository
  - Known limitations and what I would improve next
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: networking-tracker-readme/local-setup-and-deployment-details
plan_origin: stored
---
# Local Setup and Deployment Details

## Summary

This note details the complete process for setting up and deploying the Networking Tracker application locally and to a live environment. It covers necessary prerequisites like Node 22.18 or later, specific commands for setting up the Neon database and authentication, and outlines the structure of environment variables, distinguishing between publishable and secret values. The main result is a comprehensive guide to achieving a secure, functional deployment.

## Details

**Local setup**
1. Clone the repository and install dependencies:
   ```
   git clone https://github.com/IsaacAVazquez/Fundamentals-of-Agentic-AI.git
   cd Fundamentals-of-Agentic-AI/assignment-01
   npm install
   ```
2. Create a Neon project, enable managed Better Auth, and enable the Data API with the Neon Auth provider using the following commands:
   ```
   npx neon@latest auth
   npx neon projects create --name networking-tracker --set-context
   npx neon neon-auth enable
   npx neon data-api create --database neondb --auth-provider neon_auth --add-default-grants
   ```
   After enabling both, `npx neon neon-auth status` shows the Auth URL as its Base URL and `npx neon data-api get --database neondb` shows the Data API URL. `npx neon connection-string` prints the Postgres connection string used only for the migration step.
3. Copy `.env.example` to `.env.local` and fill in the values. Generate the cookie secret with `openssl rand -base64 32`.
4. Create the contacts table, its constraints, and its RLS policies by running:
   ```
   npm run db:migrate
   ```
5. Tell Neon Auth to accept sign-ins from your local origin, then start the app and open http://localhost:3000:
   ```
   npx neon neon-auth domain add http://localhost:3000
   npm run dev
   ```

**Environment variables**
Real values live in `.env.local`, which is ignored by Git. `.env.example` holds placeholders only.

| Name | Where it is used | Notes |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_NEON_AUTH_URL` | Server (auth proxy) | HTTPS endpoint of Neon Auth for the branch. Public by design. |
| `NEXT_PUBLIC_NEON_DATA_API_URL` | Browser | HTTPS endpoint of the Data API. Public by design, RLS protects the rows. |
| `NEON_AUTH_COOKIE_SECRET` | Server only | Signs the session cookie. At least 32 characters. Never in the browser bundle. |
| `DATABASE_URL` | Local only | Used by `npm run db:migrate` and the optional database test. Not set on Vercel. |

The two `NEXT_PUBLIC_` URLs are publishable. The cookie secret and the connection string are secrets.

**Deployment**
I deployed with the Vercel CLI from inside `assignment-01`.
```
vercel link
vercel env add NEXT_PUBLIC_NEON_AUTH_URL production --type config
vercel env add NEXT_PUBLIC_NEON_DATA_API_URL production --type config
vercel env add NEON_AUTH_COOKIE_SECRET production
vercel --prod
```
After the first deploy, the production domain has to be added to Neon Auth's trusted domains:
```
npx neon neon-auth domain add https://networking-tracker-lyart.vercel.app
```

**Evidence**
The assignment brief asks for seven specific artifacts, and the Definition of Done slide in the Class 2 deck adds an explanation of publishable versus secret values.

- Automated test output with a passing validation test: The `npm test` output under Tests, five passing, with the blank name and invalid priority cases checked in the validator and again in the database
- Sign-in and sign-out: `prod-01-sign-in.png`, `prod-02-signed-in.png`, and `prod-04-signed-out.png` under Walkthrough
- Creating, editing, deleting, and refreshing a contact: `04-add-dialog.png` through `12-after-delete.png` under Walkthrough, with `06-after-refresh.png` as the reload
- Two accounts, neither can reach the other's contacts: The Data API transcript below, run in both directions, plus `prod-05-user-b-empty.png`
- One invalid input failing safely: `03-invalid-name.png` in the form, and the two `23514` responses in the transcript at the database
- The schema and the RLS ownership rule: Database schema and Authentication and row ownership above
- Publishable versus secret values: Publishable versus secret values, under Environment variables
- No committed secret values: The last paragraph of this section

- Assignment Overview and Requirements: This note covers the setup and deployment process for the application.
- Technology Stack and Architecture: This note details the local setup, environment variables, and deployment process for the application.

## Related

_No related notes yet._

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "Local setup", "Environment variables", "Publishable versus secret values", "Deployment", "Evidence", "Two-account privacy check" and more
