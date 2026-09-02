export const PRIORITIES = ['high', 'medium', 'low'] as const;
export type Priority = (typeof PRIORITIES)[number];

export type Contact = {
  id: string;
  user_id: string;
  name: string;
  company: string | null;
  role: string | null;
  where_met: string | null;
  notes: string | null;
  priority: Priority;
  created_at: string;
};

/** Raw form values. Everything is a string because it comes straight from inputs. */
export type ContactInput = Record<'name' | 'company' | 'role' | 'where_met' | 'notes' | 'priority', string>;
/** What the app sends to the database. `user_id` is never sent; Postgres fills it from the JWT. */
export type ContactValues = Omit<Contact, 'id' | 'user_id' | 'created_at'>;
export type FieldErrors = Partial<Record<keyof ContactInput, string>>;

export const LABELS: Record<keyof ContactInput, string> = {
  name: 'Name',
  company: 'Company',
  role: 'Role',
  where_met: 'Where you met',
  notes: 'Notes',
  priority: 'Priority',
};

const MAX_LENGTH = { name: 120, company: 120, role: 120, where_met: 200, notes: 2000 } as const;

export function isPriority(value: string): value is Priority {
  return (PRIORITIES as readonly string[]).includes(value);
}

/**
 * Pure validation shared by the form and the automated test.
 * The database enforces the same two hard rules (non-blank name, priority in the allowed set)
 * with CHECK constraints, so a request that skips this function still fails safely.
 */
export function validateContact(
  input: ContactInput,
): { ok: true; value: ContactValues } | { ok: false; errors: FieldErrors } {
  const errors: FieldErrors = {};
  const name = input.name.trim();
  if (!name) errors.name = 'Name is required.';
  else if (name.length > MAX_LENGTH.name) errors.name = `Name must be ${MAX_LENGTH.name} characters or fewer.`;
  if (!isPriority(input.priority)) errors.priority = 'Priority must be high, medium, or low.';
  for (const key of ['company', 'role', 'where_met', 'notes'] as const) {
    if (input[key].trim().length > MAX_LENGTH[key]) {
      errors[key] = `${LABELS[key]} must be ${MAX_LENGTH[key]} characters or fewer.`;
    }
  }
  if (Object.keys(errors).length > 0) return { ok: false, errors };

  const optional = (value: string) => value.trim() || null;
  return {
    ok: true,
    value: {
      name,
      company: optional(input.company),
      role: optional(input.role),
      where_met: optional(input.where_met),
      notes: optional(input.notes),
      priority: input.priority as Priority,
    },
  };
}

/** Turns a Data API (PostgREST) error into a sentence the UI can show. */
export function describeDbError(error: { code?: string; message?: string } | null | undefined): string {
  switch (error?.code) {
    case '23514':
      return 'The database rejected this contact. Name must not be blank and priority must be high, medium, or low.';
    case '23502':
      return 'A required field was missing.';
    case '42501':
      return 'You do not have access to that contact.';
    case 'PGRST301':
      return 'Your session has expired. Sign in again.';
    default:
      return error?.message || 'Something went wrong. Try again.';
  }
}
