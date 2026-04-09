"""Herramienta para generar documentación."""

from pathlib import Path
from typing import Any
import re

from ..utils.logger import get_logger

logger = get_logger()


class DocGeneratorTool:
    """Herramienta para generar documentación."""
    
    def __init__(self):
        self.name = "doc_generator"
        self.description = "Herramienta para generar documentación de código"
    
    def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "generate_module_doc",
                "description": "Generar documentación de módulo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "format": {"type": "string", "description": "Formato: markdown, rst, text", "default": "markdown"}
                }
            },
            {
                "name": "generate_class_doc",
                "description": "Generar documentación de clase",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "class_name": {"type": "string", "description": "Nombre de la clase"},
                    "format": {"type": "string", "description": "Formato: markdown, rst, text", "default": "markdown"}
                }
            },
            {
                "name": "generate_function_doc",
                "description": "Generar documentación de función",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "function_name": {"type": "string", "description": "Nombre de la función"},
                    "format": {"type": "string", "description": "Formato: markdown, rst, text", "default": "markdown"}
                }
            },
            {
                "name": "generate_readme",
                "description": "Generar README",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del proyecto"},
                    "include_examples": {"type": "boolean", "description": "Incluir ejemplos", "default": True}
                }
            }
        ]
    
    async def generate_module_doc(
        self,
        path: str,
        format: str = "markdown"
    ) -> str:
        """Generar documentación de módulo."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        
        functions = self._extract_functions(content)
        classes = self._extract_classes(content)
        imports = self._extract_imports(content)
        
        if format == "markdown":
            return self._format_module_markdown(file_path.name, imports, functions, classes)
        elif format == "rst":
            return self._format_module_rst(file_path.name, imports, functions, classes)
        else:
            return self._format_module_text(file_path.name, imports, functions, classes)
    
    async def generate_class_doc(
        self,
        path: str,
        class_name: str,
        format: str = "markdown"
    ) -> str:
        """Generar documentación de clase."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        
        class_info = self._extract_class_info(content, class_name)
        
        if not class_info:
            raise ValueError(f"Clase no encontrada: {class_name}")
        
        if format == "markdown":
            return self._format_class_markdown(class_info)
        elif format == "rst":
            return self._format_class_rst(class_info)
        else:
            return self._format_class_text(class_info)
    
    async def generate_function_doc(
        self,
        path: str,
        function_name: str,
        format: str = "markdown"
    ) -> str:
        """Generar documentación de función."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        
        function_info = self._extract_function_info(content, function_name)
        
        if not function_info:
            raise ValueError(f"Función no encontrada: {function_name}")
        
        if format == "markdown":
            return self._format_function_markdown(function_info)
        elif format == "rst":
            return self._format_function_rst(function_info)
        else:
            return self._format_function_text(function_info)
    
    async def generate_readme(
        self,
        path: str,
        include_examples: bool = True
    ) -> str:
        """Generar README del proyecto."""
        project_dir = Path(path)
        
        if not project_dir.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {path}")
        
        readme_content = "# Project Name\n\n"
        readme_content += "Description of the project.\n\n"
        readme_content += "## Installation\n\n"
        readme_content += "```bash\n"
        readme_content += "pip install -r requirements.txt\n"
        readme_content += "```\n\n"
        
        if include_examples:
            readme_content += "## Usage\n\n"
            readme_content += "```python\n"
            readme_content += "# Example usage\n"
            readme_content += "```\n\n"
        
        readme_content += "## Features\n\n"
        readme_content += "- Feature 1\n"
        readme_content += "- Feature 2\n\n"
        readme_content += "## License\n\n"
        readme_content += "MIT License\n"
        
        return readme_content
    
    def _extract_functions(self, content: str) -> list[dict[str, Any]]:
        """Extraer funciones del código."""
        functions = []
        
        pattern = r"def\s+(\w+)\s*\((.*?)\)\s*(->\s*(.+?))?\s*:"
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            func_name = match.group(1)
            params = match.group(2) or ""
            return_type = match.group(4) or "None"
            
            docstring = self._extract_docstring(content, match.end())
            
            functions.append({
                "name": func_name,
                "parameters": [p.strip() for p in params.split(",") if p.strip()],
                "return_type": return_type.strip(),
                "docstring": docstring
            })
        
        return functions
    
    def _extract_classes(self, content: str) -> list[dict[str, Any]]:
        """Extraer clases del código."""
        classes = []
        
        pattern = r"class\s+(\w+)(?:\s*\((.*?)\))?\s*:"
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            class_name = match.group(1)
            base_classes = match.group(2) or ""
            
            docstring = self._extract_docstring(content, match.end())
            
            class_methods = self._extract_class_methods(content, match.start())
            
            classes.append({
                "name": class_name,
                "base_classes": [b.strip() for b in base_classes.split(",") if b.strip()],
                "docstring": docstring,
                "methods": class_methods
            })
        
        return classes
    
    def _extract_imports(self, content: str) -> list[str]:
        """Extraer imports del código."""
        imports = []
        
        import_pattern = r"^import\s+.*$"
        from_pattern = r"^from\s+.*import\s+.*$"
        
        for line in content.split("\n"):
            if re.match(import_pattern, line) or re.match(from_pattern, line):
                imports.append(line.strip())
        
        return imports
    
    def _extract_docstring(self, content: str, start_pos: int) -> str:
        """Extraer docstring del código."""
        rest = content[start_pos:].lstrip()
        
        if rest.startswith('"""'):
            end_pos = rest.find('"""', 3)
            if end_pos != -1:
                return rest[3:end_pos].strip()
        elif rest.startswith("'''"):
            end_pos = rest.find("'''", 3)
            if end_pos != -1:
                return rest[3:end_pos].strip()
        
        return ""
    
    def _extract_class_methods(self, content: str, class_start: int) -> list[dict[str, Any]]:
        """Extraer métodos de una clase."""
        methods = []
        
        class_end = content.find("\nclass ", class_start + 1)
        if class_end == -1:
            class_end = len(content)
        
        class_content = content[class_start:class_end]
        
        pattern = r"def\s+(\w+)\s*\((.*?)\)\s*(->\s*(.+?))?\s*:"
        matches = re.finditer(pattern, class_content, re.MULTILINE)
        
        for match in matches:
            method_name = match.group(1)
            if method_name.startswith("_"):
                continue
            
            params = match.group(2) or ""
            return_type = match.group(4) or "None"
            
            docstring = self._extract_docstring(class_content, match.end())
            
            methods.append({
                "name": method_name,
                "parameters": [p.strip() for p in params.split(",") if p.strip()],
                "return_type": return_type.strip(),
                "docstring": docstring
            })
        
        return methods
    
    def _extract_class_info(self, content: str, class_name: str) -> dict[str, Any] | None:
        """Extraer información de una clase específica."""
        pattern = rf"class\s+{class_name}(?:\s*\((.*?)\))?\s*:"
        match = re.search(pattern, content)
        
        if not match:
            return None
        
        base_classes = match.group(1) or ""
        docstring = self._extract_docstring(content, match.end())
        methods = self._extract_class_methods(content, match.start())
        
        return {
            "name": class_name,
            "base_classes": [b.strip() for b in base_classes.split(",") if b.strip()],
            "docstring": docstring,
            "methods": methods
        }
    
    def _extract_function_info(self, content: str, function_name: str) -> dict[str, Any] | None:
        """Extraer información de una función específica."""
        pattern = rf"def\s+{function_name}\s*\((.*?)\)\s*(->\s*(.+?))?\s*:"
        match = re.search(pattern, content)
        
        if not match:
            return None
        
        params = match.group(1) or ""
        return_type = match.group(3) or "None"
        docstring = self._extract_docstring(content, match.end())
        
        return {
            "name": function_name,
            "parameters": [p.strip() for p in params.split(",") if p.strip()],
            "return_type": return_type.strip(),
            "docstring": docstring
        }
    
    def _format_module_markdown(
        self,
        module_name: str,
        imports: list[str],
        functions: list[dict[str, Any]],
        classes: list[dict[str, Any]]
    ) -> str:
        """Formatear módulo como markdown."""
        doc = f"# {module_name}\n\n"
        
        if imports:
            doc += "## Imports\n\n```python\n"
            doc += "\n".join(imports)
            doc += "\n```\n\n"
        
        if classes:
            doc += "## Classes\n\n"
            for cls in classes:
                doc += f"### {cls['name']}\n\n"
                if cls['docstring']:
                    doc += f"{cls['docstring']}\n\n"
                if cls['base_classes']:
                    doc += f"**Base classes:** {', '.join(cls['base_classes'])}\n\n"
                if cls['methods']:
                    doc += "**Methods:**\n\n"
                    for method in cls['methods']:
                        doc += f"- `{method['name']}`({', '.join(method['parameters'])})"
                        if method['return_type']:
                            doc += f" -> {method['return_type']}"
                        doc += "\n"
                doc += "\n"
        
        if functions:
            doc += "## Functions\n\n"
            for func in functions:
                doc += f"### `{func['name']}`({', '.join(func['parameters'])})"
                if func['return_type']:
                    doc += f" -> {func['return_type']}"
                doc += "\n\n"
                if func['docstring']:
                    doc += f"{func['docstring']}\n\n"
        
        return doc
    
    def _format_module_rst(
        self,
        module_name: str,
        imports: list[str],
        functions: list[dict[str, Any]],
        classes: list[dict[str, Any]]
    ) -> str:
        """Formatear módulo como reStructuredText."""
        doc = f".. _{module_name}:\n\n{module_name}\n"
        doc += "=" * len(module_name) + "\n\n"
        
        if imports:
            doc += "Imports\n-------\n\n::\n\n"
            doc += "\n".join(imports)
            doc += "\n\n"
        
        if classes:
            doc += "Classes\n-------\n\n"
            for cls in classes:
                doc += f".. _{cls['name']}:\n\n{cls['name']}\n"
                doc += "-" * len(cls['name']) + "\n\n"
                if cls['docstring']:
                    doc += f"{cls['docstring']}\n\n"
        
        if functions:
            doc += "Functions\n---------\n\n"
            for func in functions:
                doc += f".. function:: {func['name']}({', '.join(func['parameters'])})"
                if func['return_type']:
                    doc += f" -> {func['return_type']}"
                doc += "\n\n"
                if func['docstring']:
                    doc += f"   {func['docstring']}\n\n"
        
        return doc
    
    def _format_module_text(
        self,
        module_name: str,
        imports: list[str],
        functions: list[dict[str, Any]],
        classes: list[dict[str, Any]]
    ) -> str:
        """Formatear módulo como texto plano."""
        doc = f"Module: {module_name}\n\n"
        
        if imports:
            doc += "Imports:\n"
            doc += "\n".join(imports)
            doc += "\n\n"
        
        if classes:
            doc += "Classes:\n"
            for cls in classes:
                doc += f"  - {cls['name']}"
                if cls['base_classes']:
                    doc += f" ({', '.join(cls['base_classes'])})"
                doc += "\n"
            doc += "\n"
        
        if functions:
            doc += "Functions:\n"
            for func in functions:
                doc += f"  - {func['name']}({', '.join(func['parameters'])})"
                if func['return_type']:
                    doc += f" -> {func['return_type']}"
                doc += "\n"
        
        return doc
    
    def _format_class_markdown(self, class_info: dict[str, Any]) -> str:
        """Formatear clase como markdown."""
        doc = f"# {class_info['name']}\n\n"
        
        if class_info['base_classes']:
            doc += f"**Base classes:** {', '.join(class_info['base_classes'])}\n\n"
        
        if class_info['docstring']:
            doc += f"{class_info['docstring']}\n\n"
        
        if class_info['methods']:
            doc += "## Methods\n\n"
            for method in class_info['methods']:
                doc += f"### `{method['name']}`({', '.join(method['parameters'])})"
                if method['return_type']:
                    doc += f" -> {method['return_type']}"
                doc += "\n\n"
                if method['docstring']:
                    doc += f"{method['docstring']}\n\n"
        
        return doc
    
    def _format_class_rst(self, class_info: dict[str, Any]) -> str:
        """Formatear clase como reStructuredText."""
        doc = f".. class:: {class_info['name']}"
        if class_info['base_classes']:
            doc += f"({', '.join(class_info['base_classes'])})"
        doc += "\n\n"
        
        if class_info['docstring']:
            doc += f"   {class_info['docstring']}\n\n"
        
        if class_info['methods']:
            for method in class_info['methods']:
                doc += f"   .. method:: {method['name']}({', '.join(method['parameters'])})"
                if method['return_type']:
                    doc += f" -> {method['return_type']}"
                doc += "\n\n"
                if method['docstring']:
                    doc += f"      {method['docstring']}\n\n"
        
        return doc
    
    def _format_class_text(self, class_info: dict[str, Any]) -> str:
        """Formatear clase como texto plano."""
        doc = f"Class: {class_info['name']}\n"
        
        if class_info['base_classes']:
            doc += f"Base classes: {', '.join(class_info['base_classes'])}\n"
        
        if class_info['docstring']:
            doc += f"\n{class_info['docstring']}\n"
        
        if class_info['methods']:
            doc += "\nMethods:\n"
            for method in class_info['methods']:
                doc += f"  - {method['name']}({', '.join(method['parameters'])})"
                if method['return_type']:
                    doc += f" -> {method['return_type']}"
                doc += "\n"
        
        return doc
    
    def _format_function_markdown(self, function_info: dict[str, Any]) -> str:
        """Formatear función como markdown."""
        doc = f"# `{function_info['name']}`\n\n"
        doc += f"```python\n{function_info['name']}({', '.join(function_info['parameters'])})"
        
        if function_info['return_type']:
            doc += f" -> {function_info['return_type']}"
        
        doc += "\n```\n\n"
        
        if function_info['docstring']:
            doc += f"{function_info['docstring']}\n"
        
        return doc
    
    def _format_function_rst(self, function_info: dict[str, Any]) -> str:
        """Formatear función como reStructuredText."""
        doc = f".. function:: {function_info['name']}({', '.join(function_info['parameters'])})"
        
        if function_info['return_type']:
            doc += f" -> {function_info['return_type']}"
        
        doc += "\n\n"
        
        if function_info['docstring']:
            doc += f"   {function_info['docstring']}\n"
        
        return doc
    
    def _format_function_text(self, function_info: dict[str, Any]) -> str:
        """Formatear función como texto plano."""
        doc = f"Function: {function_info['name']}({', '.join(function_info['parameters'])})"
        
        if function_info['return_type']:
            doc += f" -> {function_info['return_type']}"
        
        doc += "\n"
        
        if function_info['docstring']:
            doc += f"\n{function_info['docstring']}\n"
        
        return doc