"""Tests de integración para CLI."""

import pytest
from pathlib import Path
import tempfile
import json

from src.cli.interface import NictichuCLI
from src.cli.conversation import ConversationLoop
from src.cli.commands import CommandHandler


class TestNictichuCLI:
    """Tests para NictichuCLI."""
    
    @pytest.fixture
    def cli(self):
        """Crear instancia de CLI."""
        return NictichuCLI(
            model_name="test-model",
            provider="test-provider"
        )
    
    def test_cli_initialization(self, cli):
        """Test inicialización de CLI."""
        assert cli.model_name == "test-model"
        assert cli.provider == "test-provider"
        assert cli.running is False
        assert cli.session is None
        assert cli.core is None
        assert cli.conversation is None
        assert cli.command_handler is None
    
    def test_theme_colors(self, cli):
        """Test colores del tema."""
        assert cli.THEME["primary"] == "#06B6D4"
        assert cli.THEME["secondary"] == "#0891B2"
        assert cli.THEME["success"] == "#10B981"
        assert cli.THEME["error"] == "#EF4444"
    
    def test_prompt_style(self, cli):
        """Test estilo del prompt."""
        style = cli._create_prompt_style()
        assert style is not None
    
    def test_get_prompt(self, cli):
        """Test generación del prompt."""
        prompt = cli._get_prompt()
        assert "test-model" in prompt


class TestConversationLoop:
    """Tests para ConversationLoop."""
    
    @pytest.fixture
    def conversation(self, mock_core):
        """Crear instancia de conversación."""
        conv = ConversationLoop(mock_core)
        return conv
    
    @pytest.fixture
    def mock_core(self):
        """Crear mock del core."""
        from unittest.mock import AsyncMock, MagicMock
        
        core = MagicMock()
        core.model_name = "test-model"
        core.provider = "test-provider"
        core.mcp_manager = MagicMock()
        core.mcp_manager.get_available_servers.return_value = []
        core.model = AsyncMock()
        core.model.generate = AsyncMock(return_value={"text": "Test response"})
        
        return core
    
    def test_conversation_initialization(self, conversation):
        """Test inicialización de conversación."""
        assert conversation.context is not None
        assert len(conversation.tools) == 0
        assert len(conversation.mcp_tools) == 0
    
    @pytest.mark.asyncio
    async def test_conversation_register_tools(self, conversation):
        """Test registro de herramientas."""
        await conversation.initialize()
        
        assert "code_editor" in conversation.tools
        assert "code_reviewer" in conversation.tools
        assert "test_runner" in conversation.tools
        assert "doc_generator" in conversation.tools
    
    @pytest.mark.asyncio
    async def test_conversation_clear(self, conversation):
        """Test limpiar contexto."""
        await conversation.initialize()
        
        conversation.context.add_message("user", "test message")
        assert len(conversation.context.history) > 0
        
        await conversation.clear()
        assert len(conversation.context.history) == 0
    
    @pytest.mark.asyncio
    async def test_conversation_save_load(self, conversation, tmp_path):
        """Test guardar y cargar conversación."""
        await conversation.initialize()
        
        conversation.context.add_message("user", "test message")
        
        filepath = tmp_path / "test_conversation.json"
        await conversation.save(str(filepath))
        
        assert filepath.exists()
        
        conversation.context.clear()
        assert len(conversation.context.history) == 0
        
        await conversation.load(str(filepath))
        assert len(conversation.context.history) > 0
    
    def test_get_tool_definitions(self, conversation):
        """Test obtención de definiciones de herramientas."""
        from unittest.mock import MagicMock
        
        conversation.tools = {
            "test_tool": MagicMock(list_tools=lambda: [{
                "name": "test_action",
                "description": "Test description",
                "parameters": {}
            }])
        }
        
        definitions = conversation._get_tool_definitions()
        
        assert len(definitions) > 0
        assert definitions[0]["type"] == "function"
        assert "code_test_tool" in definitions[0]["function"]["name"]


class TestCommandHandler:
    """Tests para CommandHandler."""
    
    @pytest.fixture
    def handler(self, mock_core, mock_conversation):
        """Crear instancia de handler."""
        return CommandHandler(mock_core, mock_conversation)
    
    @pytest.fixture
    def mock_core(self):
        """Crear mock del core."""
        from unittest.mock import MagicMock
        
        core = MagicMock()
        core.provider = "test-provider"
        core.model_name = "test-model"
        
        return core
    
    @pytest.fixture
    def mock_conversation(self):
        """Crear mock de conversación."""
        from unittest.mock import AsyncMock
        
        conv = AsyncMock()
        conv.tools = {}
        
        return conv
    
    @pytest.mark.asyncio
    async def test_cmd_help(self, handler):
        """Test comando help."""
        result = await handler.handle("help", "")
        assert result["text"] is not None
        assert "/help" in result["text"]
    
    @pytest.mark.asyncio
    async def test_cmd_tools(self, handler):
        """Test comando tools."""
        from unittest.mock import MagicMock
        
        handler.conversation.tools = {
            "test_tool": MagicMock(description="Test tool")
        }
        
        result = await handler.handle("tools", "")
        assert result["text"] is not None
        assert "test_tool" in result["text"]
    
    @pytest.mark.asyncio
    async def test_cmd_clear(self, handler):
        """Test comando clear."""
        result = await handler.handle("clear", "")
        assert result["text"] is not None
        handler.conversation.clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cmd_unknown(self, handler):
        """Test comando desconocido."""
        result = await handler.handle("unknown", "")
        assert "error" in result
        assert "desconocido" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cmd_save(self, handler):
        """Test comando save."""
        result = await handler.handle("save", "test.json")
        assert result["text"] is not None
        handler.conversation.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cmd_load(self, handler):
        """Test comando load."""
        result = await handler.handle("load", "test.json")
        assert result["text"] is not None
        handler.conversation.load.assert_called_once()