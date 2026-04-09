"""Herramienta para edición de código."""

from pathlib import Path
from typing import Any
import re

from ..utils.logger import get_logger

logger = get_logger()


class CodeEditorTool:
    """Herramienta para crear, editar y refactorizar código."""
    
    def __init__(self):
        self.name = "code_editor"
        self.description = "Herramienta para crear, editar y refactorizar código"
    
    def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "create_file",
                "description": "Crear nuevo archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "content": {"type": "string", "description": "Contenido del archivo"},
                    "language": {"type": "string", "description": "Lenguaje de programación", "default": "python"}
                }
            },
            {
                "name": "edit_file",
                "description": "Editar archivo existente",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "edits": {"type": "array", "description": "Lista de ediciones"}
                }
            },
            {
                "name": "refactor_file",
                "description": "Refactorizar archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "refactor_type": {"type": "string", "description": "Tipo de refactorización: format, sort_imports, remove_unused"}
                }
            },
            {
                "name": "search_and_replace",
                "description": "Buscar y reemplazar en archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "search": {"type": "string", "description": "Patrón a buscar"},
                    "replace": {"type": "string", "description": "Reemplazo"},
                    "use_regex": {"type": "boolean", "description": "Usar expresión regular", "default": False}
                }
            },
            {
                "name": "create_directory",
                "description": "Crear directorio",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del directorio"}
                }
            },
            {
                "name": "delete_file",
                "description": "Eliminar archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"}
                }
            }
        ]
    
    async def create_file(
        self,
        path: str,
        content: str,
        language: str = "python"
    ) -> dict[str, Any]:
        """Crear nuevo archivo."""
        file_path = Path(path)
        
        if file_path.exists():
            raise FileExistsError(f"El archivo ya existe: {path}")
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Archivo creado: {path}")
        
        return {
            "success": True,
            "path": str(file_path),
            "language": language,
            "lines": content.count("\n") + 1,
            "size": len(content)
        }
    
    async def edit_file(
        self,
        path: str,
        edits: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Editar archivo existente."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        for edit in edits:
            old_text = edit.get("old", "")
            new_text = edit.get("new", "")
            
            if old_text not in content:
                raise ValueError(f"Texto no encontrado: {old_text[:50]}...")
            
            content = content.replace(old_text, new_text, 1)
        
        file_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Archivo editado: {path}")
        
        return {
            "success": True,
            "path": str(file_path),
            "edits_applied": len(edits),
            "lines_changed": self._count_lines_changed(original_content, content)
        }
    
    async def refactor_file(
        self,
        path: str,
        refactor_type: str = "format"
    ) -> dict[str, Any]:
        """Refactorizar archivo."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        if refactor_type == "format":
            content = self._format_code(content, file_path.suffix)
        elif refactor_type == "sort_imports":
            content = self._sort_imports(content)
        elif refactor_type == "remove_unused":
            content = self._remove_unused(content)
        else:
            raise ValueError(f"Tipo de refactorización no soportado: {refactor_type}")
        
        file_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Archivo refactorizado ({refactor_type}): {path}")
        
        return {
            "success": True,
            "path": str(file_path),
            "refactor_type": refactor_type,
            "lines_changed": self._count_lines_changed(original_content, content)
        }
    
    async def search_and_replace(
        self,
        path: str,
        search: str,
        replace: str,
        use_regex: bool = False
    ) -> dict[str, Any]:
        """Buscar y reemplazar en archivo."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        if use_regex:
            content = re.sub(search, replace, content)
        else:
            content = content.replace(search, replace)
        
        file_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Buscar y reemplazar en: {path}")
        
        return {
            "success": True,
            "path": str(file_path),
            "lines_changed": self._count_lines_changed(original_content, content)
        }
    
    async def create_directory(self, path: str) -> dict[str, Any]:
        """Crear directorio."""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Directorio creado: {path}")
        
        return {
            "success": True,
            "path": str(dir_path)
        }
    
    async def delete_file(self, path: str) -> dict[str, Any]:
        """Eliminar archivo."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        file_path.unlink()
        
        logger.info(f"Archivo eliminado: {path}")
        
        return {
            "success": True,
            "path": str(file_path)
        }
    
    def _format_code(self, content: str, extension: str) -> str:
        """Formatear código."""
        if extension in [".py", ".pyw"]:
            try:
                import black
                return black.format_str(content, mode=black.FileMode())
            except ImportError:
                logger.warning("black no está instalado, retornando original")
                return content
        
        return content
    
    def _sort_imports(self, content: str) -> str:
        """Ordenar imports."""
        lines = content.split("\n")
        
        import_lines = []
        other_lines = []
        in_imports = False
        
        for line in lines:
            if line.startswith("import ") or line.startswith("from "):
                import_lines.append(line)
                in_imports = True
            elif in_imports and line.strip() == "":
                pass
            else:
                in_imports = False
                other_lines.append(line)
        
        import_lines.sort()
        
        return "\n".join(import_lines) + "\n" + "\n".join(other_lines)
    
    def _remove_unused(self, content: str) -> str:
        """Eliminar imports no usados."""
        import re
        
        imports = re.findall(r"^(?:from\s+\S+\s+import\s+\S+|import\s+\S+)", content, re.MULTILINE)
        
        used_names = set()
        for name in re.findall(r"\b\w+\b", content):
            used_names.add(name)
        
        used_imports = []
        for imp in imports:
            if "from " in imp:
                module = re.search(r"from\s+(\S+)", imp)
                names = re.search(r"import\s+(.+)", imp)
                if module and names:
                    names_list = [n.strip() for n in names.group(1).split(",")]
                    used_names_list = [n for n in names_list if n in used_names]
                    if used_names_list:
                        used_imports.append(f"from {module.group(1)} import {', '.join(used_names_list)}")
            else:
                name = imp.replace("import ", "").strip()
                if name.split(".")[0] in used_names:
                    used_imports.append(imp)
        
        content_without_imports = re.sub(r"^(?:from\s+\S+\s+import\s+\S+|import\s+\S+)\n?", "", content, flags=re.MULTILINE)
        
        return "\n".join(used_imports) + "\n\n" + content_without_imports.lstrip()
    
    def _count_lines_changed(self, original: str, modified: str) -> int:
        """Contar líneas modificadas."""
        original_lines = original.split("\n")
        modified_lines = modified.split("\n")
        
        changed = 0
        max_lines = max(len(original_lines), len(modified_lines))
        
        for i in range(max_lines):
            orig_line = original_lines[i] if i < len(original_lines) else None
            mod_line = modified_lines[i] if i < len(modified_lines) else None
            
            if orig_line != mod_line:
                changed += 1
        
        return changed
