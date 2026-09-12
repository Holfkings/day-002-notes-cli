#!/usr/bin/env python3
"""
notes.py — CLI para sistema de notas con etiquetas y búsqueda.

Uso:
    notes add "Contenido de la nota" --tags vida,trabajo
    notes list [--days 7] [--limit 50]
    notes search "texto a buscar" [--tag vida]
    notes show <id>
    notes delete <id>
    notes tags
"""

import argparse
import sys
from storage import (
    init_db,
    add_note,
    list_notes,
    search_notes,
    delete_note,
    get_note_by_id,
    format_note,
)


def cmd_add(args: argparse.Namespace) -> int:
    """Comando: agregar una nota."""
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    note_id = add_note(args.content, tags)
    print(f"Nota creada con ID {note_id}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """Comando: listar notas."""
    notes = list_notes(days=args.days, limit=args.limit)

    if not notes:
        print("No hay notas.")
        return 0

    print(f"Notas ({len(notes)}):\n")
    for note in notes:
        print(format_note(note))
        print()
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Comando: buscar notas."""
    notes = search_notes(
        query_text=args.query,
        tag=args.tag,
    )

    if not notes:
        print("No se encontraron notas.")
        return 0

    print(f"Resultados: {len(notes)}\n")
    for note in notes:
        print(format_note(note))
        print()
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Comando: mostrar una nota por ID."""
    note = get_note_by_id(args.id)

    if not note:
        print(f"No existe nota con ID {args.id}")
        return 1

    print(format_note(note))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """Comando: borrar una nota por ID."""
    if delete_note(args.id):
        print(f"Nota {args.id} borrada.")
        return 0
    else:
        print(f"No existe nota con ID {args.id}")
        return 1


def cmd_tags(args: argparse.Namespace) -> int:
    """Comando: listar todas las etiquetas."""
    from storage import get_connection

    conn = get_connection()
    try:
        cursor = conn.execute("SELECT name FROM tags ORDER BY name")
        rows = cursor.fetchall()
        if not rows:
            print("No hay etiquetas.")
            return 0
        print("Etiquetas:\n")
        for row in rows:
            print(f"  {row['name']}")
    finally:
        conn.close()
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sistema de notas con etiquetas y búsqueda",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  notes add "Comprar café" --tags casa,vida
  notes list --days 7
  notes search "café" --tag vida
  notes show 5
  notes delete 5
  notes tags
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # notes add
    parser_add = subparsers.add_parser("add", help="Agregar una nota")
    parser_add.add_argument("content", help="Contenido de la nota")
    parser_add.add_argument("--tags", "-t", help="Etiquetas separadas por coma")
    parser_add.set_defaults(func=cmd_add)

    # notes list
    parser_list = subparsers.add_parser("list", help="Listar notas")
    parser_list.add_argument("--days", type=int, default=None, help="Solo notas de los últimos N días")
    parser_list.add_argument("--limit", "-l", type=int, default=50, help="Máximo de notas a mostrar")
    parser_list.set_defaults(func=cmd_list)

    # notes search
    parser_search = subparsers.add_parser("search", help="Buscar notas")
    parser_search.add_argument("query", nargs="?", default="", help="Texto a buscar")
    parser_search.add_argument("--tag", "-tg", help="Filtrar por etiqueta")
    parser_search.set_defaults(func=cmd_search)

    # notes show
    parser_show = subparsers.add_parser("show", help="Mostrar una nota por ID")
    parser_show.add_argument("id", type=int, help="ID de la nota")
    parser_show.set_defaults(func=cmd_show)

    # notes delete
    parser_delete = subparsers.add_parser("delete", help="Borrar una nota")
    parser_delete.add_argument("id", type=int, help="ID de la nota a borrar")
    parser_delete.set_defaults(func=cmd_delete)

    # notes tags
    parser_tags = subparsers.add_parser("tags", help="Listar todas las etiquetas")
    parser_tags.set_defaults(func=cmd_tags)

    args = parser.parse_args()

    # Inicializar DB siempre
    init_db()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
