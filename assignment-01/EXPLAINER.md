# What this app is doing

This is a plain-language walkthrough of the networking tracker in this folder. The README is the graded document and covers setup, architecture, and evidence. This file is for anyone who opens the code and wants to know what each piece does and why it's there, including people who haven't worked with Next.js or Postgres before.

The app itself is small. You sign up with an email and password, you get a private list of people you want to stay in touch with, and you can add, edit, delete, search, filter, and sort that list. What makes it worth reading is that every request is checked twice, once by the app and once by the database, so a signed-in person can only ever touch their own rows.

## The five pieces and how a request moves through them

There are five moving parts. The browser runs the interface, Next.js serves it and holds the session, Neon Auth handles accounts and passwords, the Neon Data API turns web requests into database queries, and Postgres stores the rows and enforces who may see them.

When you load the site, the first thing that runs is `proxy.ts`, which is Next.js middleware, meaning code that runs before a page is rendered. It matches only `/`, the contacts page, and sends anyone without a valid session to `/sign-in`. That's why you never see the contacts page flash before a redirect.

Signing in posts your email and password through `app/api/auth/[...path]/route.ts`, which is a catch-all route that hands every `/api/auth/*` request to Neon's managed authentication service. The app proxies that traffic rather than letting the browser talk to Neon directly, so the session lands in a first-party cookie marked HttpOnly, which means JavaScript in the page cannot read it. `lib/auth/server.ts` is where that instance is configured, and the cookie is signed with a secret that exists only on the server.

Once you're signed in, the page needs a way to query the database. It doesn't hold a database password. Instead `lib/neon.ts` asks the app's own `/api/auth/token` endpoint for a short-lived signed token, called a JWT, and keeps it in memory until 30 seconds before it expires. The session cookie travels with that request automatically, so the browser never handles a long-lived secret. Every database call then carries the token in an `Authorization` header.

The database is the last gate, and it's the one that actually matters. `db/schema.sql` turns on row level security on the `contacts` table and adds four policies, one each for select, insert, update, and delete, all of which compare `auth.user_id()`, the user id inside the token, against the `user_id` column on the row. The column defaults to `auth.user_id()`, so the app never sends a user id at all and cannot get it wrong.

If someone forged a request for another person's contact, Postgres would return nothing rather than trusting the app to have filtered correctly.

## What each file does

| File | What it does |
| --- | --- |
| `proxy.ts` | Next.js middleware that redirects signed-out visitors away from the contacts page |
| `lib/auth/server.ts` | Configures server-side auth, including the signed HttpOnly session cookie |
| `app/api/auth/[...path]/route.ts` | Proxies every auth request to Neon's managed service |
| `lib/auth/client.ts` | The browser-side auth client, plus a small wrapper that turns any failure into one readable sentence |
| `lib/neon.ts` | Fetches and caches the session token, and creates the database client that carries it |
| `db/schema.sql` | The `contacts` table, its constraints, its index, and the four row level security policies |
| `scripts/migrate.mjs` | Applies `db/schema.sql` one statement at a time over Neon's HTTP driver |
| `lib/contacts.ts` | The contact type, the field labels and length limits, the validation function, and the database-error translator |
| `components/auth-form.tsx` | One component that renders both sign-in and sign-up |
| `components/contact-form.tsx` | The add and edit dialog, which validates before it writes |
| `components/contacts-page.tsx` | The list itself, with search, the priority filter, sorting, counts, delete confirmation, and sign out |
| `app/layout.tsx`, `app/page.tsx`, `app/sign-in`, `app/sign-up` | The page shell, the fonts, the toast host, and the three routes |
| `app/globals.css` | Tailwind setup and the color and type tokens the design uses |
| `components/ui/` | Generated shadcn components, meaning the buttons, inputs, dialogs, and table primitives |
| `tests/contacts.test.ts` | Four tests for the validation rules plus one that proves the database rejects bad rows on its own |

## Validation happens in two places on purpose

`validateContact` in `lib/contacts.ts` is a pure function, meaning it takes form values and returns either a cleaned contact or a set of field errors, with no database and no side effects. It trims whitespace, requires a name, requires the priority to be high, medium, or low, turns empty optional fields into `null`, and enforces length limits. Because it's pure, the test file can check it directly without a browser or a network.

The same two hard rules are also written into the table as CHECK constraints, which is deliberate. The form check is there so you get a useful message next to the field, and the database check is there so a request that skips the form still fails. The last test in `tests/contacts.test.ts` proves the second half by inserting a blank name and an invalid priority straight into Postgres and asserting both come back as constraint violations. That test only runs when `DATABASE_URL` is set, so the suite still passes offline.

When the database does reject something, `describeDbError` maps the Postgres error code to a sentence a person can act on, so code `23514` becomes a note about name and priority rather than a raw error string.

## What the contacts page is doing while you use it

`components/contacts-page.tsx` loads every row once, newest first, and then does the searching, filtering, and sorting in the browser over that list. For a personal contact list that's the simpler choice, and it means typing in the search box doesn't hit the network. The priority tabs down the right edge are both a filter and a live count of each group.

After you add or edit a contact, the page updates its copy of the list from the row the database returned rather than reloading everything, which is why the change appears immediately. Deleting asks for confirmation first, then removes the row and shows a toast. Signing out clears the cached token in addition to ending the session, so nothing stale is left in memory. If a database call comes back with an expired session, the page sends you to sign-in instead of showing a broken list.

## The design files

None of these change how the app behaves.

`PRODUCT.md` and `DESIGN.md` describe the interface and the direction it was built to, and `.impeccable/` holds the notes the design tooling uses. The comment block in `app/layout.tsx` is the direction contract for that work, kept in the markup so it survives a production build.
