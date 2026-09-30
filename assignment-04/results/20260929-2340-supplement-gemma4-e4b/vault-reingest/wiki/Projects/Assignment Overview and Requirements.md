---
title: Assignment Overview and Requirements
aliases:
  - assignment-overview-and-requirements
topic: Projects
summary: This section details the structure of the assignment requirements following the provided rubric.
sources:
  - raw/Networking Tracker README.md
source_id: networking-tracker-readme
source_sha256: 74a345428e79e97dbf42f9cf77ea7d277df32dd213f6d22299cd07f2b222bae8
sections_used:
  - Networking Tracker
  - Where to find each requirement
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: networking-tracker-readme/assignment-overview-and-requirements
plan_origin: model
---
# Assignment Overview and Requirements

## Summary

This note details the structure and components of the "Networking Tracker" web app, which was built for Assignment 1 of Fundamentals of Agentic AI. The app functions as a private contact list for Berkeley connections, ensuring data privacy through Postgres Row Level Security. The technology stack includes Next.js on Vercel, Neon Postgres, Neon's managed Better Auth, and the Neon Data API.

## Details

The Networking Tracker is a small web app for keeping a private list of people I want to stay connected with at Berkeley. Each contact requires a name, company, role, where we met, a note, and a priority. Every account sees only its own contacts, and this is enforced inside Postgres with Row Level Security, meaning even a request that skips the UI and talks to the database API directly gets only the caller's rows.

The stack used is:
*   Next.js on Vercel
*   Neon Postgres
*   Neon's managed Better Auth
*   Neon Data API

The live app is available at: https://networking-tracker-lyart.vercel.app

The following sections map to the assignment's README requirements:
*   Live Vercel URL: Above, and again under Deployment
*   Screenshots or walkthrough: Walkthrough
*   Feature list: What it does
*   Technology stack and why: Technology stack and why
*   Architecture summary: Architecture
*   Local setup through `npm run dev`: Local setup
*   Environment variable names: Environment variables
*   Publishable versus secret values: Environment variables
*   Schema with every column: Database schema
*   Authentication and RLS ownership: Authentication and row ownership
*   Test command and what it verifies: Tests
*   Deployment instructions: Deployment
*   Known limitations: Known limitations and what I would improve next
*   Grading evidence: Evidence, which maps each required artifact to a file or transcript

## Related

- [[Core Functionality and Features]]: What it does
- [[Technology Stack and Architecture]]: Technology stack and why
- [[Data Persistence and Security Details]]: Authentication and row ownership

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "Networking Tracker", "Where to find each requirement"
