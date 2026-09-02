'use client';

import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { ArrowDown, ArrowUp, ArrowUpDown, Pencil, Plus, Trash2 } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ContactForm, capitalize, selectClassName } from '@/components/contact-form';
import { authClient, runAuth } from '@/lib/auth/client';
import { describeDbError, PRIORITIES, type Contact, type Priority } from '@/lib/contacts';
import { clearToken, db } from '@/lib/neon';
import { cn } from '@/lib/utils';

type SortKey = 'name' | 'company' | 'priority' | 'created_at';
type Sort = { key: SortKey; dir: 'asc' | 'desc' };

const PRIORITY_RANK: Record<Priority, number> = { high: 0, medium: 1, low: 2 };
const PRIORITY_BADGE: Record<Priority, 'destructive' | 'default' | 'secondary'> = {
  high: 'destructive',
  medium: 'default',
  low: 'secondary',
};

const isAuthProblem = (error: { code?: string; message?: string }) =>
  error.code === 'PGRST301' || /authentication required/i.test(error.message ?? '');

export function ContactsPage() {
  const router = useRouter();
  const { data: session } = authClient.useSession();
  const [contacts, setContacts] = useState<Contact[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<'all' | Priority>('all');
  const [sort, setSort] = useState<Sort>({ key: 'created_at', dir: 'desc' });
  const [editor, setEditor] = useState<{ open: boolean; contact: Contact | null }>({ open: false, contact: null });
  const [deleting, setDeleting] = useState<Contact | null>(null);

  const load = useCallback(() => {
    // State updates happen inside the promise callback, never synchronously in an effect.
    db.from('contacts')
      .select('*')
      .order('created_at', { ascending: false })
      .then(({ data, error }) => {
        if (error) {
          if (isAuthProblem(error)) {
            router.push('/sign-in');
            return;
          }
          setLoadError(describeDbError(error));
          return;
        }
        setLoadError(null);
        setContacts(data as Contact[]);
      });
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  const visible = useMemo(() => {
    if (!contacts) return [];
    const needle = query.trim().toLowerCase();
    const rows = contacts.filter(
      (contact) =>
        (priorityFilter === 'all' || contact.priority === priorityFilter) &&
        (!needle ||
          [contact.name, contact.company, contact.role, contact.where_met, contact.notes].some((value) =>
            value?.toLowerCase().includes(needle),
          )),
    );
    const direction = sort.dir === 'asc' ? 1 : -1;
    return rows.sort((a, b) => {
      if (sort.key === 'priority') return (PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority]) * direction;
      if (sort.key === 'created_at') return a.created_at.localeCompare(b.created_at) * direction;
      return (a[sort.key] ?? '').localeCompare(b[sort.key] ?? '', undefined, { sensitivity: 'base' }) * direction;
    });
  }, [contacts, query, priorityFilter, sort]);

  function toggleSort(key: SortKey) {
    setSort((current) =>
      current.key === key
        ? { key, dir: current.dir === 'asc' ? 'desc' : 'asc' }
        : { key, dir: key === 'created_at' ? 'desc' : 'asc' },
    );
  }

  function onSaved(saved: Contact, mode: 'created' | 'updated') {
    setContacts((list) =>
      mode === 'created' ? [saved, ...(list ?? [])] : (list ?? []).map((c) => (c.id === saved.id ? saved : c)),
    );
    toast.success(mode === 'created' ? `Added ${saved.name}.` : `Saved changes to ${saved.name}.`);
  }

  async function confirmDelete() {
    if (!deleting) return;
    const target = deleting;
    const { error } = await db.from('contacts').delete().eq('id', target.id);
    setDeleting(null);
    if (error) {
      toast.error(describeDbError(error));
      return;
    }
    setContacts((list) => list?.filter((c) => c.id !== target.id) ?? null);
    toast.success(`Deleted ${target.name}.`);
  }

  async function signOut() {
    const message = await runAuth(() => authClient.signOut());
    if (message) {
      toast.error(message);
      return;
    }
    clearToken();
    router.push('/sign-in');
    router.refresh();
  }

  const openNew = () => setEditor({ open: true, contact: null });

  const sortHead = (label: string, key: SortKey, className?: string) => (
    <TableHead className={className} aria-sort={sort.key === key ? (sort.dir === 'asc' ? 'ascending' : 'descending') : 'none'}>
      <button type="button" className="inline-flex items-center gap-1 hover:text-foreground" onClick={() => toggleSort(key)}>
        {label}
        {sort.key === key ? (
          sort.dir === 'asc' ? <ArrowUp className="size-3.5" /> : <ArrowDown className="size-3.5" />
        ) : (
          <ArrowUpDown className="size-3.5 opacity-40" />
        )}
      </button>
    </TableHead>
  );

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 p-4 sm:p-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Networking Tracker</h1>
          <p className="text-sm text-muted-foreground">People to stay connected with at Berkeley.</p>
        </div>
        <div className="flex items-center gap-3 text-sm">
          {session?.user?.email && <span className="hidden text-muted-foreground sm:inline">{session.user.email}</span>}
          <Button variant="outline" size="sm" onClick={signOut}>
            Sign out
          </Button>
        </div>
      </header>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <Input
          aria-label="Search contacts"
          placeholder="Search name, company, role, notes"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="sm:max-w-xs"
        />
        <select
          aria-label="Filter by priority"
          value={priorityFilter}
          onChange={(event) => setPriorityFilter(event.target.value as 'all' | Priority)}
          className={cn(selectClassName, 'sm:w-44')}
        >
          <option value="all">All priorities</option>
          {PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>
              {capitalize(priority)}
            </option>
          ))}
        </select>
        <Button className="sm:ml-auto" onClick={openNew}>
          <Plus /> Add contact
        </Button>
      </div>

      {loadError ? (
        <Card>
          <CardContent className="flex flex-col items-start gap-3 py-6">
            <p role="alert" className="text-sm text-destructive">
              {loadError}
            </p>
            <Button variant="outline" size="sm" onClick={load}>
              Try again
            </Button>
          </CardContent>
        </Card>
      ) : contacts === null ? (
        <div className="space-y-2" aria-busy="true" aria-label="Loading contacts">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : contacts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
            <p className="font-medium">No contacts yet</p>
            <p className="text-sm text-muted-foreground">Add the first person you want to keep in touch with.</p>
            <Button onClick={openNew}>
              <Plus /> Add contact
            </Button>
          </CardContent>
        </Card>
      ) : visible.length === 0 ? (
        <p className="py-10 text-center text-sm text-muted-foreground">No contacts match your search or filter.</p>
      ) : (
        <Table className="block md:table">
          <TableHeader className="hidden md:table-header-group">
            <TableRow>
              {sortHead('Name', 'name')}
              {sortHead('Company', 'company')}
              <TableHead>Role</TableHead>
              <TableHead>Where met</TableHead>
              {sortHead('Priority', 'priority')}
              {sortHead('Added', 'created_at')}
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="block md:table-row-group">
            {visible.map((contact) => (
              <TableRow key={contact.id} className="block border-b py-3 md:table-row md:py-0">
                <TableCell className="block py-1 text-base font-medium md:table-cell md:py-2 md:text-sm">{contact.name}</TableCell>
                <Cell label="Company">{contact.company}</Cell>
                <Cell label="Role">{contact.role}</Cell>
                <Cell label="Where met">{contact.where_met}</Cell>
                <Cell label="Priority">
                  <Badge variant={PRIORITY_BADGE[contact.priority]}>{capitalize(contact.priority)}</Badge>
                </Cell>
                <Cell label="Added" className="text-muted-foreground">
                  {new Date(contact.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                </Cell>
                {contact.notes && (
                  <TableCell className="block whitespace-pre-wrap py-1 text-muted-foreground md:hidden">{contact.notes}</TableCell>
                )}
                <TableCell className="block py-1 md:table-cell md:py-2 md:text-right">
                  <div className="flex gap-1 md:justify-end">
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label={`Edit ${contact.name}`}
                      onClick={() => setEditor({ open: true, contact })}
                    >
                      <Pencil />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label={`Delete ${contact.name}`}
                      onClick={() => setDeleting(contact)}
                    >
                      <Trash2 />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <ContactForm
        open={editor.open}
        contact={editor.contact}
        onOpenChange={(open) => setEditor((current) => ({ ...current, open }))}
        onSaved={onSaved}
      />

      <AlertDialog open={deleting !== null} onOpenChange={(open) => !open && setDeleting(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {deleting?.name}?</AlertDialogTitle>
            <AlertDialogDescription>This removes the contact from your list. There is no undo.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction variant="destructive" onClick={confirmDelete}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

/** A table cell that shows its column label on narrow screens, where rows stack into cards. */
function Cell({ label, className, children }: { label: string; className?: string; children: ReactNode }) {
  if (children === null || children === undefined || children === '') return <TableCell className="hidden md:table-cell" />;
  return (
    <TableCell className={cn('flex items-baseline justify-between gap-4 py-1 md:table-cell md:py-2', className)}>
      <span className="text-xs text-muted-foreground md:hidden">{label}</span>
      <span className="text-right md:text-left">{children}</span>
    </TableCell>
  );
}
