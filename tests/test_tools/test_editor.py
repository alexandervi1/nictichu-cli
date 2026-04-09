"""Tests para CodeEditorTool."""

import pytest
import tempfile
from pathlib import Path
from src.tools.editor import CodeEditorTool


@pytest.mark.asyncio
class TestCodeEditorTool:
    """Tests para CodeEditorTool."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.editor = CodeEditorTool()
    
    def test_list_tools(self):
        """Test listar herramientas."""
        tools = self.editor.list_tools()
        
        assert len(tools) == 6
        tool_names = [t["name"] for t in tools]
        assert "create_file" in tool_names
        assert "edit_file" in tool_names
        assert "refactor_file" in tool_names
        assert "search_and_replace" in tool_names
        assert "create_directory" in tool_names
        assert "delete_file" in tool_names
    
    async def test_create_file(self):
        """Test crear archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await self.editor.create_file(
                f"{tmpdir}/test.py",
                "print('Hello, World!')"
            )
            
            assert result["success"] is True
            assert Path(f"{tmpdir}/test.py").exists()
            assert result["lines"] == 1
    
    async def test_create_file_already_exists(self):
        """Test crear archivo que ya existe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo
            Path(f"{tmpdir}/test.py").write_text("content")
            
            # Intentar crear de nuevo
            with pytest.raises(FileExistsError):
                await self.editor.create_file(
                    f"{tmpdir}/test.py",
                    "new content"
                )
    
    async def test_edit_file(self):
        """Test editar archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo
            Path(f"{tmpdir}/test.py").write_text("Hello, World!")
            
            # Editar archivo
            result = await self.editor.edit_file(
                f"{tmpdir}/test.py",
                [{"old": "World", "new": "Python"}]
            )
            
            assert result["success"] is True
            assert result["edits_applied"] == 1
            
            # Verificar contenido
            content = Path(f"{tmpdir}/test.py").read_text()
            assert content == "Hello, Python!"
    
    async def test_edit_file_not_found(self):
        """Test editar archivo no encontrado."""
        with pytest.raises(FileNotFoundError):
            await self.editor.edit_file(
                "/nonexistent/file.py",
                [{"old": "old", "new": "new"}]
            )
    
    async def test_search_and_replace(self):
        """Test buscar y reemplazar."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo
            Path(f"{tmpdir}/test.py").write_text("Hello, World!")
            
            # Buscar y reemplazar
            result = await self.editor.search_and_replace(
                f"{tmpdir}/test.py",
                "World",
                "Python",
                use_regex=False
            )
            
            assert result["success"] is True
            
            # Verificar contenido
            content = Path(f"{tmpdir}/test.py").read_text()
            assert content == "Hello, Python!"
    
    async def test_create_directory(self):
        """Test crear directorio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = await self.editor.create_directory(f"{tmpdir}/newdir")
            
            assert result["success"] is True
            assert Path(f"{tmpdir}/newdir").exists()
    
    async def test_delete_file(self):
        """Test eliminar archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo
            file_path = Path(f"{tmpdir}/test.py")
            file_path.write_text("content")
            
            # Eliminar archivo
            result = await self.editor.delete_file(str(file_path))
            
            assert result["success"] is True
            assert not file_path.exists()
    
    async def test_delete_file_not_found(self):
        """Test eliminar archivo no encontrado."""
        with pytest.raises(FileNotFoundError):
            await self.editor.delete_file("/nonexistent/file.py")
    
    def test_count_lines_changed(self):
        """Test contar líneas cambiadas."""
        original = "line1\nline2\nline3"
        modified = "line1\nmodified\nline3"
        
        changed = self.editor._count_lines_changed(original, modified)
        
        assert changed == 1
