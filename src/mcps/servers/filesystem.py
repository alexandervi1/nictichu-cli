"""MCP Server para operaciones de filesystem."""

from pathlib import Path
from typing import Any

from ..client import MCPClient
from ...utils.logger import get_logger

logger = get_logger()


class FileSystemMCPClient(MCPClient):
    """Cliente MCP para operaciones de sistema de archivos."""
    
    def __init__(self, server_name: str, config: dict[str, Any] | None = None):
        super().__init__(server_name, config)
        self.allowed_paths: list[Path] = []
    
    async def connect(self) -> bool:
        """Conectar al servidor filesystem."""
        try:
            allowed_dirs = self.config.get("allowed_directories", ["."])
            
            self.allowed_paths = []
            for dir_path in allowed_dirs:
                path = Path(dir_path).expanduser().resolve()
                if path.exists():
                    self.allowed_paths.append(path)
            
            self.session = True
            logger.info(f"Filesystem MCP conectado con {len(self.allowed_paths)} rutas permitidas")
            return True
        except Exception as e:
            logger.error(f"Error conectando filesystem MCP: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Desconectar del servidor filesystem."""
        self.session = None
        self.allowed_paths.clear()
        logger.info("Filesystem MCP desconectado")
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "read_file",
                "description": "Leer contenido de un archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"}
                }
            },
            {
                "name": "write_file",
                "description": "Escribir contenido a un archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "content": {"type": "string", "description": "Contenido a escribir"}
                }
            },
            {
                "name": "list_directory",
                "description": "Listar contenido de un directorio",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del directorio"}
                }
            },
            {
                "name": "create_directory",
                "description": "Crear un directorio",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del directorio"}
                }
            },
            {
                "name": "delete_file",
                "description": "Eliminar un archivo",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"}
                }
            },
            {
                "name": "file_exists",
                "description": "Verificar si un archivo existe",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"}
                }
            }
        ]
    
    def _resolve_path(self, path: str) -> Path | None:
        """Resolver y validar ruta."""
        try:
            resolved = Path(path).expanduser().resolve()
            
            for allowed in self.allowed_paths:
                try:
                    resolved.relative_to(allowed)
                    return resolved
                except ValueError:
                    continue
            
            logger.warning(f"Ruta no permitida: {path}")
            return None
        except Exception as e:
            logger.error(f"Error resolviendo ruta {path}: {e}")
            return None
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Ejecutar herramienta de filesystem."""
        if not await self.is_connected():
            raise RuntimeError("Cliente filesystem no conectado")
        
        handlers = {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "create_directory": self._create_directory,
            "delete_file": self._delete_file,
            "file_exists": self._file_exists,
        }
        
        handler = handlers.get(tool_name)
        if handler is None:
            raise ValueError(f"Herramienta no soportada: {tool_name}")
        
        return await handler(arguments)
    
    async def _read_file(self, args: dict[str, Any]) -> str:
        """Leer archivo."""
        path = self._resolve_path(args["path"])
        if path is None:
            raise PermissionError(f"Ruta no permitida: {args['path']}")
        
        if not path.is_file():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        return path.read_text(encoding="utf-8")
    
    async def _write_file(self, args: dict[str, Any]) -> bool:
        """Escribir archivo."""
        path = self._resolve_path(args["path"])
        if path is None:
            raise PermissionError(f"Ruta no permitida: {args['path']}")
        
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args["content"], encoding="utf-8")
        
        logger.info(f"Archivo escrito: {path}")
        return True
    
    async def _list_directory(self, args: dict[str, Any]) -> list[str]:
        """Listar directorio."""
        path = self._resolve_path(args["path"])
        if path is None:
            raise PermissionError(f"Ruta no permitida: {args['path']}")
        
        if not path.is_dir():
            raise NotADirectoryError(f"No es un directorio: {path}")
        
        return [str(p) for p in path.iterdir()]
    
    async def _create_directory(self, args: dict[str, Any]) -> bool:
        """Crear directorio."""
        path = self._resolve_path(args["path"])
        if path is None:
            raise PermissionError(f"Ruta no permitida: {args['path']}")
        
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio creado: {path}")
        return True
    
    async def _delete_file(self, args: dict[str, Any]) -> bool:
        """Eliminar archivo."""
        path = self._resolve_path(args["path"])
        if path is None:
            raise PermissionError(f"Ruta no permitida: {args['path']}")
        
        path.unlink()
        logger.info(f"Archivo eliminado: {path}")
        return True
    
    async def _file_exists(self, args: dict[str, Any]) -> bool:
        """Verificar si existe archivo."""
        path = self._resolve_path(args["path"])
        if path is None:
            return False
        
        return path.exists()
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """Listar recursos."""
        return [
            {"uri": f"file://{p}", "name": str(p)}
            for p in self.allowed_paths
        ]
    
    async def read_resource(self, uri: str) -> Any:
        """Leer recurso."""
        if not uri.startswith("file://"):
            raise ValueError(f"URI no soportada: {uri}")
        
        path_str = uri[7:]
        return await self._read_file({"path": path_str})
