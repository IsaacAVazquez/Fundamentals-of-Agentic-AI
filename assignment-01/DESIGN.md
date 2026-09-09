---
name: Networking Tracker
description: A private edition of the Berkeley class directory, with the priority filter as the book's thumb index.
colors:
  cover: "#003262"
  cover-foreground: "#ffffff"
  gold: "#fdb515"
  gold-foreground: "#003262"
  paper: "#ffffff"
  ink: "#141414"
  rule: "#cfd3d8"
  muted: "#f3f5f7"
  muted-foreground: "#5b6168"
  secondary: "#eef1f4"
  input: "#6f7780"
  destructive: "#b3261e"
typography:
  display:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.12em"
  headline:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.1em"
  title:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: "0.12em"
  running-head:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.43
    letterSpacing: "0.12em"
  entry-name:
    fontFamily: "Libre Franklin, Franklin Gothic, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.375
    letterSpacing: "normal"
  body:
    fontFamily: "Libre Franklin, Franklin Gothic, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.43
    letterSpacing: "normal"
  label:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.12em"
  priority-mark:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.14em"
  caption:
    fontFamily: "Libre Franklin, Franklin Gothic, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.33
    letterSpacing: "normal"
rounded:
  none: "0px"
  md: "2.56px"
  lg: "3.2px"
  xl: "4.48px"
spacing:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  2xl: "24px"
  column-gutter: "48px"
  thumb-index: "112px"
  fore-edge: "144px"
components:
  button-primary:
    backgroundColor: "{colors.cover}"
    textColor: "{colors.cover-foreground}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-primary-hover:
    backgroundColor: "rgba(0, 50, 98, 0.8)"
  button-outline:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  button-outline-hover:
    backgroundColor: "{colors.muted}"
  button-band-outline:
    backgroundColor: "transparent"
    textColor: "{colors.gold}"
    rounded: "{rounded.md}"
    padding: "0 10px"
    height: "28px"
  button-band-outline-hover:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.gold-foreground}"
  button-ghost-icon:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    size: "28px"
  button-ghost-icon-hover:
    backgroundColor: "{colors.muted}"
  button-destructive:
    backgroundColor: "rgba(179, 38, 30, 0.1)"
    textColor: "{colors.destructive}"
    rounded: "{rounded.lg}"
    padding: "0 10px"
    height: "32px"
  input:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "4px 10px"
    height: "32px"
  thumb-tab:
    backgroundColor: "{colors.cover}"
    textColor: "{colors.cover-foreground}"
    typography: "{typography.running-head}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  thumb-tab-active:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.gold-foreground}"
  priority-high:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.gold-foreground}"
    typography: "{typography.priority-mark}"
    rounded: "{rounded.none}"
    padding: "4px 6px"
  priority-medium:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.priority-mark}"
    rounded: "{rounded.none}"
    padding: "3px 6px"
  priority-low:
    backgroundColor: "transparent"
    textColor: "{colors.muted-foreground}"
    typography: "{typography.priority-mark}"
    rounded: "{rounded.none}"
    padding: "0"
  cover-band:
    backgroundColor: "{colors.cover}"
    textColor: "{colors.cover-foreground}"
    rounded: "{rounded.none}"
    padding: "24px 24px 20px"
  bookplate:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "6px"
  dialog:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xl}"
    padding: "16px"
---

# Design System: Networking Tracker

## Overview

**Creative North Star: "The Class Directory"**

I built this app as a private edition of the Berkeley class directory. The chrome, meaning the top band and the thumb index on the right edge, is flat Berkeley Blue with gold stamping, and everything that carries the actual entries is bright white uncoated stock with black type, hairline rules, and a hanging indent. The direction contract in `app/layout.tsx` calls the chrome cloth, but the finish review on 2026-09-08 confirmed that the build is a flat fill with no texture, and that is what this document records. There is exactly one accent, the gold, and it is spent on the stamped title, the active tab of the thumb index, the high priority register, the owner's inscription on the band, and the frame around the sign in bookplate.

The layout refuses the sidebar and data table CRM shell. The band, the running head, and the thumb index are fixed furniture that never move, and sort and filter only swap the listing between them. Entries read in directory grammar, with the name flush left in Libre Franklin semibold and the company, role, where met, notes, and priority hung one indent step to the right. Archivo Narrow condensed caps carry the running heads, the tabs, the field labels, and the priority marks, which is the same typographic contrast a printed directory uses between its heads and its listings. Corners are near square. The base radius is 0.2rem, so buttons and inputs land at about 3px and dialogs at about 4.5px, while the band, bookplate, and priority marks have no radius at all.

There is no dark theme, and that is a deliberate decision. The `.dark` token block was deleted on purpose during the build and a dark theme is a recorded anti-goal, along with a sidebar shell, social or sharing cues, a literal network graph, and cream paper.

Key characteristics:

- Flat Berkeley Blue chrome with gold stamping, confined to the band and the thumb index
- Bright white listing stock with black ink, hairline rules, and no cream
- One hanging indent axis for the running head and every entry on both breakpoints
- Priority as a typographic register, with no colored badge set
- Fixed furniture with a swapping listing, so nothing above or beside the entries moves on sort or filter

## Colors

The palette is two chrome colors, Berkeley Blue and California Gold, on top of a black on white listing with one cool grey family for rules and secondary text.

### Primary

Berkeley Blue (`cover`) is the flat fill of the band, the sign in cover, the resting thumb index tabs, the solid Add contact button, the sign in button, the focus ring, the caret, the scrollbar thumb, and the form accent color. It never appears as a text color on the white stock except as the link color and the primary button fill.

California Gold (`gold`) is the stamping. It carries the title on the band and on the cover, the owner's email in the inscription, the active thumb index tab, the high priority mark, the border of the sign in bookplate, the sign out button on the band, and the text selection highlight. It is always paired with `gold-foreground`, which is the same Berkeley Blue, so gold never carries white or black text.

### Neutral

Paper (`paper`) is the listing stock, the bookplate, the dialogs, and the outline button fill. It is pure white and never warmed toward cream. Ink (`ink`) is the entry text and the medium priority border. Rule (`rule`) is the hairline under every entry and under the running head, and it doubles as the outline button border. Muted (`muted`) is the hover fill for outline and ghost buttons and the dialog footer wash at half opacity. Muted foreground (`muted-foreground`) is where met, notes, the added date, field labels, descriptions, and the low priority mark. Input (`input`) is the border on every text field and native select at rest. Secondary (`secondary`) is defined for the shadcn secondary button variant, which no surface uses yet. Destructive (`destructive`) is the color of inline validation errors, load errors, and the tinted Delete action in the confirm dialog.

### Named rules

**The Chrome Only Rule.** Berkeley Blue fills the band, the sign in cover, the thumb index, and the solid primary button, and nothing else. The listing stock stays white and the blue never becomes a page background or a card fill inside the listing.

**The Stamping Rule.** Gold is stamping on the chrome and the high register on the stock. On the white stock it appears only as the high priority mark and the bookplate frame, and it always carries Berkeley Blue text, never white or black.

**The Priority Register Rule.** Every priority state has its own typographic register. High is stamped gold with blue caps, medium is ruled with a one pixel ink border and no fill, and low is set quiet in muted grey caps with no border. This was raised as binding on 2026-09-08 because the laptop scan is where priority earns its place, and three colored chips at equal weight would read as a status legend and lose the ranking.

**The White Stock Rule.** The listing background is pure white. Cream paper was rejected as an anti-goal because the world is a modern uncoated directory, and warming the stock would push it toward a heritage pastiche and cost contrast on the grey text.

## Typography

Display and label font is Archivo Narrow (with Arial Narrow and sans-serif fallback), loaded through `next/font/google` as `--font-archivo` and exposed as both `font-heading` and `font-condensed`. Body font is Libre Franklin (with Franklin Gothic and sans-serif fallback), loaded as `--font-franklin` and mapped to `font-sans`. There is a mono stack defined for the shadcn primitives, but no surface uses it.

Character. The pairing is a directory's own contrast. Franklin sets the listing in a plain, wide American gothic, and the condensed caps in Archivo Narrow with wide tracking read as stamped heads and tab labels. Every use of Archivo Narrow is uppercase with letter spacing between 0.08em and 0.14em, and it is never used for running text.

### Hierarchy

Display is Archivo Narrow bold at 30px on the band, rising to 36px from the small breakpoint up, with line height 1 and 0.12em tracking, set in gold. The sign in cover uses the same face at 36px with 0.08em tracking and balanced wrapping.

Headline is Archivo Narrow bold at 20px with 0.1em tracking, used for the dialog title and the bookplate title (Sign in, Create your account, Add contact, Edit contact).

Title is Archivo Narrow bold at 18px with 0.12em tracking, used for the empty state heading and the delete confirmation title.

Running head is Archivo Narrow semibold at 14px with 0.12em tracking and tabular numerals, used for the live count line and the vertical thumb index tabs. The horizontal tabs on phones drop to 12px.

Entry name is Libre Franklin semibold at 16px with snug line height, flush left on the indent axis.

Body is Libre Franklin regular at 14px, used for every hung line of an entry, the descriptions, the controls, and the buttons. Inputs render at 16px below the medium breakpoint so iOS does not zoom, then 14px above it.

Label is Archivo Narrow semibold at 12px with 0.12em tracking in muted grey, used for every field label and the "This copy belongs to" inscription on the band.

Priority mark is Archivo Narrow at 11px with 0.14em tracking and line height 1, at bold weight for high, semibold for medium, and medium for low.

Caption is Libre Franklin at 12px with tabular numerals in muted grey, used only for the added date.

### Named rules

**The Condensed Caps Rule.** Archivo Narrow appears only as uppercase with tracking of 0.08em or wider, and only in heads, tabs, labels, counts, and priority marks. Running text, entry names, and control text stay in Libre Franklin at normal tracking.

**The Hanging Indent Rule.** One indent axis of 16px rules the whole listing and the running head on both breakpoints. The count line and every entry name sit on the container edge, and every line below a name is hung 16px to the right. This was raised as binding on 2026-09-08 because the indent is what makes a list of five fields read as a directory entry instead of a stacked card, and it has to hold on the phone or the mobile view collapses back into cards.

## Layout

The page is a single column with a maximum width of 1152px, padded 16px on phones and 24px from the small breakpoint up. The band spans the full viewport width in Berkeley Blue and holds the title on the left and the inscription with the sign out button on the right, aligned to the baseline, wrapping under the title on narrow screens. Under the band, inside the container, the running head is one row with the live count on the left and the search field, the sort select, the direction toggle, and the one solid Add contact button on the right, closed by a hairline rule. On phones the count keeps its own row and the controls wrap beneath it, with the search field taking the full width and the sort select stretching beside the toggle and the button.

From the medium breakpoint (768px) the listing sets in two CSS columns with a 48px gutter, entries kept whole with break inside avoid, and the container reserves 144px of right padding so the fore edge stays clear. The thumb index sits in an absolute full height column 112px wide on that right edge, sticky at 24px from the top, so it follows the scroll without leaving the edge. Below the medium breakpoint the thumb index becomes a horizontal row of four equal tabs directly under the running head and the listing runs in one column.

Vertical rhythm is 12px of padding above and below each entry, a hairline rule between entries, 16px of padding in the running head, 24px above and 20px below the band content, and 48px of bottom padding under the listing. Forms use a 16px grid gap between fields and 6px between a label and its field, with company and role sharing a two column row from the small breakpoint up. The empty state centers in 80px of vertical padding and the filtered to nothing state in 64px.

**The Fixed Furniture Rule.** The band, the running head, and the thumb index never move. Sort and filter swap only the listing between them, and the thumb index column keeps its width even when the list is empty. This was raised as binding on 2026-09-08 because a filter that shifts the chrome would feel like a page change, when it should feel like turning to a tab of the same book.

**The Live Count Rule.** The running head count changes visibly on every filter. The line reads the full count with the high count beside it at rest, switches to "N of total" when a filter or search is active, and re-enters with a 300ms fade each time the number changes, in a polite live region. This was raised as binding on 2026-09-08 because the count is the reader's proof that the filter did something when the listing looks similar before and after.

## Elevation & Depth

The system is flat. The chrome and the stock are separated by color and by hairline rules, not by shadows, and the listing has no shadow anywhere. Depth appears in exactly two places. The bookplate on the sign in cover carries one soft drop shadow so the white plate reads as pasted onto the blue cover, and the dialogs float on a one pixel ring of ink at 10% opacity over a backdrop that is black at 10% with a slight blur. The active thumb index tab does not lift with a shadow; it stands proud by translating 6px toward the listing on desktop and 2px downward on phones.

### Shadow vocabulary

Bookplate (`box-shadow: 0 16px 40px -16px rgba(0,0,0,0.6)`) is used once, on the sign in and sign up plate.

Dialog ring (`box-shadow: 0 0 0 1px rgb(20 20 20 / 0.1)`) is the only edge on the add, edit, and delete dialogs.

### Named rules

**The Flat Directory Rule.** Surfaces are flat at rest and stay flat. The only shadows in the system are the bookplate and the dialog ring, and no new surface introduces a hover lift, a card shadow, or a hard offset shadow.

## Shapes

Corners are near square. The base radius is 0.2rem, so the shadcn scale resolves to about 2.5px for medium, 3.2px for large, and 4.5px for extra large. Buttons, inputs, selects, and the textarea use the large step. The thumb index tabs round only the edge that faces away from the listing, meaning the left edge on desktop and the bottom edge on phones, so the tab reads as cut into the fore edge. Dialogs use the extra large step. The band, the bookplate and its gold frame, and the three priority marks have no radius at all. The contract asked for square corners and the build landed a hair off square; I record the build. Borders are one pixel everywhere, hairline rules in `rule`, field borders in `input`, the medium priority border in `ink`, and the bookplate frame in `gold`. The bookplate itself is a white plate with 6px of white margin around a gold ruled frame, which is the one decorative silhouette in the system.

## Components

### Buttons

Buttons are plain and quiet. The primary button is the only solid blue element on the stock, and there is one per surface.

Shape is near square (3.2px), height 32px, 10px of horizontal padding, 14px medium weight Franklin, with a 16px inline icon and a 6px gap. Primary is Berkeley Blue with white text, dropping to 80% opacity on hover, used for Add contact, Save changes, and the sign in submit, where it grows to 36px tall in condensed uppercase at 0.1em. Outline is white with a hairline `rule` border and ink text, washing to `muted` on hover, used for Cancel, Try again, and the sort direction toggle at 32px square. Ghost has no border or fill and washes to `muted` on hover, used for the 28px square edit and delete icon buttons on every entry and the dialog close. The band outline variant is the sign out button, 28px tall with a gold border at 70% opacity and gold text on the blue, filling solid gold with blue text on hover. Destructive is a 10% tint of the destructive red with red text, used only for the Delete action in the confirm dialog. Every button presses down one pixel on active, drops to 50% opacity when disabled, and shows a 3px focus ring of Berkeley Blue at 50% on keyboard focus.

### Priority marks

Priority is a typographic register. All three are Archivo Narrow uppercase at 11px with 0.14em tracking and line height 1, sitting on the hung line with the added date. High is solid gold with blue bold text and 4px by 6px padding. Medium is a one pixel ink border with no fill, semibold, and 3px by 6px padding. Low is muted grey medium weight text with no box.

### Directory entry

An entry is a plain list item with no card treatment. It has no background, no border except the hairline rule beneath it, and 12px of padding above and below. The name is 16px semibold on the indent axis with the edit and delete ghost icons pulled up and right so they hang off the name line. Company and role join on one hung line, where met is hung in italic muted grey, notes are hung in muted grey with preserved line breaks, and the last hung line holds the priority mark and the added date with a 12px gap and 6px of space above. Entries never break across columns.

### Inputs and fields

Fields are transparent with a one pixel `input` grey border, 32px tall, 10px of horizontal padding, near square corners, and muted placeholder text. On focus the border turns Berkeley Blue and a 3px ring of blue at 50% opacity appears. Invalid fields turn the border red with a red ring at 20%, and the error sentence sits beneath in 14px red with role alert. Native selects share the same styling and stay native because they work best on phones. The textarea is the same treatment with a 64px minimum height and content sizing. Labels are Archivo Narrow 12px caps in muted grey with 6px above the field.

### Running head

The running head is the white strip between the band and the listing. On the left the count line in 14px condensed caps with tabular numerals, on the right the search input at 256px wide, the native sort select, the outline direction toggle, and the solid Add contact button, all 32px tall with an 8px gap, closed by a hairline rule. While loading it reads "Loading entries" in muted grey.

### Thumb index

The thumb index is the signature component and the priority filter. It is a nav labeled "Filter by priority" with four tabs, All and the three priorities, each a button with the label on the left and its count on the right at 12px tabular and 80% opacity. Resting tabs are Berkeley Blue with white condensed caps at 14px semibold and 8px by 12px padding, rounding only their outer edge. The pressed tab turns gold with blue text and translates 6px toward the listing on desktop or 2px downward on phones, with a 200ms ease out transition on transform, background, and color. On desktop the tabs stack vertically in a 112px column on the right edge with a 6px gap and stick 24px from the top. On phones they sit in a single row under the running head at 12px caps and 6px by 8px padding, each taking equal width. Tabs carry aria pressed for the active state and the standard focus ring.

### Cover band and bookplate

The band is the flat Berkeley Blue header on every signed in page, holding the gold stamped title, a white subtitle at 85% opacity, the inscription "This copy belongs to" in 12px condensed caps with the owner's email in gold, and the sign out button. The sign in and sign up pages are the same blue as a full cover with the title and description centered above a bookplate. The bookplate is a 384px wide white plate with 6px of white margin, a one pixel gold frame, 24px by 20px of inner padding rising to 24px on the sides from the small breakpoint, the headline in condensed caps, a muted description, the form fields, a full width condensed sign in button, and a plain underlined blue link to the other form. It carries the single soft shadow in the system.

### Dialogs

Add contact, Edit contact, and the delete confirmation are white dialogs with 16px padding, 4.5px corners, a 10% ink ring, and a 10% black blurred backdrop, entering with a 100ms fade and zoom from 95%. The form dialog widens to 512px on desktop. Titles are condensed caps at 20px for the form dialog and 18px for the delete confirmation, descriptions are 14px muted grey, and the footer is a half opacity muted wash with the outline Cancel on the left of the primary or destructive action. Toasts from sonner appear at the top center and are left at their library styling.

### States

Loading shows four skeleton entries in the two column listing, each a 16px by 160px bar with a 12px by 224px bar hung beneath it, inside an aria busy region. The empty state centers the title "No contacts yet" in 18px condensed caps, a muted sentence, and a primary Add contact button, while the thumb index stays in place with zero counts. Filtered to nothing is one centered muted sentence. A load error is a red sentence with role alert and an outline Try again button under a hairline rule.

## Do's and Don'ts

### Do:

- Do keep Berkeley Blue on the band, the cover, the thumb index, and the primary button only, and keep the listing stock pure white.
- Do give every priority its own register, gold stamped for high, ink ruled for medium, and quiet grey for low, at 11px condensed caps with 0.14em tracking.
- Do hang every line of an entry 16px off the name and keep the running head count on the same axis on both breakpoints.
- Do set heads, tabs, labels, counts, and priority marks in Archivo Narrow uppercase with 0.08em to 0.14em tracking, and everything else in Libre Franklin.
- Do keep the band, the running head, and the thumb index fixed while sort and filter swap only the listing, and fade the count in over 300ms when it changes.
- Do use one pixel borders, hairline `rule` between entries, `input` grey on fields, and the base radius of 0.2rem for controls.
- Do keep native selects native and keep the ARIA labels, live region, and focus rings that ship on every control.

### Don't:

- Don't add a dark theme. The `.dark` token block was deleted on purpose and a dark theme is a recorded anti-goal, because the world is white stock inside a blue cover and inverting it would have no equivalent in the object.
- Don't build a sidebar shell or a data table for the listing. The thumb index is the only navigation and entries read in directory grammar, because the sidebar and table shell is the CRM template this world refuses.
- Don't add social or sharing cues, avatars, follower counts, or invitations. Privacy is the product truth and every copy belongs to one owner.
- Don't draw a literal network graph or node map. The metaphor is a bound book.
- Don't warm the stock toward cream or any off white. The listing is pure white.
- Don't put gold on white text or black text, and don't spend it outside the chrome, the high register, the bookplate frame, and text selection.
- Don't add shadows, hover lifts, or card surfaces to entries. The bookplate shadow and the dialog ring are the only depth in the system.
- Don't texture the chrome. The blue is a flat fill, and the contract's "cloth" describes the metaphor, and the build is a flat fill.
