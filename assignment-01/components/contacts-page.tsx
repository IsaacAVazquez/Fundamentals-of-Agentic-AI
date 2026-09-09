'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { ArrowDown, ArrowUp, Pencil, Plus, Trash2 } from 'lucide-react';
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
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { ContactForm, capitalize, selectClassName } from '@/components/contact-form';
import { authClient, runAuth } from '@/lib/auth/client';
import { describeDbError, PRIORITIES, type Contact, type Priority } from '@/lib/contacts';
import { clearToken, db } from '@/lib/neon';
import { cn } from '@/lib/utils';

type SortKey = 'name' | 'company' | 'priority' | 'created_at';
type Sort = { key: SortKey; dir: 'asc' | 'desc' };
type Filter = 'all' | Priority;

const PRIORITY_RANK: Record<Priority, number> = { high: 0, medium: 1, low: 2 };
const SORT_LABELS: Record<SortKey, string> = { name: 'Name', company: 'Company', priority: 'Priority', created_at: 'Date added' };
const CONDENSED = 'font-condensed uppercase tracking-[0.12em]';

const isAuthProblem = (error: { code?: string; message?: string }) =>
  error.code === 'PGRST301' || /authentication required/i.test(error.message ?? '');

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });

export function ContactsPage() {
  const router = useRouter();
  const { data: session } = authClient.useSession();
  const [contacts, setContacts] = useState<Contact[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<Filter>('all');
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

  const counts = useMemo(() => {
    const tally: Record<Filter, number> = { all: 0, high: 0, medium: 0, low: 0 };
    for (const contact of contacts ?? []) {
      tally.all += 1;
      tally[contact.priority] += 1;
    }
    return tally;
  }, [contacts]);

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
  const filtered = priorityFilter !== 'all' || query.trim() !== '';

  // The thumb index. Each tab is a priority; the open one is stamped gold and stands proud of the rest.
  const thumbIndex = (orientation: 'vertical' | 'horizontal') => (
    <nav
      aria-label="Filter by priority"
      className={
        orientation === 'vertical'
          ? 'sticky top-6 hidden w-28 flex-col gap-1.5 md:flex'
          : 'flex gap-1.5 md:hidden'
      }
    >
      {(['all', ...PRIORITIES] as Filter[]).map((value) => {
        const active = priorityFilter === value;
        return (
          <button
            key={value}
            type="button"
            aria-pressed={active}
            onClick={() => setPriorityFilter(value)}
            className={cn(
              CONDENSED,
              'flex items-center justify-between gap-2 px-3 py-2 text-sm font-semibold outline-none transition-[transform,background-color,color] duration-200 ease-out focus-visible:ring-3 focus-visible:ring-ring/50',
              orientation === 'vertical' ? 'rounded-l-md' : 'flex-1 rounded-b-md px-2 py-1.5 text-xs',
              active
                ? cn('bg-gold text-gold-foreground', orientation === 'vertical' ? '-translate-x-1.5' : 'translate-y-0.5')
                : 'bg-cover text-cover-foreground hover:bg-primary/90',
            )}
          >
            <span>{value === 'all' ? 'All' : capitalize(value)}</span>
            <span className="text-xs tabular-nums opacity-80">{counts[value]}</span>
          </button>
        );
      })}
    </nav>
  );

  return (
    <div className="flex flex-1 flex-col">
      {/* The cover band: blue cloth, gold stamping, and the owner's inscription. */}
      <header className="bg-cover text-cover-foreground">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-end justify-between gap-x-8 gap-y-4 px-4 pb-5 pt-6 sm:px-6">
          <div>
            <h1 className={cn(CONDENSED, 'text-3xl font-bold leading-none text-gold sm:text-4xl')}>Networking Tracker</h1>
            <p className="mt-2 text-sm text-cover-foreground/85">People to stay connected with at Berkeley.</p>
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
            {session?.user?.email && (
              <p>
                <span className={cn(CONDENSED, 'text-xs font-semibold text-cover-foreground/85')}>This copy belongs to</span>{' '}
                <span className="text-gold">{session.user.email}</span>
              </p>
            )}
            <Button
              variant="outline"
              size="sm"
              className="border-gold/70 bg-transparent text-gold hover:bg-gold hover:text-gold-foreground"
              onClick={signOut}
            >
              Sign out
            </Button>
          </div>
        </div>
      </header>

      <main className="flex flex-1 flex-col">
        {/* The running head: live counts on the left, lookup, sort, and the one solid action on the right. */}
        <div className="mx-auto w-full max-w-6xl px-4 sm:px-6">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-3 border-b border-rule py-4">
            <p aria-live="polite" className={cn(CONDENSED, 'text-sm font-semibold tabular-nums')}>
              {contacts === null ? (
                <span className="text-muted-foreground">Loading entries</span>
              ) : (
                <span key={`${visible.length}-${counts.all}-${counts.high}`} className="inline-block animate-in fade-in-0 duration-300">
                  {filtered ? `${visible.length} of ${counts.all}` : counts.all} {counts.all === 1 && !filtered ? 'entry' : 'entries'}
                  {!filtered && counts.high > 0 && <span className="text-muted-foreground"> · {counts.high} high</span>}
                </span>
              )}
            </p>
            <div className="flex w-full flex-wrap items-center gap-2 sm:ml-auto sm:w-auto">
              <Input
                aria-label="Search contacts"
                placeholder="Search name, company, role, notes"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="min-w-0 basis-full sm:basis-auto sm:w-64"
              />
              <select
                aria-label="Sort by"
                value={sort.key}
                onChange={(event) => setSort({ key: event.target.value as SortKey, dir: event.target.value === 'created_at' ? 'desc' : 'asc' })}
                className={cn(selectClassName, 'min-w-0 flex-1 sm:w-auto sm:flex-none')}
              >
                {(Object.keys(SORT_LABELS) as SortKey[]).map((key) => (
                  <option key={key} value={key}>
                    Sort: {SORT_LABELS[key]}
                  </option>
                ))}
              </select>
              <Button
                variant="outline"
                size="icon"
                aria-label={sort.dir === 'asc' ? 'Sorted ascending. Switch to descending' : 'Sorted descending. Switch to ascending'}
                onClick={() => setSort((current) => ({ ...current, dir: current.dir === 'asc' ? 'desc' : 'asc' }))}
              >
                {sort.dir === 'asc' ? <ArrowUp /> : <ArrowDown />}
              </Button>
              <Button onClick={openNew}>
                <Plus /> Add contact
              </Button>
            </div>
          </div>
          {thumbIndex('horizontal')}
        </div>

        {/* The listing page, with the thumb index cut into its right edge on wide screens. */}
        <div className="relative flex-1">
          <div className="mx-auto w-full max-w-6xl px-4 pb-12 sm:px-6 md:pr-36">
            {loadError ? (
              <div className="flex flex-col items-start gap-3 border-b border-rule py-8">
                <p role="alert" className="text-sm text-destructive">
                  {loadError}
                </p>
                <Button variant="outline" size="sm" onClick={load}>
                  Try again
                </Button>
              </div>
            ) : contacts === null ? (
              <div aria-busy="true" aria-label="Loading contacts" className="md:columns-2 md:gap-12">
                {[0, 1, 2, 3].map((i) => (
                  <div key={i} className="border-b border-rule py-3.5 break-inside-avoid">
                    <Skeleton className="h-4 w-40" />
                    <Skeleton className="mt-2 ml-4 h-3 w-56" />
                  </div>
                ))}
              </div>
            ) : contacts.length === 0 ? (
              <div className="flex flex-col items-center py-20 text-center">
                <p className={cn(CONDENSED, 'text-lg font-bold')}>No contacts yet</p>
                <p className="mt-2 max-w-xs text-sm text-muted-foreground text-pretty">Add the first person you want to keep in touch with.</p>
                <Button className="mt-6" onClick={openNew}>
                  <Plus /> Add contact
                </Button>
              </div>
            ) : visible.length === 0 ? (
              <p className="py-16 text-center text-sm text-muted-foreground">No contacts match your search or filter.</p>
            ) : (
              <ul aria-label="Contacts" className="text-sm md:columns-2 md:gap-12">
                {visible.map((contact) => {
                  const line = [contact.company, contact.role].filter(Boolean).join(', ');
                  return (
                    <li key={contact.id} className="border-b border-rule py-3 break-inside-avoid">
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-base font-semibold leading-snug">{contact.name}</p>
                        <div className="-mt-1 -mr-1.5 flex shrink-0 gap-0.5">
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
                      </div>
                      {line && <p className="pl-4">{line}</p>}
                      {contact.where_met && <p className="pl-4 italic text-muted-foreground">{contact.where_met}</p>}
                      {contact.notes && <p className="whitespace-pre-wrap pl-4 text-muted-foreground">{contact.notes}</p>}
                      <p className="flex items-center gap-3 pl-4 pt-1.5">
                        <PriorityMark priority={contact.priority} />
                        <time dateTime={contact.created_at} className="whitespace-nowrap text-xs tabular-nums text-muted-foreground">
                          Added {formatDate(contact.created_at)}
                        </time>
                      </p>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
          {/* A full-height column on the fore-edge, so the index follows the scroll without leaving the edge. */}
          <div className="absolute inset-y-0 right-0 hidden w-28 md:block">{thumbIndex('vertical')}</div>
        </div>
      </main>

      <ContactForm
        open={editor.open}
        contact={editor.contact}
        onOpenChange={(open) => setEditor((current) => ({ ...current, open }))}
        onSaved={onSaved}
      />

      <AlertDialog open={deleting !== null} onOpenChange={(open) => !open && setDeleting(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className={cn(CONDENSED, 'text-lg font-bold')}>Delete {deleting?.name}?</AlertDialogTitle>
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

/** Priority as a typographic register: high is stamped gold, medium is ruled, low is set quiet. */
function PriorityMark({ priority }: { priority: Priority }) {
  return (
    <span
      className={cn(
        CONDENSED,
        'inline-block text-[11px] leading-none tracking-[0.14em]',
        priority === 'high' && 'bg-gold px-1.5 py-1 font-bold text-gold-foreground',
        priority === 'medium' && 'border border-foreground px-1.5 py-[3px] font-semibold',
        priority === 'low' && 'font-medium text-muted-foreground',
      )}
    >
      {capitalize(priority)}
    </span>
  );
}

