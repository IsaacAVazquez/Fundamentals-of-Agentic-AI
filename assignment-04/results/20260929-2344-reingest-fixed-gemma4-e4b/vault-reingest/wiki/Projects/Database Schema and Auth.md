---
title: Database Schema and Auth
aliases:
  - database-schema-and-auth
topic: Projects
summary: Covers the database structure, authentication flow, and row ownership.
sources:
  - raw/Networking Tracker README.md
source_id: networking-tracker-readme
source_sha256: 74a345428e79e97dbf42f9cf77ea7d277df32dd213f6d22299cd07f2b222bae8
sections_used:
  - Database schema
  - Authentication and row ownership
  - Tests
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: networking-tracker-readme/database-schema-and-auth
plan_origin: stored
---
# Database Schema and Auth

## Summary

This note details the database schema for the `contacts` table, the authentication flow, and the implementation of row ownership using Row Level Security (RLS). The system ensures that users can only interact with their own data through multiple layers of validation, including browser-side checks, database constraints, and RLS policies.

## Details

**Database schema**
The full definition is in `db/schema.sql`. The table is `contacts`.

| Column | Type | Constraints | Purpose |
| --- | --- | --- | --- |
| `id` | `uuid` | primary key, default `gen_random_uuid()` | Row identifier |
| `user_id` | `text` | not null, default `auth.user_id()` | Owner. Filled by Postgres from the JWT, never sent by the app |
| `name` | `text` | not null, `check (length(btrim(name)) > 0)` | Person's name |
| `company` | `text` | nullable | Where they work |
| `role` | `text` | nullable | What they do |
| `where_met` | `text` | nullable | Where we met |
| `notes` | `text` | nullable | Free text |
| `priority` | `text` | not null, `check (priority in ('high', 'medium', 'low'))` | How important it is to stay in touch |
| `created_at` | `timestamptz` | not null, default `now()` | When the row was added |

There is an index on `user_id` because every query filters on it through RLS.

**Authentication and row ownership**
Sign-up and sign-in go through Neon's managed Better Auth by way of the app's own `/api/auth` proxy. A successful sign-in produces two things. The first is a session cookie that lives on the app's domain, is HttpOnly, and is signed with `NEON_AUTH_COOKIE_SECRET`. The second, fetched on demand, is a JWT whose `sub` claim is the user's id and whose `role` claim is `authenticated`.

The contacts table has Row Level Security enabled and four separate policies, one each for select, insert, update, and delete, all scoped to the `authenticated` role and all built on the same rule, `auth.user_id() = user_id`. The select and delete policies use that rule in `USING`, so rows belonging to anyone else are invisible and undeletable. The insert policy uses it in `WITH CHECK`, so a new row must carry the caller's id, and since the app never sends `user_id` at all, the column default fills it from the token. The update policy uses the rule in both `USING` and `WITH CHECK`, which means a user can only touch their own rows and cannot change `user_id` to hand a row to someone else.

The Data API is the only path from the browser into Postgres, and it always connects as `authenticated`, so those policies apply to every request the app makes. The migration script connects as the table owner over `DATABASE_URL`, which bypasses RLS, and that is exactly why that string stays on my machine and is never given to Vercel.

Validation has two layers on purpose. `lib/contacts.ts` checks the name, the priority, and the length limits in the browser so the form can show a specific message under the field, and the `NOT NULL` and `CHECK` constraints in the schema enforce the same rules in the database so a crafted request fails too. The name constraint treats tabs and newlines as blank, the way the form does, and the length constraint carries the form's limits. `db/schema.sql` drops and re-adds both, so a database created before 2026-09-28 picks them up on its next `npm run db:migrate`. The UI maps the Postgres error codes for a check violation, a missing required value, and an RLS denial to plain sentences, and a request that never reached the database to a sentence about the connection.

**Tests**
```
npm test
```

The test file is `tests/contacts.test.ts` and it runs on Node's built-in runner. Six cases cover `validateContact`, `describeDbError`, and `isAuthProblem`. They verify that a valid contact is accepted with text trimmed and blanks stored as null, that an empty or whitespace-only name is rejected with the message the form shows, a tab or a newline included, that a priority outside high, medium, and low is rejected, that every field passes at its length limit and fails one character past it, that each database error code becomes the sentence the page shows, and that a missing or expired session is recognized. A seventh case connects to the database when `DATABASE_URL` is set and proves the `CHECK` constraints reject a blank name, a tab-only name, an invalid priority, and an over-long name at the Postgres level. Without `DATABASE_URL` that case is skipped, so the suite still passes on a machine without credentials.

Output from a run on 2026-09-28 without `DATABASE_URL`, so the database case is skipped. The 2026-09-08 run on my machine with `DATABASE_URL` set passed the database case as it stood then, with a blank name and an invalid priority, and the schema's new name and length constraints were checked on 2026-09-28 against a local Postgres 16, where applying `db/schema.sql` twice was clean and each bad insert failed on the constraint meant for it.

- Assignment Overview and Requirements: This note covers the database structure, authentication flow, and row ownership.
- Technology Stack and Architecture: This note details the database schema for the `contacts` table, the authentication flow, and the implementation of row ownership using Row Level Security (RLS).

## Related

_No related notes yet._

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "Database schema", "Authentication and row ownership", "Tests"
