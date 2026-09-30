---
title: Core Functionality and Features
aliases:
  - core-functionality-and-features
topic: Projects
summary: Describes the main features like contact addition, authentication, and data management.
sources:
  - raw/Networking Tracker README.md
source_id: networking-tracker-readme
source_sha256: 74a345428e79e97dbf42f9cf77ea7d277df32dd213f6d22299cd07f2b222bae8
sections_used:
  - What it does
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: networking-tracker-readme/core-functionality-and-features
plan_origin: model
---
# Core Functionality and Features

## Summary

This note details the core functionality of the networking tracker, covering user authentication, contact management, and data persistence. Key features include signing up and signing in via Neon's Better Auth, adding detailed contacts, and viewing/filtering contacts in a directory listing. The application ensures data integrity through form validation and persists all contacts in Neon Postgres.

## Details

- Sign up, sign in, and sign out with email and password through Neon's managed Better Auth.
- Add a contact with name, company, role, where you met, notes, and a priority of high, medium, or low.
- View contacts as a directory listing that sorts by name, company, priority, or date added, in either direction, and filters by search text and by priority.
- Edit and delete your own contacts, with a confirmation step before a delete.
- Contacts live in Neon Postgres, so they survive a refresh, a new tab, or a different device.
- A blank name, a priority outside the allowed set, or a field past its length limit fails with a clear message in the form, and fails again at the database if the form is bypassed.
- Loading, empty, no-match, success, and error states each have their own visible treatment.
- The layout works on a phone. Below 768px the two-column listing becomes one column and the priority filter moves under the running head.

## Related

- [[Database Schema and Auth]]: This relates to the use of Neon Postgres for contact storage and the use of Better Auth for user management

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "What it does"
