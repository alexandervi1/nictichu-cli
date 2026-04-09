"""Tests de integración completos."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.core import NictichuCore
from src.core.context import ContextManager
from src.models.registry import get_registry, ModelRegistry
from src.tools.editor import CodeEditorTool
from src.tools.reviewer import CodeReviewerTool
from src.tools.tester import PytestRunner
from src.tools.docs import DocGeneratorTool


class TestEndToEndIntegration:
    """Tests de integración de punta a punta."""
    
    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Configurar registry para tests."""
        registry = get_registry()
        registry.clear()
        
        from src.models.base import BaseModel
        
        class MockModel(BaseModel):
            def __init__(self, model_id: str, config: dict = None):
                super().__init__(model_id, config)
            
            async def generate(self, messages, **kwargs):
                return {"text": "Mock response", "tool_calls": None}
            
            async def chat(self, messages, **kwargs):
                return "Mock chat response"
            
            async def generate_stream(self, messages, **kwargs):
                yield "Mock"
                yield " response"
            
            async def chat_stream(self, messages, **kwargs):
                yield "Mock"
                yield " chat response"
            
            async def is_available(self):
                return True
        
        registry.register_provider("test-provider", MockModel)
        
        yield
        
        registry.clear()
    
    @pytest.mark.asyncio
    async def test_core_initialization(self):
        """Test inicialización del core."""
        core = NictichuCore(
            model_name="test-model",
            provider="test-provider"
        )
        
        await core.initialize()
        
        assert core.model is not None
        assert core.mcp_manager is not None
    
    @pytest.mark.asyncio
    async def test_core_tools_integration(self):
        """Test integración de herramientas con core."""
        core = NictichuCore(
            model_name="test-model",
            provider="test-provider"
        )
        
        await core.initialize()
        
        tools = await core.get_available_tools()
        
        assert len(tools) > 0
        
        tool_names = [t["name"] for t in tools]
        
        # Verificar que hay herramientas disponibles
        assert len(tool_names) > 0, f"No tools found"
        # Verificar algunas herramientas específicas
        assert "code_edit_file" in tool_names, f"code_edit_file not found in {tool_names}"
        assert "code_generate_module_doc" in tool_names, f"code_generate_module_doc not found in {tool_names}"
    
    @pytest.mark.asyncio
    async def test_core_mcp_integration(self):
        """Test integración de MCP con core."""
        core = NictichuCore(
            model_name="test-model",
            provider="test-provider",
            mcp_config={
                "enabled": ["filesystem"],
                "servers": {
                    "filesystem": {
                        "type": "fileSystem",
                        "root_path": tempfile.gettempdir()
                    }
                }
            }
        )
        
        await core.initialize()
        await core.initialize_mcps()
        
        mcps = await core.get_active_mcps()
        
        assert isinstance(mcps, list)
    
    @pytest.mark.asyncio
    async def test_context_with_tools(self):
        """Test contexto con herramientas."""
        context = ContextManager()
        
        context.add_message("user", "Crear un archivo test.py")
        context.add_message("assistant", "Voy a usar create_file")
        context.add_message("system", '{"success": true}')
        
        messages = context.get_messages()
        
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "system"
        
        summary = context.get_summary()
        assert summary["total_messages"] == 3
    
    @pytest.mark.asyncio
    async def test_editor_tool_integration(self):
        """Test integración de herramienta de edición."""
        editor = CodeEditorTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            
            result = await editor.create_file(
                str(test_file),
                "print('hello')",
                "python"
            )
            
            assert result["success"] is True
            assert test_file.exists()
            
            result = await editor.edit_file(
                str(test_file),
                [{"old": "hello", "new": "world"}]
            )
            
            assert result["success"] is True
            assert "world" in test_file.read_text()
    
    @pytest.mark.asyncio
    async def test_reviewer_tool_integration(self):
        """Test integración de herramienta de revisión."""
        reviewer = CodeReviewerTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\nprint(x)")
            
            result = await reviewer.analyze_file(str(test_file))
            
            assert "file" in result
            assert "checks" in result
            assert "complexity" in result["checks"]
    
    @pytest.mark.asyncio
    async def test_tester_tool_integration(self):
        """Test integración de herramienta de tests."""
        tester = PytestRunner()
        
        tools = tester.list_tools()
        
        assert len(tools) > 0
        assert any(t["name"] == "run_tests" for t in tools)
    
    @pytest.mark.asyncio
    async def test_docs_tool_integration(self):
        """Test integración de herramienta de documentación."""
        docs = DocGeneratorTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('"""Module docstring."""\n\ndef foo():\n    """Function docstring."""\n    pass')
            
            result = await docs.generate_module_doc(str(test_file), format="markdown")
            
            assert "test.py" in result
            assert "Module docstring" in result or "foo" in result
    
    @pytest.mark.asyncio
    async def test_conversation_flow(self):
        """Test flujo de conversación completo."""
        from src.cli.conversation import ConversationLoop
        
        mock_core = MagicMock()
        mock_core.model_name = "test-model"
        mock_core.provider = "test-provider"
        mock_core.mcp_manager = None
        
        mock_model = AsyncMock()
        mock_model.generate = AsyncMock(return_value={
            "text": "Respuesta de prueba",
            "tool_calls": None
        })
        mock_core.model = mock_model
        
        conv = ConversationLoop(mock_core)
        await conv.initialize()
        
        response = await conv.send_message("Test message")
        
        assert response["text"] is not None
        assert len(conv.context.history) > 0
    
    @pytest.mark.asyncio
    async def test_filesystem_mcp_integration(self):
        """Test integración de FileSystem MCP."""
        from src.mcps.servers.filesystem import FileSystemMCPClient
        
        with tempfile.TemporaryDirectory() as tmpdir:
            client = FileSystemMCPClient("test-fs", {"root_path": tmpdir})
            
            connected = await client.connect()
            assert connected is True
            
            tools = await client.list_tools()
            assert len(tools) > 0
            
            result = await client.call_tool("write_file", {
                "path": "test.txt",
                "content": "Hello, world!"
            })
            
            assert result is True
            
            result = await client.call_tool("read_file", {
                "path": "test.txt"
            })
            
            assert "Hello, world!" in result
            
            await client.disconnect()


class TestCLIIntegration:
    """Tests de integración del CLI."""
    
    @pytest.mark.asyncio
    async def test_cli_workflow(self):
        """Test flujo completo del CLI."""
        from src.cli.interface import NictichuCLI
        from unittest.mock import patch
        
        with patch('src.cli.interface.NictichuCore') as mock_core_class:
            mock_core = AsyncMock()
            mock_core.initialize = AsyncMock()
            mock_core.initialize_mcps = AsyncMock()
            mock_core.get_available_tools = AsyncMock(return_value=[])
            mock_core.get_active_mcps = AsyncMock(return_value=[])
            mock_core.get_status = AsyncMock(return_value={"test": {"ok": True, "details": "OK"}})
            mock_core.cleanup = AsyncMock()
            
            mock_core_class.return_value = mock_core
            
            cli = NictichuCLI(model_name="test-model", provider="test-provider")
            
            assert cli.model_name == "test-model"
            assert cli.provider == "test-provider"


class TestToolsWithMCP:
    """Tests de herramientas con MCP."""
    
    @pytest.mark.asyncio
    async def test_editor_with_mcp(self):
        """Test editor con MCP."""
        editor = CodeEditorTool()
        
        tools = editor.list_tools()
        
        assert any(t["name"] == "create_file" for t in tools)
        assert any(t["name"] == "edit_file" for t in tools)
        assert any(t["name"] == "search_and_replace" for t in tools)
    
    @pytest.mark.asyncio
    async def test_multiple_tools_workflow(self):
        """Test flujo con múltiples herramientas."""
        editor = CodeEditorTool()
        reviewer = CodeReviewerTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "example.py"
            
            await editor.create_file(
                str(test_file),
                "password = 'secret123'\nx = 1\nprint(x)",
                "python"
            )
            
            analysis = await reviewer.analyze_file(str(test_file))
            
            assert "security" in analysis["checks"]
            
            security_issues = analysis["checks"]["security"]["issues"]
            
            assert len(security_issues) > 0