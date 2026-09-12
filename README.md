# Sistema de Notas CLI

Aplicación de línea de comandos para tomar notas rápidas, organizarlas con
etiquetas y buscarlas después. Usa SQLite para almacenamiento local.

**Repo del reto:** [Día 002/100 del Reto #100Días](https://github.com/Holfkings)

---

## Qué hace

- Crear notas con uno o varios tags
- Listar notas (con filtro por días y límite)
- Buscar notas por texto o por etiqueta
- Borrar notas
- Listar todas las etiquetas

No requiere servidor, no requiere configuración — usa una base de datos
SQLite local en `~/.notes_cli/notes.db`.

---

## Instalación

No requiere instalación. Solo necesitas Python 3.14+:

```bash
# Clonar o descargar los archivos
git clone https://github.com/Holfkings/day-002-notes-cli.git
cd day-002-notes-cli

# La base de datos se crea automáticamente al primer uso
```

---

## Uso

El comando principal es `notes.py`. Ejecutalo con `python3 notes.py`.

### Agregar una nota

```bash
python3 notes.py add "Comprar leche en el súper" --tags casa,compras
python3 notes.py add "Reunión con Juan a las 3pm" --tags trabajo,urgente
```

### Listar notas

```bash
# Todas las notas (máximo 50)
python3 notes.py list

# Solo las de los últimos 7 días
python3 notes.py list --days 7

# Limitar resultados
python3 notes.py list --limit 10
```

### Buscar notas

```bash
# Por texto
python3 notes.py search "leche"

# Por etiqueta
python3 notes.py search --tag trabajo

# Combinado: texto + etiqueta
python3 notes.py search "Reunión" --tag trabajo
```

### Ver una nota específica

```bash
python3 notes.py show 5
```

### Borrar una nota

```bash
python3 notes.py delete 5
```

### Ver todas las etiquetas

```bash
python3 notes.py tags
```

---

## Comandos disponibles

| Comando | Descripción |
|---------|-------------|
| `add`   | Agregar una nueva nota |
| `list`  | Listar notas existentes |
| `search`| Buscar notas por texto o etiqueta |
| `show`  | Mostrar una nota por su ID |
| `delete`| Borrar una nota por su ID |
| `tags`  | Listar todas las etiquetas |

---

## Formato del archivo .deploy

El sistema usa una base de datos SQLite local. No hay archivos de
configuración por fuera del código.

---

## Stack técnico

- **Python 3.14+** — stdlib only, sin dependencias externas
- **SQLite** — base de datos embebida, viene con Python
- **argparse** — CLI built-in de Python

---

## Estructura del proyecto

```
day-002-notes-cli/
├── notes.py           # CLI principal (argparse)
├── storage.py         # Capa de datos (SQLite)
├── tests/
│   └── test_notes.py  # Tests automatizados (pytest)
├── .gitignore
└── README.md
```

Módulos:
- `storage.py` — todo lo relacionado con la base de datos:
  - `init_db()` — crea las tablas
  - `add_note()` — crea una nota
  - `list_notes()` — lista notas con filtros
  - `search_notes()` — busca por texto o etiqueta
  - `delete_note()` — borra una nota
  - `get_note_by_id()` — obtiene una nota individual

- `notes.py` — CLI con subcomandos:
  - `add`, `list`, `search`, `show`, `delete`, `tags`

---

## Tests

```bash
# Ejecutar todos los tests
python3 -m pytest tests/ -v

# Ejecutar un test específico
python3 -m pytest tests/test_notes.py::TestSearchNotes::test_buscar_por_texto -v
```

Los tests usan una base de datos temporal para no afectar los datos reales.

---

## Limitaciones conocidas

- La búsqueda por texto usa `LIKE '%termino%'` — es case-insensitive pero
  no soporta búsqueda fuzzy o por expresiones regulares.
- No hay edición de notas existentes (solo create/read/search/delete).
- No hay sincronización entre dispositivos — es totalmente local.
- Los tags no se eliminan aunque ninguna nota los use.

---

## Para el Día 003 (posible continuación)

Si se continúa este proyecto, se podrían agregar:
- Editar notas existentes (`notes edit <id> "nuevo contenido"`)
- Exportar a Markdown
- Importar desde archivo de texto
- Modo interactivo (REPL)
- Filtro por rango de fechas
- Ordenamiento por fecha, por tags, etc.
