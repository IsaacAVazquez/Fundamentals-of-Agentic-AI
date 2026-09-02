import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateContact } from '../lib/contacts.ts';

const valid = {
  name: '  Ada Lovelace ',
  company: 'Analytical Engines',
  role: 'Engineer',
  where_met: 'Haas mixer',
  notes: '',
  priority: 'high',
};

test('accepts a valid contact, trims text, and stores blanks as null', () => {
  const result = validateContact(valid);
  assert.equal(result.ok, true);
  if (!result.ok) return;
  assert.equal(result.value.name, 'Ada Lovelace');
  assert.equal(result.value.notes, null);
  assert.equal(result.value.priority, 'high');
});

test('rejects an empty or whitespace-only name', () => {
  for (const name of ['', '   ']) {
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
  const result = validateContact({ ...valid, notes: 'x'.repeat(2001) });
  assert.equal(result.ok, false);
  if (result.ok) return;
  assert.match(result.errors.notes ?? '', /2000 characters/);
});

// The database enforces the same rules with CHECK constraints. This case talks to Neon
// directly, so it runs only when DATABASE_URL is available.
test(
  'database CHECK constraints reject a blank name and an invalid priority',
  { skip: process.env.DATABASE_URL ? false : 'DATABASE_URL not set' },
  async () => {
    const { neon } = await import('@neondatabase/serverless');
    const sql = neon(process.env.DATABASE_URL!);
    const isCheckViolation = (error: unknown) => (error as { code?: string }).code === '23514';
    await assert.rejects(
      sql.query("insert into contacts (user_id, name, priority) values ('test-user', 'Ada', 'urgent')"),
      isCheckViolation,
    );
    await assert.rejects(
      sql.query("insert into contacts (user_id, name, priority) values ('test-user', '   ', 'high')"),
      isCheckViolation,
    );
  },
);
