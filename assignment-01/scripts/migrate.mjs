import { readFileSync } from 'node:fs';
import { neon } from '@neondatabase/serverless';

const url = process.env.DATABASE_URL;
if (!url) {
  console.error('DATABASE_URL is not set. Put it in .env.local or export it before running this.');
  process.exit(1);
}

const schema = readFileSync(new URL('../db/schema.sql', import.meta.url), 'utf8');
// The Data API-style HTTP driver runs one statement per call, so strip the SQL comments and split on semicolons.
const statements = schema
  .replace(/--.*$/gm, '')
  .split(';')
  .map((statement) => statement.trim())
  .filter(Boolean);

const sql = neon(url);
for (const statement of statements) {
  await sql.query(statement);
}
console.log(`Applied ${statements.length} statements from db/schema.sql.`);
