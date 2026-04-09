"""Herramienta para revisión de código."""

from pathlib import Path
from typing import Any
import re

from ..utils.logger import get_logger

logger = get_logger()


class CodeReviewerTool:
    """Herramienta para analizar y revisar código."""
    
    def __init__(self):
        self.name = "code_reviewer"
        self.description = "Herramienta para análisis de código y detección de bugs"
    
    def list_tools(self) -> list[dict[str, Any]]:
        """Listar herramientas disponibles."""
        return [
            {
                "name": "analyze_file",
                "description": "Analizar archivo de código",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "checks": {"type": "array", "description": "Lista de verificaciones: complexity, security, style, performance"}
                }
            },
            {
                "name": "find_issues",
                "description": "Encontrar issues en el código",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "severity": {"type": "string", "description": "Severidad: error, warning, info, all", "default": "all"}
                }
            },
            {
                "name": "generate_report",
                "description": "Generar reporte de revisión",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"},
                    "format": {"type": "string", "description": "Formato: markdown, json, text", "default": "markdown"}
                }
            },
            {
                "name": "check_security",
                "description": "Verificar seguridad del código",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"}
                }
            },
            {
                "name": "check_complexity",
                "description": "Verificar complejidad del código",
                "parameters": {
                    "path": {"type": "string", "description": "Ruta del archivo"}
                }
            }
        ]
    
    async def analyze_file(
        self,
        path: str,
        checks: list[str] | None = None
    ) -> dict[str, Any]:
        """Analizar archivo de código."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        
        if checks is None:
            checks = ["complexity", "security", "style", "performance"]
        
        results = {
            "file": str(file_path),
            "size": len(content),
            "lines": content.count("\n") + 1,
            "checks": {}
        }
        
        for check in checks:
            if check == "complexity":
                results["checks"]["complexity"] = self._check_complexity(content)
            elif check == "security":
                results["checks"]["security"] = self._check_security(content)
            elif check == "style":
                results["checks"]["style"] = self._check_style(content, file_path.suffix)
            elif check == "performance":
                results["checks"]["performance"] = self._check_performance(content)
        
        logger.info(f"Archivo analizado: {path}")
        
        return results
    
    async def find_issues(
        self,
        path: str,
        severity: str = "all"
    ) -> list[dict[str, Any]]:
        """Encontrar issues en el código."""
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        
        content = file_path.read_text(encoding="utf-8")
        
        issues = []
        
        issues.extend(self._find_syntax_errors(content))
        issues.extend(self._find_style_issues(content))
        issues.extend(self._find_security_issues(content))
        issues.extend(self._find_performance_issues(content))
        
        if severity != "all":
            issues = [i for i in issues if i["severity"] == severity]
        
        logger.info(f"Issues encontrados en {path}: {len(issues)}")
        
        return issues
    
    async def generate_report(
        self,
        path: str,
        format: str = "markdown"
    ) -> str:
        """Generar reporte de revisión."""
        analysis = await self.analyze_file(path)
        issues = await self.find_issues(path)
        
        file_path = Path(path)
        
        if format == "markdown":
            return self._generate_markdown_report(analysis, issues, file_path.name)
        elif format == "json":
            import json
            return json.dumps({"analysis": analysis, "issues": issues}, indent=2)
        else:
            return self._generate_text_report(analysis, issues)
    
    async def check_security(self, path: str) -> dict[str, Any]:
        """Verificar seguridad del código."""
        return await self.analyze_file(path, checks=["security"])
    
    async def check_complexity(self, path: str) -> dict[str, Any]:
        """Verificar complejidad del código."""
        return await self.analyze_file(path, checks=["complexity"])
    
    def _check_complexity(self, content: str) -> dict[str, Any]:
        """Verificar complejidad del código."""
        lines = content.split("\n")
        
        max_line_length = max(len(line) for line in lines) if lines else 0
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        
        function_count = len(re.findall(r"\bdef\s+\w+", content))
        class_count = len(re.findall(r"\bclass\s+\w+", content))
        
        return {
            "max_line_length": max_line_length,
            "avg_line_length": round(avg_line_length, 2),
            "function_count": function_count,
            "class_count": class_count,
            "total_lines": len(lines)
        }
    
    def _check_security(self, content: str) -> dict[str, Any]:
        """Verificar issues de seguridad."""
        issues = []
        
        patterns = [
            (r"password\s*=\s*['\"].*['\"]", "Hardcoded password"),
            (r"api_key\s*=\s*['\"].*['\"]", "Hardcoded API key"),
            (r"secret\s*=\s*['\"].*['\"]", "Hardcoded secret"),
            (r"eval\s*\(", "Use of eval()"),
            (r"exec\s*\(", "Use of exec()"),
            (r"__import__\s*\(", "Dynamic import"),
        ]
        
        for pattern, description in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append({
                    "type": description,
                    "count": len(matches)
                })
        
        return {
            "issues": issues,
            "is_secure": len(issues) == 0
        }
    
    def _check_style(self, content: str, extension: str) -> dict[str, Any]:
        """Verificar estilo del código."""
        issues = []
        
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i} too long ({len(line)} chars)")
            
            if line.endswith(" ") or line.endswith("\t"):
                issues.append(f"Line {i} has trailing whitespace")
        
        return {
            "issues": issues,
            "compliant": len(issues) == 0
        }
    
    def _check_performance(self, content: str) -> dict[str, Any]:
        """Verificar issues de rendimiento."""
        issues = []
        
        patterns = [
            (r"for\s+.*\s+in\s+range\(len\(", "Use enumerate() instead of range(len())"),
            (r"\.append\(.*\)\s*in\s+.*for", "Consider list comprehension"),
            (r"^\s*\+\=\s*", "String concatenation in loop (use join())"),
        ]
        
        for pattern, suggestion in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                issues.append({
                    "type": suggestion,
                    "count": len(matches)
                })
        
        return {
            "issues": issues,
            "suggestions": len(issues) == 0
        }
    
    def _find_syntax_errors(self, content: str) -> list[dict[str, Any]]:
        """Encontrar errores de sintaxis."""
        issues = []
        
        patterns = [
            (r"^\s*def\s+\w+\s*\([^)]*\s*:", "Missing parenthesis in function definition"),
            (r"^\s*class\s+\w+\s*[^:]*$", "Missing colon in class definition"),
            (r"^\s*if\s+.*\s*[^:]$", "Missing colon in if statement"),
            (r"^\s*for\s+.*\s*[^:]$", "Missing colon in for loop"),
            (r"^\s*while\s+.*\s*[^:]$", "Missing colon in while loop"),
        ]
        
        for pattern, description in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                issues.append({
                    "type": "syntax_error",
                    "severity": "error",
                    "message": description,
                    "line": content[:content.find(match)].count("\n") + 1
                })
        
        return issues
    
    def _find_style_issues(self, content: str) -> list[dict[str, Any]]:
        """Encontrar issues de estilo."""
        issues = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    "type": "style",
                    "severity": "warning",
                    "message": f"Line too long ({len(line)} chars)",
                    "line": i
                })
            
            if line.endswith(" ") or line.endswith("\t"):
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "message": "Trailing whitespace",
                    "line": i
                })
        
        return issues
    
    def _find_security_issues(self, content: str) -> list[dict[str, Any]]:
        """Encontrar issues de seguridad."""
        issues = []
        
        patterns = [
            (r"password\s*=\s*['\"].*['\"]", "hardcoded_password", "error"),
            (r"api_key\s*=\s*['\"].*['\"]", "hardcoded_api_key", "error"),
            (r"secret\s*=\s*['\"].*['\"]", "hardcoded_secret", "error"),
            (r"eval\s*\(", "use_of_eval", "warning"),
            (r"exec\s*\(", "use_of_exec", "warning"),
        ]
        
        for pattern, issue_type, severity in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                issues.append({
                    "type": issue_type,
                    "severity": severity,
                    "message": f"Found {issue_type.replace('_', ' ')}",
                    "line": line_num
                })
        
        return issues
    
    def _find_performance_issues(self, content: str) -> list[dict[str, Any]]:
        """Encontrar issues de rendimiento."""
        issues = []
        
        patterns = [
            (r"for\s+\w+\s+in\s+range\(len\(", "Use enumerate() instead of range(len())", "warning"),
            (r"\.append\(.*\)\s*for\s+", "Consider list comprehension", "info"),
        ]
        
        for pattern, description, severity in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                issues.append({
                    "type": "performance",
                    "severity": severity,
                    "message": description,
                    "line": line_num
                })
        
        return issues
    
    def _generate_markdown_report(
        self,
        analysis: dict[str, Any],
        issues: list[dict[str, Any]],
        filename: str
    ) -> str:
        """Generar reporte en formato markdown."""
        report = f"# Code Review Report: {filename}\n\n"
        
        report += "## Summary\n\n"
        report += f"- **File**: {analysis['file']}\n"
        report += f"- **Size**: {analysis['size']} bytes\n"
        report += f"- **Lines**: {analysis['lines']}\n\n"
        
        if "checks" in analysis:
            report += "## Checks\n\n"
            
            if "complexity" in analysis["checks"]:
                report += "### Complexity\n\n"
                comp = analysis["checks"]["complexity"]
                report += f"- Max line length: {comp['max_line_length']}\n"
                report += f"- Avg line length: {comp['avg_line_length']}\n"
                report += f"- Functions: {comp['function_count']}\n"
                report += f"- Classes: {comp['class_count']}\n\n"
            
            if "security" in analysis["checks"]:
                report += "### Security\n\n"
                sec = analysis["checks"]["security"]
                report += f"- **Secure**: {'Yes' if sec['is_secure'] else 'No'}\n"
                if sec["issues"]:
                    for issue in sec["issues"]:
                        report += f"  - {issue['type']}: {issue['count']}\n"
                report += "\n"
        
        if issues:
            report += "## Issues\n\n"
            for issue in issues:
                report += f"- **{issue['severity'].upper()}** (Line {issue['line']}): {issue['message']}\n"
        
        return report
    
    def _generate_text_report(
        self,
        analysis: dict[str, Any],
        issues: list[dict[str, Any]]
    ) -> str:
        """Generar reporte en formato texto."""
        report = f"Code Review Report\n"
        report += f"==================\n\n"
        
        report += f"File: {analysis['file']}\n"
        report += f"Size: {analysis['size']} bytes\n"
        report += f"Lines: {analysis['lines']}\n\n"
        
        if "checks" in analysis:
            report += "Checks\n------\n\n"
            
            if "complexity" in analysis["checks"]:
                comp = analysis["checks"]["complexity"]
                report += f"Complexity:\n"
                report += f"  Max line length: {comp['max_line_length']}\n"
                report += f"  Avg line length: {comp['avg_line_length']}\n"
                report += f"  Functions: {comp['function_count']}\n"
                report += f"  Classes: {comp['class_count']}\n\n"
        
        if issues:
            report += "Issues\n------\n\n"
            for issue in issues:
                report += f"[{issue['severity'].upper()}] Line {issue['line']}: {issue['message']}\n"
        
        return report
