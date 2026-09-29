# Obsidian screenshots

The assignment asks for three screenshots of the vault open in Obsidian. Take them after `scripts/offline_demo.sh` has generated the notes, save them here with these exact names, and the README links them.

1. `01-open-note.png`: open `vault/` as the vault (Open folder as vault, pick the `vault` folder, not the repository), open a note under `wiki/Projects/`, for example the Pac-Man training note, with the file explorer visible. The frame should show the short descriptive filename, the matching first heading, the Related links, and the Sources section with its link to the catalog note and the raw path.
2. `02-index-and-page-list.png`: open `index.md` with the file explorer expanded so `raw/`, `wiki/Projects/`, `wiki/Concepts/`, `wiki/Course/`, and `wiki/Sources/` are all visible. The index groups the notes by topic with one line each.
3. `03-graph-view.png`: open the graph view, set the filter to `path:wiki/`, turn Attachments off, and zoom in until the note labels are readable. Optionally add a group per folder (`path:wiki/Projects` and so on) to color them. Record the filter used in the README.

Before taking the screenshots, click through one chain: start at `index.md`, open a note, follow a Related link, then follow the Sources link to the catalog note and from there the link to the raw file. A link that shows as unresolved in Obsidian means the note or the raw file has a different name than the link expects; fix the note, not the raw file.

Redact anything private before committing. These files are ordinary PNGs; the wiki itself stays plain Markdown.
