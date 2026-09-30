---
title: Web App Walkthrough Screenshots
aliases:
  - web-app-walkthrough-screenshots
topic: Projects
summary: A detailed walkthrough of the app's functionality using various screenshots.
sources:
  - raw/Networking Tracker README.md
source_id: networking-tracker-readme
source_sha256: 74a345428e79e97dbf42f9cf77ea7d277df32dd213f6d22299cd07f2b222bae8
sections_used:
  - Walkthrough
  - Sign up, sign in, and sign out
  - Adding a contact and surviving a refresh
  - Sorting and filtering
  - Editing and deleting
  - Invalid input
  - A phone viewport
  - A second account
  - What it does
created: 2026-09-30
updated: 2026-09-30
reviewed: false
generated_by: gemma4:e4b
generated_by_digest: c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb
note_id: networking-tracker-readme/web-app-walkthrough-screenshots
plan_origin: model-retry
---
# Web App Walkthrough Screenshots

## Summary

This note provides a detailed walkthrough of the web app's functionality using screenshots taken on the live Vercel site. It covers core features such as user authentication (sign up, sign in, sign out), contact management (adding, editing, deleting), and viewing contacts with sorting and filtering. The walkthrough confirms that contacts persist across refreshes and that the app handles various invalid inputs and different viewport sizes correctly.

## Details

All screenshots are in `docs/screenshots`, and every one of them was taken on the live Vercel site. The sign-up form and the contact screens come from 2026-09-08, after the redesign described under Technology stack, using a review account. On that account I added one contact through the form, added four more, and then sorted, filtered, edited, and deleted. The sign-in, sign-out, and second-account screens come from a separate test account on 2026-09-13.

**Sign up, sign in, and sign out**
The sign-in, sign-out, and second-account screens were taken seconds apart on 2026-09-13 with the test account privacy-b-20260913@example.com. They run from the filled sign-in form, to the list the app opens after sign-in with that email next to Sign out in the header, to the sign-in page the app went back to after I clicked Sign out. Loading `/` again at that point redirected straight back to the sign-in page and `/api/auth/token` answered 401, so the session was actually gone.

**Adding a contact and surviving a refresh**
On the review account these go from the empty list a new account starts with, to the add dialog with name and priority required, to the first saved contact, to the full list after a hard page reload, with all five entries still there because they live in Postgres.

**Sorting and filtering**
The first is the list sorted by priority with high first, and the second is the list filtered to high priority through the thumb index on the right edge, which leaves 2 of 5 entries.

**Editing and deleting**
The edit dialog opens with the contact's current values, and after saving, Marcus Chen's role reads Staff Data Scientist instead of Senior Data Scientist. Deleting asks for confirmation first, and afterwards the list is down to four entries and the low priority count is zero.

**Invalid input**
Saving with a blank name keeps the dialog open and shows the message under the field. A priority outside high, medium, and low cannot be picked in the form at all, so that case is shown under Evidence, where Postgres rejects it.

**A phone viewport**
At 390px wide the listing drops to one column and the priority filter moves under the running head.

**A second account**
This is User B, the 2026-09-13 test account, right after it was created on the live site. The list is empty even though User A, the review account, had four contacts at that moment. The stronger proof that accounts are isolated is the Data API transcript under Evidence, which skips the UI entirely and runs in both directions.

## Related

- [[Assignment Overview and Requirements]]: This note details the functionality of the web app
- [[Local Setup and Deployment Details]]: The screenshots were taken on the live Vercel site
- [[Model Performance and Results]]: The walkthrough demonstrates the app's operational results

## Sources

- [[wiki/Sources/Networking Tracker README|Networking Tracker README]]: `raw/Networking Tracker README.md`, sections "Walkthrough", "Sign up, sign in, and sign out", "Adding a contact and surviving a refresh", "Sorting and filtering", "Editing and deleting", "Invalid input" and more
