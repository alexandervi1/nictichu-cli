"""Tests para CodeReviewerTool."""

import pytest
import tempfile
from pathlib import Path
from src.tools.reviewer import CodeReviewerTool


@pytest.mark.asyncio
class TestCodeReviewerTool:
    """Tests para CodeReviewerTool."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.reviewer = CodeReviewerTool()
    
    def test_list_tools(self):
        """Test listar herramientas."""
        tools = self.reviewer.list_tools()
        
        assert len(tools) == 5
        tool_names = [t["name"] for t in tools]
        assert "analyze_file" in tool_names
        assert "find_issues" in tool_names
        assert "generate_report" in tool_names
        assert "check_security" in tool_names
        assert "check_complexity" in tool_names
    
    async def test_analyze_file(self):
        """Test analizar archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear archivo de prueba
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("""
def hello():
    print("Hello, World!")

class Test:
    pass
""")
            
            result = await self.reviewer.analyze_file(str(test_file))
            
            assert "file" in result
            assert "size" in result
            assert "lines" in result
            assert "checks" in result
    
    async def test_analyze_file_with_checks(self):
        """Test analizar archivo con verificaciones específicas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("x = 1")
            
            result = await self.reviewer.analyze_file(
                str(test_file),
                checks=["complexity", "security"]
            )
            
            assert "complexity" in result["checks"]
            assert "security" in result["checks"]
    
    async def test_find_issues(self):
        """Test encontrar issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("""
password = "secret123"
eval("print('test')")
""")
            
            issues = await self.reviewer.find_issues(str(test_file))
            
            # Debería encontrar al menos un issue de seguridad
            security_issues = [i for i in issues if i.get("type") == "hardcoded_password"]
            assert len(security_issues) > 0
    
    async def test_generate_report_markdown(self):
        """Test generar reporte en Markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("x = 1")
            
            report = await self.reviewer.generate_report(
                str(test_file),
                format="markdown"
            )
            
            assert "# Code Review Report" in report
            assert "test.py" in report
    
    async def test_generate_report_text(self):
        """Test generar reporte en texto."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("x = 1")
            
            report = await self.reviewer.generate_report(
                str(test_file),
                format="text"
            )
            
            assert "Code Review Report" in report
    
    async def test_check_security(self):
        """Test verificar seguridad."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("""
password = "secret"
api_key = "key123"
""")
            
            result = await self.reviewer.check_security(str(test_file))
            
            assert "checks" in result
            assert "security" in result["checks"]
            assert result["checks"]["security"]["is_secure"] is False
    
    async def test_check_complexity(self):
        """Test verificar complejidad."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(f"{tmpdir}/test.py")
            test_file.write_text("""
def function1():
    pass

def function2():
    pass

class Test:
    pass
""")
            
            result = await self.reviewer.check_complexity(str(test_file))
            
            assert "checks" in result
            assert "complexity" in result["checks"]
            assert result["checks"]["complexity"]["function_count"] == 2
            assert result["checks"]["complexity"]["class_count"] == 1
    
    async def test_file_not_found(self):
        """Test archivo no encontrado."""
        with pytest.raises(FileNotFoundError):
            await self.reviewer.analyze_file("/nonexistent/file.py")
