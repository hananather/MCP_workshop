from fastmcp import FastMCP
from typing import List, Optional
import subprocess
import os

mcp = FastMCP("File Search Tools")

@mcp.tool
def search_files(query: str, path: Optional[str] = ".") -> dict:
    """Search for files containing a text query
    
    Args:
        query: The text to search for in files
        path: The directory path to search in (defaults to current directory)
    
    Returns:
        Dictionary containing list of matching files and count
    """
    command = ["grep", "-r", "-l", query, path]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout.strip():
        files = result.stdout.strip().split('\n')
    else:
        files = []
    
    return {
        "files": files,
        "count": len(files),
        "query": query,
        "search_path": path
    }

@mcp.tool
def search_files_with_context(query: str, path: Optional[str] = ".", lines_before: int = 2, lines_after: int = 2) -> List[dict]:
    """Search for files containing text and return matches with context
    
    Args:
        query: The text to search for in files
        path: The directory path to search in (defaults to current directory)
        lines_before: Number of lines to show before match
        lines_after: Number of lines to show after match
    
    Returns:
        List of dictionaries containing file, line number, and match context
    """
    command = ["grep", "-r", "-n", f"-B{lines_before}", f"-A{lines_after}", query, path]
    result = subprocess.run(command, capture_output=True, text=True)
    
    matches = []
    if result.stdout.strip():
        # Parse grep output to structure results
        current_file = None
        current_match = []
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('--'):
                # Separator between matches
                if current_file and current_match:
                    matches.append({
                        "file": current_file,
                        "context": "\n".join(current_match)
                    })
                    current_match = []
            else:
                # Extract filename from grep output
                if ':' in line:
                    parts = line.split(':', 2)
                    if len(parts) >= 2:
                        current_file = parts[0]
                        current_match.append(line)
        
        # Add last match if exists
        if current_file and current_match:
            matches.append({
                "file": current_file,
                "context": "\n".join(current_match)
            })
    
    return matches

@mcp.tool
def find_files_by_name(pattern: str, path: Optional[str] = ".") -> List[str]:
    """Find files by name pattern using shell find command
    
    Args:
        pattern: The file name pattern to search for (supports wildcards)
        path: The directory path to search in (defaults to current directory)
    
    Returns:
        List of file paths matching the pattern
    """
    command = ["find", path, "-name", pattern, "-type", "f"]
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.stdout.strip():
        return result.stdout.strip().split('\n')
    return []

if __name__ == "__main__":
    mcp.run()