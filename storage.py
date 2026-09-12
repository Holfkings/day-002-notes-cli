"""
storage.py — Gestión de la base de datos SQLite para el sistema de notas.

Tablas:
    notes     — notas (id, content, created_at, updated_at)
    tags      — etiquetas (id, name)
    note_tags — relación muchos-a-muchos entre notas y etiquetas
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import Optional


DB_PATH = os.path.join(os.path.expanduser("~"), ".notes_cli", "notes.db")


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos. Crea el directorio y la DB si no existen."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn


def init_db() -> None:
    """Crea las tablas si no existen."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );
        """)
        conn.commit()
    finally:
        conn.close()


def add_note(content: str, tags: list[str] | None = None) -> int:
    """
    Crea una nueva nota.

    Args:
        content: texto de la nota
        tags: lista opcional de nombres de etiquetas

    Returns:
        El ID de la nota creada
    """
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO notes (content, created_at, updated_at) VALUES (?, ?, ?)",
            (content, now, now)
        )
        note_id = cursor.lastrowid

        if tags:
            for tag_name in tags:
                tag_id = get_or_create_tag(conn, tag_name.strip())
                conn.execute(
                    "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
                    (note_id, tag_id)
                )

        conn.commit()
        return note_id
    finally:
        conn.close()


def get_or_create_tag(conn: sqlite3.Connection, name: str) -> int:
    """
    Obtiene el ID de una etiqueta o la crea si no existe.

    Args:
        conn: conexión abierta a la DB
        name: nombre de la etiqueta

    Returns:
        El ID de la etiqueta
    """
    cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row["id"]
    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    conn.commit()
    return cursor.lastrowid


def list_notes(days: int | None = None, limit: int = 50) -> list[dict]:
    """
    Lista notas, opcionalmente filtradas por antigüedad.

    Args:
        days: si se proporciona, solo notas creadas en los últimos N días
        limit: máximo de notas a retornar

    Returns:
        Lista de dicts con id, content, created_at, updated_at, tags
    """
    conn = get_connection()
    try:
        query = """
            SELECT n.id, n.content, n.created_at, n.updated_at,
                   GROUP_CONCAT(t.name, ',') AS tags
            FROM notes n
            LEFT JOIN note_tags nt ON n.id = nt.note_id
            LEFT JOIN tags t ON nt.tag_id = t.id
        """
        params: list[str] = []

        if days is not None:
            cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
            query += " WHERE datetime(n.created_at) >= datetime(?, 'unixepoch')"
            params.append(str(int(cutoff)))

        query += " GROUP BY n.id ORDER BY n.created_at DESC LIMIT ?"
        params.append(str(limit))

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "tags": row["tags"].split(",") if row["tags"] else [],
            })
        return result
    finally:
        conn.close()


def search_notes(query_text: str = "", tag: str | None = None) -> list[dict]:
    """
    Busca notas por texto o por etiqueta.

    Args:
        query_text: texto a buscar en el contenido de las notas (vacío = sin filtro de texto)
        tag: si se proporciona, solo notas con esta etiqueta

    Returns:
        Lista de dicts con id, content, created_at, updated_at, tags
    """
    conn = get_connection()
    try:
        if tag and not query_text:
            # Búsqueda por etiqueta solamente
            search_sql = """
                SELECT n.id, n.content, n.created_at, n.updated_at,
                       GROUP_CONCAT(t2.name, ',') AS tags
                FROM notes n
                LEFT JOIN note_tags nt ON n.id = nt.note_id
                LEFT JOIN tags t2 ON nt.tag_id = t2.id
                WHERE n.id IN (
                    SELECT nt2.note_id
                    FROM note_tags nt2
                    JOIN tags t3 ON nt2.tag_id = t3.id
                    WHERE t3.name = ?
                )
                GROUP BY n.id
                ORDER BY n.created_at DESC
            """
            cursor = conn.execute(search_sql, (tag,))
        elif tag and query_text:
            # Búsqueda combinada: texto + etiqueta
            search_sql = """
                SELECT n.id, n.content, n.created_at, n.updated_at,
                       GROUP_CONCAT(t2.name, ',') AS tags
                FROM notes n
                LEFT JOIN note_tags nt ON n.id = nt.note_id
                LEFT JOIN tags t2 ON nt.tag_id = t2.id
                WHERE n.content LIKE ?
                  AND n.id IN (
                      SELECT nt2.note_id
                      FROM note_tags nt2
                      JOIN tags t3 ON nt2.tag_id = t3.id
                      WHERE t3.name = ?
                  )
                GROUP BY n.id
                ORDER BY n.created_at DESC
            """
            cursor = conn.execute(search_sql, (f"%{query_text}%", tag))
        elif query_text:
            # Búsqueda por texto (LIKE %query%)
            search_sql = """
                SELECT n.id, n.content, n.created_at, n.updated_at,
                       GROUP_CONCAT(t.name, ',') AS tags
                FROM notes n
                LEFT JOIN note_tags nt ON n.id = nt.note_id
                LEFT JOIN tags t ON nt.tag_id = t.id
                WHERE n.content LIKE ?
                GROUP BY n.id
                ORDER BY n.created_at DESC
            """
            cursor = conn.execute(search_sql, (f"%{query_text}%",))
        else:
            # Sin filtro — retorna todas
            search_sql = """
                SELECT n.id, n.content, n.created_at, n.updated_at,
                       GROUP_CONCAT(t.name, ',') AS tags
                FROM notes n
                LEFT JOIN note_tags nt ON n.id = nt.note_id
                LEFT JOIN tags t ON nt.tag_id = t.id
                GROUP BY n.id
                ORDER BY n.created_at DESC
            """
            cursor = conn.execute(search_sql)

        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "tags": row["tags"].split(",") if row["tags"] else [],
            }
            for row in rows
        ]
    finally:
        conn.close()


def delete_note(note_id: int) -> bool:
    """
    Borra una nota por su ID.

    Args:
        note_id: ID de la nota a borrar

    Returns:
        True si se borró, False si no existe
    """
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            return False
        # Borrar primero las relaciones many-to-many (ON DELETE CASCADE no está habilitado en SQLite por defecto)
        conn.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def get_note_by_id(note_id: int) -> Optional[dict]:
    """
    Obtiene una nota por su ID.

    Args:
        note_id: ID de la nota

    Returns:
        Dict con la nota o None si no existe
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT n.id, n.content, n.created_at, n.updated_at,
                   GROUP_CONCAT(t.name, ',') AS tags
            FROM notes n
            LEFT JOIN note_tags nt ON n.id = nt.note_id
            LEFT JOIN tags t ON nt.tag_id = t.id
            WHERE n.id = ?
            GROUP BY n.id
            """,
            (note_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "content": row["content"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "tags": row["tags"].split(",") if row["tags"] else [],
        }
    finally:
        conn.close()


def format_note(note: dict) -> str:
    """
    Formatea una nota para mostrar por pantalla.

    Args:
        note: dict con la nota

    Returns:
        String formateado
    """
    tags_str = f" [{', '.join(note['tags'])}]" if note["tags"] else ""
    return f"[{note['id']}] {note['content']}{tags_str}\n    creada: {note['created_at']}"


if __name__ == "__main__":
    # Prueba rápida al ejecutar directamente
    init_db()
    print(f"Base de datos inicializada en: {DB_PATH}")
    note_id = add_note("Nota de prueba desde storage.py", ["prueba", "test"])
    print(f"Nota creada con ID: {note_id}")
    notes = list_notes(limit=5)
    print(f"\nNotas en la base de datos ({len(notes)}):")
    for n in notes:
        print(format_note(n))
