"""
test_notes.py — Tests automatizados para el sistema de notas.

Coordinación con storage.py — cada test usa una base de datos temporal
para no afectar los datos reales del usuario.
"""

import os
import sqlite3
import tempfile
from datetime import datetime, timezone

import pytest

from storage import (
    DB_PATH,
    get_connection,
    init_db,
    add_note,
    list_notes,
    search_notes,
    delete_note,
    get_note_by_id,
    format_note,
    get_or_create_tag,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def use_temp_db(monkeypatch, tmp_path):
    """
    Cada test usa una base de datos temporal en tmp_path.
    Así los tests son aislados y no contaminan la DB real del usuario.
    """
    test_db_dir = tmp_path / "test_notes_cli"
    test_db_dir.mkdir()
    test_db_path = test_db_dir / "notes.db"

    # Reemplazar DB_PATH global para que storage.py use nuestra DB temporal
    monkeypatch.setattr("storage.DB_PATH", str(test_db_path))

    # Inicializar tablas
    init_db()

    yield test_db_path

    # Limpieza automática: tmp_path se borra al final del test


# =============================================================================
# Tests de inicialización
# =============================================================================

class TestInitDB:
    """Tests para la inicialización de la base de datos."""

    def test_tablas_creadas(self, use_temp_db):
        """Verifica que las tres tablas existen después de init_db."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row["name"] for row in cursor.fetchall()]
            assert "notes" in tables
            assert "tags" in tables
            assert "note_tags" in tables
        finally:
            conn.close()

    def test_db_archivo_creado(self, use_temp_db):
        """Verifica que el archivo de base de datos existe en disco."""
        assert os.path.exists(str(use_temp_db))


# =============================================================================
# Tests de CRUD de notas
# =============================================================================

class TestAddNote:
    """Tests para agregar notas."""

    def test_agregar_nota_simple(self, use_temp_db):
        """Nota sin etiquetas se guarda correctamente."""
        note_id = add_note("Nota de prueba")
        assert note_id > 0

        note = get_note_by_id(note_id)
        assert note is not None
        assert note["content"] == "Nota de prueba"
        assert note["tags"] == []

    def test_agregar_nota_con_etiquetas(self, use_temp_db):
        """Nota con etiquetas se guarda y las etiquetas se asignan."""
        note_id = add_note("Nota con tags", ["vida", "trabajo"])
        assert note_id > 0

        note = get_note_by_id(note_id)
        assert note is not None
        assert set(note["tags"]) == {"vida", "trabajo"}

    def test_agregar_múltiples_notas(self, use_temp_db):
        """Se pueden agregar varias notas y se 번호ean correctamente."""
        ids = []
        for i in range(5):
            ids.append(add_note(f"Nota número {i}"))

        # Los IDs deben ser secuenciales y mayores a 0
        assert ids == list(range(1, 6))

        all_notes = list_notes(limit=10)
        assert len(all_notes) == 5

    def test_etiquetas_únicas(self, use_temp_db):
        """Tags con el mismo nombre se reutilizan, no se duplican."""
        id1 = add_note("Nota 1", ["compartida"])
        id2 = add_note("Nota 2", ["compartida"])

        # Buscar la etiqueta en la DB
        conn = get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) as cnt FROM tags WHERE name = 'compartida'")
            count = cursor.fetchone()["cnt"]
            assert count == 1, "La etiqueta 'compartida' debería existir una sola vez"
        finally:
            conn.close()


# =============================================================================
# Tests de listado
# =============================================================================

class TestListNotes:
    """Tests para listar notas."""

    def test_listar_notas_vacío(self, use_temp_db):
        """Lista retorna lista vacía cuando no hay notas."""
        notes = list_notes()
        assert notes == []

    def test_listar_todas_las_notas(self, use_temp_db):
        """Lista todas las notas creadas."""
        add_note("Nota A")
        add_note("Nota B")
        add_note("Nota C")

        notes = list_notes(limit=10)
        assert len(notes) == 3
        # Deben venir en orden descendente por created_at
        assert notes[0]["content"] == "Nota C"
        assert notes[-1]["content"] == "Nota A"

    def test_límite_de_resultados(self, use_temp_db):
        """El límite funciona correctamente."""
        for i in range(10):
            add_note(f"Nota {i}")

        limited = list_notes(limit=3)
        assert len(limited) == 3

    def test_filtrar_por_días(self, use_temp_db):
        """Filtrar por días retorna solo notas recientes."""
        from storage import get_connection

        # Agregar una nota ahora
        add_note("Nota reciente")

        # Modificar manualmente una nota para que sea vieja (hack para pruebas)
        conn = get_connection()
        try:
            old_time = "2020-01-01T00:00:00+00:00"
            conn.execute(
                "UPDATE notes SET created_at = ?, updated_at = ? WHERE content = 'Nota reciente'",
                (old_time, old_time)
            )
            conn.commit()
        finally:
            conn.close()

        # Lista sin filtro: ve la nota vieja
        all_notes = list_notes(limit=10)
        assert len(all_notes) == 1

        # Lista con días=1: no debería ver la nota vieja
        recent_notes = list_notes(days=1, limit=10)
        assert len(recent_notes) == 0


# =============================================================================
# Tests de búsqueda
# =============================================================================

class TestSearchNotes:
    """Tests para buscar notas."""

    def setup_method(self, use_temp_db):
        """Crear notas de prueba antes de cada test de búsqueda."""
        add_note("Comprar leche en el supermercado", ["casa", "compras"])
        add_note("Reunión de trabajo con el equipo", ["trabajo"])
        add_note("Leer libro de Python", ["lectura", "programacion"])
        add_note("Comprar pan en la panadería", ["casa", "comida"])

    def test_buscar_por_texto(self, use_temp_db):
        """Búsqueda por texto encuentra notas que contienen el término."""
        results = search_notes(query_text="leche")
        assert len(results) == 1
        assert results[0]["content"] == "Comprar leche en el supermercado"

    def test_buscar_por_texto_case_insensitive(self, use_temp_db):
        """La búsqueda no distingue mayúsculas/minúsculas (LIKE de SQLite)."""
        results = search_notes(query_text="PYTHON")
        assert len(results) == 1
        assert "Python" in results[0]["content"]

    def test_buscar_por_etiqueta(self, use_temp_db):
        """Búsqueda por etiqueta encuentra notas con esa etiqueta."""
        results = search_notes(tag="casa")
        assert len(results) == 2
        contents = {r["content"] for r in results}
        assert "Comprar leche en el supermercado" in contents
        assert "Comprar pan en la panadería" in contents

    def test_buscar_por_etiqueta_que_no_existe(self, use_temp_db):
        """Búsqueda por etiqueta inexistente retorna lista vacía."""
        results = search_notes(tag="etiqueta_inexistente")
        assert results == []

    def test_búsqueda_sin_resultados(self, use_temp_db):
        """Búsqueda por texto que no coincide retorna lista vacía."""
        results = search_notes(query_text="xyzzy_ninguna nota tiene_esto")
        assert results == []

    def test_búsqueda_combinada_texto_y_etiqueta(self, use_temp_db):
        """Búsqueda con texto y etiqueta simultáneos."""
        results = search_notes(query_text="Comprar", tag="casa")
        assert len(results) == 2

        results = search_notes(query_text="pan", tag="casa")
        assert len(results) == 1
        assert results[0]["content"] == "Comprar pan en la panadería"

    def test_búsqueda_combinada_sin_coincidencia(self, use_temp_db):
        """Búsqueda combinada que no coincide retorna vacío."""
        results = search_notes(query_text="Python", tag="casa")
        assert results == []


# =============================================================================
# Tests de borrado
# =============================================================================

class TestDeleteNote:
    """Tests para borrar notas."""

    def test_borrar_nota_existente(self, use_temp_db):
        """Borrar una nota existente retorna True y la nota desaparece."""
        note_id = add_note("Nota a borrar")
        assert delete_note(note_id) is True

        assert get_note_by_id(note_id) is None
        assert list_notes(limit=10) == []

    def test_borrar_nota_inexistente(self, use_temp_db):
        """Borrar una nota que no existe retorna False."""
        result = delete_note(9999)
        assert result is False

    def test_borrar_nota_elimina_las_relaciones_de_etiquetas(self, use_temp_db):
        """Al borrar una nota, sus relaciones en note_tags también se borran."""
        note_id = add_note("Nota con tags", ["tag1", "tag2"])
        assert delete_note(note_id) is True

        # Verificar que no queden relaciones huérfanas
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT COUNT(*) as cnt FROM note_tags WHERE note_id = ?",
                (note_id,)
            )
            count = cursor.fetchone()["cnt"]
            assert count == 0
        finally:
            conn.close()


# =============================================================================
# Tests de formato
# =============================================================================

class TestFormatNote:
    """Tests para el formateo de notas."""

    def test_formatear_nota_con_etiquetas(self, use_temp_db):
        """El formato incluye las etiquetas entre corchetes."""
        note = {
            "id": 5,
            "content": "Contenido de prueba",
            "created_at": "2026-01-15T10:00:00+00:00",
            "updated_at": "2026-01-15T10:00:00+00:00",
            "tags": ["vida", "trabajo"],
        }
        formatted = format_note(note)
        assert "[5] Contenido de prueba [vida, trabajo]" in formatted
        assert "creada: 2026-01-15T10:00:00+00:00" in formatted

    def test_formatear_nota_sin_etiquetas(self, use_temp_db):
        """El formato no incluye corchetes vacíos cuando no hay tags."""
        note = {
            "id": 3,
            "content": "Nota sin tags",
            "created_at": "2026-01-15T10:00:00+00:00",
            "updated_at": "2026-01-15T10:00:00+00:00",
            "tags": [],
        }
        formatted = format_note(note)
        assert "[3] Nota sin tags" in formatted
        assert "[" not in formatted.split("\n")[0] or "[]" not in formatted.split("\n")[0]


# =============================================================================
# Tests de integración
# =============================================================================

class TestIntegration:
    """Tests de integración que verifican el flujo completo."""

    def test_flujo_completo_agregar_buscar_borrar(self, use_temp_db):
        """Flujo completo: agregar → listar → buscar → borrar."""
        # Agregar
        note_id = add_note("Nota importante de la reunión", ["trabajo", "urgente"])

        # Listar
        notes = list_notes(limit=10)
        assert len(notes) == 1
        assert notes[0]["id"] == note_id

        # Buscar por texto
        results = search_notes(query_text="reunión")
        assert len(results) == 1
        assert results[0]["id"] == note_id

        # Buscar por etiqueta
        results = search_notes(tag="urgente")
        assert len(results) == 1
        assert results[0]["id"] == note_id

        # Mostrar por ID
        note = get_note_by_id(note_id)
        assert note is not None
        assert note["content"] == "Nota importante de la reunión"

        # Borrar
        assert delete_note(note_id) is True
        assert get_note_by_id(note_id) is None
        assert list_notes(limit=10) == []

    def test_múltiples_notas_mismo_tag(self, use_temp_db):
        """Varias notas pueden compartir la misma etiqueta."""
        add_note("Nota A de compras", ["compras"])
        add_note("Nota B de compras", ["compras"])
        add_note("Nota C de trabajo", ["trabajo"])

        results = search_notes(tag="compras")
        assert len(results) == 2

        results = search_notes(tag="trabajo")
        assert len(results) == 1
