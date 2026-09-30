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

The `contacts` table schema is defined in `db/schema.sql` and includes columns like `id` (`uuid`), `user_id` (`text`), `name` (`text`), `company` (`text`), `role` (`text`), `where_met` (`text`), `notes` (`text`), `priority` (`text`), and `created_at` (`timestamptz`). There is an index on `user_id` because every query filters on it through RLS.

Authentication uses Neon's managed Better Auth via the app's `/api/auth` proxy. A successful sign-in yields a session cookie and a JWT with `sub` as the user's id and `role` as `authenticated`.

The `contacts` table has RLS enabled with four policies (select, insert, update, delete), all scoped to the `authenticated` role and built on the rule `auth.user_id() = user_id`.
*   Select and delete policies use the rule in `USING`.
*   The insert policy uses it in `WITH CHECK`, ensuring a new row must carry the caller's id, which the column default fills from the token.
*   The update policy uses the rule in both `USING` and `WITH CHECK`, restricting users to only touching their own rows.

The Data API connects as `authenticated`, applying these policies. The migration script connects as the table owner over `DATABASE_URL`, bypassing RLS, which is why that string remains on my machine.

Validation has two layers: `lib/contacts.ts` checks name, priority, and length limits in the browser, and `NOT NULL` and `CHECK` constraints in the schema enforce these in the database. The name constraint treats tabs and newlines as blank, and the length constraint carries the form's limits. `db/schema.sql` drops and re-adds both constraints, ensuring databases created before 2026-09-28 pick them up on `npm run db:migrate`.

Tests are run via `npm test` using `tests/contacts.test.ts`. Six cases verify valid contact acceptance, rejection of empty/whitespace names, rejection of invalid priorities, length limit failures, database error code mapping, and session recognition. A seventh case connects to the database when `DATABASE_URL` is set, proving `CHECK` constraints reject blank names, tab-only names, invalid priorities, and over-long names at the Postgres level.

## Related

- [[Technology Stack and Architecture]]: This note covers the database structure, authentication flow, and row ownership

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "Database schema", "Authentication and row ownership", "Tests"
