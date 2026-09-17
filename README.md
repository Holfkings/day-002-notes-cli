<div align="center">

# 📋 Notes CLI System

### Command-line notes · Tags · Search · SQLite · Python stdlib

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=database&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/CLI-Terminal-grey?style=for-the-badge&logo=gnubash&logoColor=white" alt="CLI">
  <img src="https://img.shields.io/badge/Zero_Dependencies-✓-green?style=for-the-badge&logo=package&logoColor=white" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Tests-24-9b59b6?style=for-the-badge&logo=pytest&logoColor=white" alt="24 Tests">
</p>

</div>

---

## ✨ What It Does

A command-line note-taking application with tag organization and full-text search. Uses SQLite for fast, local storage.

| Command | What it does |
|---------|-------------|
| `add` | Create a note with one or multiple tags |
| `list` | List notes (filter by days, limit results) |
| `search` | Search by text or by tag (combined possible) |
| `show` | View a specific note by ID |
| `delete` | Remove a note by ID |
| `tags` | List all tags |

**No server. No config. Just `python3 notes.py`.**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.14+ |
| **Database** | SQLite (embedded, comes with Python) |
| **CLI** | `argparse` (stdlib) |
| **Dependencies** | **Zero** — stdlib only |
| **Tests** | pytest — 24 automated tests |

---

## 📦 Project Structure

```text
day-002-notes-cli/
├── notes.py           # Main CLI — argparse subcommands
├── storage.py         # Data layer — all SQLite operations
├── tests/
│   └── test_notes.py  # Automated tests (24 tests)
├── .gitignore
└── README.md
```

### Module Breakdown

**`storage.py`** — database layer:
- `init_db()` — creates tables
- `add_note()` — inserts a note
- `list_notes()` — lists with filters (days, limit)
- `search_notes()` — text or tag search
- `delete_note()` — removes by ID
- `get_note_by_id()` — fetches single note

**`notes.py`** — CLI interface:
- Subcommands: `add`, `list`, `search`, `show`, `delete`, `tags`

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Holfkings/day-002-notes-cli.git
cd day-002-notes-cli

# The database is created automatically on first use
# No installation needed
```

---

## 📖 Usage

### Add notes

```bash
python3 notes.py add "Buy milk at the supermarket" --tags home,shopping
python3 notes.py add "Meeting with Juan at 3pm" --tags work,urgent
```

### List notes

```bash
python3 notes.py list              # All notes (max 50)
python3 notes.py list --days 7     # Last 7 days only
python3 notes.py list --limit 10   # Limit to 10 results
```

### Search

```bash
python3 notes.py search "milk"                          # By text
python3 notes.py search --tag work                      # By tag
python3 notes.py search "Meeting" --tag work            # Combined
```

### Manage

```bash
python3 notes.py show 5      # View note #5
python3 notes.py delete 5    # Delete note #5
python3 notes.py tags        # List all tags
```

---

## 🧪 Tests

```bash
# Run all tests (24 tests)
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_notes.py::TestSearchNotes::test_search_by_text -v
```

Tests use a temporary database — your real data stays safe.

---

## 📊 Test Coverage

| Area | Tests |
|------|-------|
| Note creation | ✓ |
| Listing with filters | ✓ |
| Text search | ✓ |
| Tag search | ✓ |
| Combined search | ✓ |
| Note deletion | ✓ |
| Tag listing | ✓ |
| Edge cases | ✓ |

---

## ⚙️ Technical Details

| Aspect | Detail |
|--------|--------|
| **DB location** | `~/.notes_cli/notes.db` |
| **DB creation** | Automatic on first use |
| **Text search** | `LIKE '%term%'` (case-insensitive) |
| **Sync** | Local only — no cloud |
| **Tag cleanup** | Tags persist even if no notes use them |

---

## 🔜 Known Limitations & Future Work

| Current | Future |
|---------|--------|
| No edit existing notes | `notes edit <id> "new content"` |
| No fuzzy/Regex search | Advanced search options |
| No device sync | Cloud sync option |
| No date range filter | Date range queries |
| No sorting options | Sort by date, tags, etc. |
| Tags never deleted | Auto-cleanup unused tags |

---

## 🎯 Why This Project

Part of the **#100Days Challenge** — building a real project every day for 100 days.

This project demonstrates:
- ✅ Solid Python — CLI with argparse, SQLite operations
- ✅ Clean architecture — separation of CLI and data layer
- ✅ Testing culture — 24 automated tests
- ✅ Zero dependencies — stdlib only, easy to run anywhere

---

<div align="center">

**Day 002/100** of the [#100Days Challenge](https://github.com/Holfkings)

<p align="center" style="color: #888; font-size: 0.85em; margin-top: 24px;">
  Built by [@Holfkings](https://github.com/Holfkings) · Python + SQLite · Clean code
</p>

</div>
