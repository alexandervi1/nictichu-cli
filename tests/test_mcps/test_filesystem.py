"""Tests para MCP de filesystem."""

import pytest
import tempfile
from pathlib import Path
from src.mcps.servers.filesystem import FileSystemMCPClient


@pytest.mark.asyncio
class TestFileSystemMCP:
    """Tests para FileSystemMCPClient."""
    
    async def test_filesystem_initialization(self):
        """Test inicialización del cliente filesystem."""
        client = FileSystemMCPClient("test", {"allowed_directories": ["."]})
        
        assert client.server_name == "test"
        assert len(client.allowed_paths) == 0
    
    async def test_filesystem_connect(self):
        """Test conexión del cliente filesystem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            
            connected = await client.connect()
            
            assert connected is True
            assert len(client.allowed_paths) == 1
            
            await client.disconnect()
    
    async def test_filesystem_connect_nonexistent(self):
        """Test conexión con directorio inexistente."""
        client = FileSystemMCPClient("test", {"allowed_directories": ["/nonexistent/path"]})
        
        connected = await client.connect()
        
        assert connected is True
        assert len(client.allowed_paths) == 0
        
        await client.disconnect()
    
    async def test_list_tools(self):
        """Test listar herramientas."""
        client = FileSystemMCPClient("test", {})
        
        tools = await client.list_tools()
        
        assert len(tools) == 6
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "list_directory" in tool_names
        assert "create_directory" in tool_names
        assert "delete_file" in tool_names
        assert "file_exists" in tool_names
    
    async def test_write_and_read_file(self):
        """Test escribir y leer archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            # Escribir archivo
            result = await client.call_tool("write_file", {
                "path": f"{tmpdir}/test.txt",
                "content": "Hello, World!"
            })
            
            assert result is True
            
            # Leer archivo
            content = await client.call_tool("read_file", {
                "path": f"{tmpdir}/test.txt"
            })
            
            assert content == "Hello, World!"
            
            await client.disconnect()
    
    async def test_list_directory(self):
        """Test listar directorio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Crear archivos
            (tmpdir_path / "file1.txt").write_text("content1")
            (tmpdir_path / "file2.txt").write_text("content2")
            
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            # Listar directorio
            files = await client.call_tool("list_directory", {"path": tmpdir})
            
            assert len(files) == 2
            
            await client.disconnect()
    
    async def test_file_exists(self):
        """Test verificar si archivo existe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test.txt"
            
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            # Archivo no existe
            exists = await client.call_tool("file_exists", {"path": str(test_file)})
            assert exists is False
            
            # Crear archivo
            test_file.write_text("content")
            
            # Archivo existe
            exists = await client.call_tool("file_exists", {"path": str(test_file)})
            assert exists is True
            
            await client.disconnect()
    
    async def test_create_directory(self):
        """Test crear directorio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            # Crear directorio
            result = await client.call_tool("create_directory", {
                "path": f"{tmpdir}/newdir"
            })
            
            assert result is True
            assert Path(f"{tmpdir}/newdir").exists()
            
            await client.disconnect()
    
    async def test_delete_file(self):
        """Test eliminar archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "test.txt"
            test_file.write_text("content")
            
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            # Eliminar archivo
            result = await client.call_tool("delete_file", {"path": str(test_file)})
            
            assert result is True
            assert not test_file.exists()
            
            await client.disconnect()
    
    async def test_path_not_allowed(self):
        """Test ruta no permitida."""
        client = FileSystemMCPClient("test", {"allowed_directories": ["/tmp"]})
        await client.connect()
        
        # Intentar acceder a ruta no permitida
        with pytest.raises(PermissionError):
            await client.call_tool("read_file", {"path": "/etc/passwd"})
        
        await client.disconnect()
    
    async def test_file_not_found(self):
        """Test archivo no encontrado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            # Intentar leer archivo inexistente
            with pytest.raises(FileNotFoundError):
                await client.call_tool("read_file", {"path": f"{tmpdir}/nonexistent.txt"})
            
            await client.disconnect()
    
    async def test_list_resources(self):
        """Test listar recursos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            client = FileSystemMCPClient("test", {"allowed_directories": [tmpdir]})
            await client.connect()
            
            resources = await client.list_resources()
            
            assert len(resources) == 1
            assert resources[0]["uri"].startswith("file://")
            
            await client.disconnect()
