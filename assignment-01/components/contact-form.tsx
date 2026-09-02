'use client';

import { useState, type FormEvent } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { db } from '@/lib/neon';
import {
  describeDbError,
  LABELS,
  PRIORITIES,
  validateContact,
  type Contact,
  type ContactInput,
  type FieldErrors,
} from '@/lib/contacts';

/** Native select styled like the shadcn Input. Native pickers work best on phones. */
export const selectClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-base outline-none transition-colors focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 aria-invalid:border-destructive md:text-sm dark:bg-input/30';

export const capitalize = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

const EMPTY: ContactInput = { name: '', company: '', role: '', where_met: '', notes: '', priority: 'medium' };

function toInput(contact: Contact | null): ContactInput {
  if (!contact) return EMPTY;
  return {
    name: contact.name,
    company: contact.company ?? '',
    role: contact.role ?? '',
    where_met: contact.where_met ?? '',
    notes: contact.notes ?? '',
    priority: contact.priority,
  };
}

type Props = {
  open: boolean;
  /** The contact being edited, or null to create a new one. */
  contact: Contact | null;
  onOpenChange: (open: boolean) => void;
  onSaved: (contact: Contact, mode: 'created' | 'updated') => void;
};

export function ContactForm({ open, contact, onOpenChange, onSaved }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{contact ? 'Edit contact' : 'Add contact'}</DialogTitle>
          <DialogDescription>Name and priority are required. Everything else is optional.</DialogDescription>
        </DialogHeader>
        {/* The dialog unmounts its content when closed, so the fields start fresh on every open. */}
        <Fields contact={contact} onDone={() => onOpenChange(false)} onSaved={onSaved} />
      </DialogContent>
    </Dialog>
  );
}

function Fields({
  contact,
  onDone,
  onSaved,
}: {
  contact: Contact | null;
  onDone: () => void;
  onSaved: Props['onSaved'];
}) {
  const [values, setValues] = useState<ContactInput>(() => toInput(contact));
  const [errors, setErrors] = useState<FieldErrors>({});
  const [pending, setPending] = useState(false);

  const update = (key: keyof ContactInput, value: string) => setValues((current) => ({ ...current, [key]: value }));

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = validateContact(values);
    if (!result.ok) {
      setErrors(result.errors);
      return;
    }
    setErrors({});
    setPending(true);
    // user_id is never sent. Postgres fills it from the JWT, and RLS rejects anything else.
    const { data, error } = contact
      ? await db.from('contacts').update(result.value).eq('id', contact.id).select().single()
      : await db.from('contacts').insert(result.value).select().single();
    setPending(false);
    if (error || !data) {
      toast.error(describeDbError(error));
      return;
    }
    onSaved(data as Contact, contact ? 'updated' : 'created');
    onDone();
  }

  const field = (key: Exclude<keyof ContactInput, 'notes' | 'priority'>, extra?: React.ComponentProps<typeof Input>) => (
    <div className="grid gap-1.5">
      <Label htmlFor={key}>{LABELS[key]}</Label>
      <Input
        id={key}
        name={key}
        value={values[key]}
        onChange={(event) => update(key, event.target.value)}
        aria-invalid={Boolean(errors[key])}
        aria-describedby={errors[key] ? `${key}-error` : undefined}
        {...extra}
      />
      {errors[key] && (
        <p id={`${key}-error`} role="alert" className="text-sm text-destructive">
          {errors[key]}
        </p>
      )}
    </div>
  );

  return (
    <form onSubmit={onSubmit} noValidate className="grid gap-4">
      {field('name', { autoFocus: true })}
      <div className="grid gap-4 sm:grid-cols-2">
        {field('company')}
        {field('role')}
      </div>
      {field('where_met', { placeholder: 'Haas mixer, a class, a conference' })}
      <div className="grid gap-1.5">
        <Label htmlFor="priority">{LABELS.priority}</Label>
        <select
          id="priority"
          name="priority"
          value={values.priority}
          onChange={(event) => update('priority', event.target.value)}
          aria-invalid={Boolean(errors.priority)}
          className={selectClassName}
        >
          {PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>
              {capitalize(priority)}
            </option>
          ))}
        </select>
        {errors.priority && (
          <p role="alert" className="text-sm text-destructive">
            {errors.priority}
          </p>
        )}
      </div>
      <div className="grid gap-1.5">
        <Label htmlFor="notes">{LABELS.notes}</Label>
        <Textarea
          id="notes"
          name="notes"
          rows={3}
          value={values.notes}
          onChange={(event) => update('notes', event.target.value)}
          aria-invalid={Boolean(errors.notes)}
        />
        {errors.notes && (
          <p role="alert" className="text-sm text-destructive">
            {errors.notes}
          </p>
        )}
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onDone} disabled={pending}>
          Cancel
        </Button>
        <Button type="submit" disabled={pending}>
          {pending ? 'Saving' : contact ? 'Save changes' : 'Add contact'}
        </Button>
      </DialogFooter>
    </form>
  );
}
