# Notes CLI System

A command-line application for taking quick notes, organizing them with tags, and searching them later. Uses SQLite for local storage.

**Challenge repo:** [Day 002/100 of the #100Days Challenge](https://github.com/Holfkings)

---

## What it does

- Create notes with one or multiple tags
- List notes (with filter by days and limit)
- Search notes by text or by tag
- Delete notes
- List all tags

No server required, no configuration needed — uses a local SQLite database at `~/.notes_cli/notes.db`.

---

## Installation

No installation needed. Just Python 3.14+:

```bash
# Clone or download the files
git clone https://github.com/Holfkings/day-002-notes-cli.git
cd day-002-notes-cli

# The database is created automatically on first use
```

---

## Usage

The main command is `notes.py`. Run it with `python3 notes.py`.

### Add a note

```bash
python3 notes.py add "Buy milk at the supermarket" --tags home,shopping
python3 notes.py add "Meeting with Juan at 3pm" --tags work,urgent
```

### List notes

```bash
# All notes (maximum 50)
python3 notes.py list

# Only notes from the last 7 days
python3 notes.py list --days 7

# Limit results
python3 notes.py list --limit 10
```

### Search notes

```bash
# By text
python3 notes.py search "milk"

# By tag
python3 notes.py search --tag work

# Combined: text + tag
python3 notes.py search "Meeting" --tag work
```

### View a specific note

```bash
python3 notes.py show 5
```

### Delete a note

```bash
python3 notes.py delete 5
```

### View all tags

```bash
python3 notes.py tags
```

---

## Available commands

| Command | Description |
|---------|-------------|
| `add`   | Add a new note |
| `list`  | List existing notes |
| `search`| Search notes by text or tag |
| `show`  | Show a note by its ID |
| `delete`| Delete a note by its ID |
| `tags`  | List all tags |

---

## Technical stack

- **Python 3.14+** — stdlib only, no external dependencies
- **SQLite** — embedded database, comes with Python
- **argparse** — Python's built-in CLI

---

## Project structure

```
day-002-notes-cli/
├── notes.py           # Main CLI (argparse)
├── storage.py         # Data layer (SQLite)
├── tests/
│   └── test_notes.py  # Automated tests (pytest)
├── .gitignore
└── README.md
```

Modules:
- `storage.py` — everything related to the database:
  - `init_db()` — creates the tables
  - `add_note()` — creates a note
  - `list_notes()` — lists notes with filters
  - `search_notes()` — searches by text or tag
  - `delete_note()` — deletes a note
  - `get_note_by_id()` — gets an individual note

- `notes.py` — CLI with subcommands:
  - `add`, `list`, `search`, `show`, `delete`, `tags`

---

## Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run a specific test
python3 -m pytest tests/test_notes.py::TestSearchNotes::test_search_by_text -v
```

Tests use a temporary database to avoid affecting real data.

---

## Known limitations

- Text search uses `LIKE '%term%'` — it is case-insensitive but does not support fuzzy search or regular expressions.
- No editing of existing notes (only create/read/search/delete).
- No synchronization between devices — fully local.
- Tags are not deleted even if no notes use them.

---

## For Day 003 (possible continuation)

If this project continues, possible additions:
- Edit existing notes (`notes edit <id> "new content"`)
- Export to Markdown
- Import from text file
- Interactive mode (REPL)
- Filter by date range
- Sort by date, by tags, etc.
