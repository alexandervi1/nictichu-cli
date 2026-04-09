"""Herramienta para ejecutar tests."""

import subprocess
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger()


class PytestRunner:
    """Herramienta para ejecutar y gestionar tests."""
    
    def __init__(self):
        self.name = "test_runner"
        self.description = "Herramienta para ejecutar tests"
    
    def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "run_tests",
                "description": "Ejecutar tests",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del directorio de tests"},
                    "framework": {"type": "string", "description": "Framework: pytest, unittest", "default": "pytest"},
                    "coverage": {"type": "boolean", "description": "Generar cobertura", "default": False}
                }
            },
            {
                "name": "run_single_test",
                "description": "Ejecutar un test específico",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo de test"},
                    "test_name": {"type": "string", "description": "Nombre del test (opcional)"},
                    "framework": {"type": "string", "description": "Framework: pytest, unittest", "default": "pytest"}
                }
            },
            {
                "name": "list_tests",
                "description": "Listar tests disponibles",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del directorio de tests"},
                    "framework": {"type": "string", "description": "Framework: pytest, unittest", "default": "pytest"}
                }
            },
            {
                "name": "generate_coverage",
                "description": "Generar reporte de cobertura",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del código fuente"},
                    "format": {"type": "string", "description": "Formato: term, html, xml", "default": "term"}
                }
            }
        ]
    
    async def run_tests(
        self,
        path: str,
        framework: str = "pytest",
        coverage: bool = False
    ) -> dict[str, Any]:
        """Ejecutar tests."""
        test_path = Path(path)
        
        if framework == "pytest":
            return await self._run_pytest(test_path, coverage)
        elif framework == "unittest":
            return await self._run_unittest(test_path)
        else:
            raise ValueError(f"Framework no soportado: {framework}")
    
    async def _run_pytest(
        self,
        path: Path,
        coverage: bool
    ) -> dict[str, Any]:
        """Ejecutar pytest."""
        cmd = ["python", "-m", "pytest", str(path), "-v"]
        
        if coverage:
            cmd.extend(["--cov=src", "--cov-report=term"])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "framework": "pytest"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out",
                "framework": "pytest"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "pytest not installed",
                "framework": "pytest"
            }
    
    async def _run_unittest(
        self,
        path: Path
    ) -> dict[str, Any]:
        """Ejecutar unittest."""
        cmd = ["python", "-m", "unittest", "discover", "-s", str(path)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "framework": "unittest"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out",
                "framework": "unittest"
            }
    
    async def run_single_test(
        self,
        path: str,
        test_name: str | None = None,
        framework: str = "pytest"
    ) -> dict[str, Any]:
        """Ejecutar un test específico."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {path}")
        
        if framework == "pytest":
            if test_name:
                cmd = ["python", "-m", "pytest", f"{path}::{test_name}", "-v"]
            else:
                cmd = ["python", "-m", "pytest", path, "-v"]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    "success": result.returncode == 0,
                    "test": test_name or path,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "test": test_name or path,
                    "error": "Test timed out"
                }
        else:
            raise ValueError(f"Framework no soportado: {framework}")
    
    async def list_tests(
        self,
        path: str,
        framework: str = "pytest"
    ) -> list[dict[str, str]]:
        """Listar tests disponibles."""
        test_path = Path(path)
        
        tests = []
        
        if framework == "pytest":
            for test_file in test_path.rglob("test_*.py"):
                tests.append({
                    "file": str(test_file),
                    "name": test_file.stem,
                    "type": "file"
                })
        elif framework == "unittest":
            for test_file in test_path.rglob("test_*.py"):
                tests.append({
                    "file": str(test_file),
                    "name": test_file.stem,
                    "type": "file"
                })
        
        return tests
    
    async def generate_coverage(
        self,
        path: str,
        format: str = "term"
    ) -> dict[str, Any]:
        """Generar reporte de cobertura."""
        try:
            subprocess.run(
                ["coverage", "run", "-m", "pytest", path],
                capture_output=True,
                timeout=120
            )
            
            result = subprocess.run(
                ["coverage", "report", f"--format={format}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "report": result.stdout,
                "format": format
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "coverage not installed"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Coverage generation timed out"
            }
