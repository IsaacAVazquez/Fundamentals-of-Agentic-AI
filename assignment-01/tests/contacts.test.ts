import { test } from 'node:test';
import assert from 'node:assert/strict';
import { describeDbError, isAuthProblem, validateContact } from '../lib/contacts.ts';

const valid = {
  name: '  Ada Lovelace ',
  company: 'Analytical Engines',
  role: 'Engineer',
  where_met: 'Haas mixer',
  notes: '',
  priority: 'high',
};

const LIMITS = { name: 120, company: 120, role: 120, where_met: 200, notes: 2000 } as const;

test('accepts a valid contact, trims text, and stores blanks as null', () => {
  const result = validateContact({ ...valid, role: '   ', notes: '  Met at the mixer.  ' });
  assert.equal(result.ok, true);
  if (!result.ok) return;
  assert.deepEqual(result.value, {
    name: 'Ada Lovelace',
    company: 'Analytical Engines',
    role: null,
    where_met: 'Haas mixer',
    notes: 'Met at the mixer.',
    priority: 'high',
  });
  const blankNotes = validateContact(valid);
  assert.equal(blankNotes.ok && blankNotes.value.notes, null);
});

test('rejects an empty or whitespace-only name', () => {
  for (const name of ['', '   ', '\t', '\n']) {
    const result = validateContact({ ...valid, name });
    assert.equal(result.ok, false);
    if (result.ok) return;
    assert.equal(result.errors.name, 'Name is required.');
  }
});

test('rejects a priority outside high, medium, and low', () => {
  for (const priority of ['urgent', 'HIGH', '']) {
    const result = validateContact({ ...valid, priority });
    assert.equal(result.ok, false);
    if (result.ok) return;
    assert.equal(result.errors.priority, 'Priority must be high, medium, or low.');
  }
});

test('rejects fields past their length limits', () => {
  for (const [key, limit] of Object.entries(LIMITS) as [keyof typeof LIMITS, number][]) {
    assert.equal(validateContact({ ...valid, [key]: 'x'.repeat(limit) }).ok, true, `${key} at ${limit} characters`);
    assert.equal(validateContact({ ...valid, [key]: `  ${'x'.repeat(limit)}  ` }).ok, true, `${key} is trimmed first`);
    const result = validateContact({ ...valid, [key]: 'x'.repeat(limit + 1) });
    assert.equal(result.ok, false, `${key} at ${limit + 1} characters`);
    if (result.ok) return;
    assert.match(result.errors[key] ?? '', new RegExp(`${limit} characters`));
  }
});

test('describes database errors as sentences', () => {
  assert.match(describeDbError({ code: '23514' }), /rejected this contact/);
  assert.equal(describeDbError({ code: '23502' }), 'A required field was missing.');
  assert.equal(describeDbError({ code: '42501' }), 'You do not have access to that contact.');
  assert.equal(describeDbError({ code: 'PGRST301' }), 'Your session has expired. Sign in again.');
  assert.equal(
    describeDbError({ code: '', message: 'TypeError: Failed to fetch' }),
    "Couldn't reach the database. Check your connection and try again.",
  );
  assert.equal(describeDbError({ code: 'XX000', message: 'disk full' }), 'disk full');
  assert.equal(describeDbError(null), 'Something went wrong. Try again.');
});

test('recognizes a missing or expired session', () => {
  assert.equal(isAuthProblem({ code: 'PGRST301', message: 'JWT expired' }), true);
  assert.equal(
    isAuthProblem({ code: '', message: 'AuthRequiredError: Authentication required. A valid token is needed to access the resource.' }),
    true,
  );
  assert.equal(isAuthProblem({ code: '23514', message: 'new row violates check constraint' }), false);
  assert.equal(isAuthProblem(null), false);
});

// The database enforces the same rules with CHECK constraints. This case talks to Neon
// directly, so it runs only when DATABASE_URL is available.
test(
  'database CHECK constraints reject a blank name, an invalid priority, and an over-long field',
  { skip: process.env.DATABASE_URL ? false : 'DATABASE_URL not set' },
  async () => {
    const { neon } = await import('@neondatabase/serverless');
    const sql = neon(process.env.DATABASE_URL!);
    const isCheckViolation = (error: unknown) => (error as { code?: string }).code === '23514';
    const insert = (name: string, priority: string) =>
      sql.query('insert into contacts (user_id, name, priority) values ($1, $2, $3)', ['test-user', name, priority]);
    await assert.rejects(insert('Ada', 'urgent'), isCheckViolation);
    await assert.rejects(insert('   ', 'high'), isCheckViolation);
    await assert.rejects(insert('\t', 'high'), isCheckViolation);
    await assert.rejects(insert('x'.repeat(121), 'high'), isCheckViolation);
  },
);
