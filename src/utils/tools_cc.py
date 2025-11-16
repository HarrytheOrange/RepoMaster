import os
import json
import subprocess
import glob
import re
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any, Annotated, Union
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import requests
from urllib.parse import quote_plus
from src.utils.audit_logger import log_event

# ============================================================================
# Base Classes and Types
# ============================================================================

class FileEditTool:
    """File editing tool that performs exact string replacements"""
    
    @staticmethod
    def edit(
        file_path: Annotated[str, "Absolute path to the file to modify"],
        old_string: Annotated[str, "The text to replace (must be unique unless replace_all=True)"],
        new_string: Annotated[str, "The text to replace it with (must be different from old_string)"],
        replace_all: Annotated[bool, "Replace all occurrences of old_string (default false)"] = False
    ) -> Annotated[str, "Edit result information with file snippet or error message"]:
        """
        Performs exact string replacements in files.

        Usage Rules:
        - Must read file with Read tool before editing
        - Preserve exact indentation as it appears in file
        - ALWAYS prefer editing existing files over creating new ones
        - Edit fails if old_string is not unique (unless replace_all=True)
        - Use replace_all for renaming variables across file
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"
            
            if old_string == new_string:
                return "Error: old_string and new_string are identical"
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_string exists
            if old_string not in content:
                return f"Error: The string to replace was not found in {file_path}"
            
            # Check for multiple occurrences if not replace_all
            occurrences = content.count(old_string)
            if not replace_all and occurrences > 1:
                return f"Error: Found {occurrences} matches of the string to replace. Use replace_all=True or add more context to make it unique."
            
            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
                replacements_made = occurrences
            else:
                new_content = content.replace(old_string, new_string, 1)
                replacements_made = 1
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Generate snippet around the modification
            lines = new_content.split('\n')
            # Structured audit log for edit
            try:
                log_event(
                    "tool_file_edit",
                    payload={
                        "tool_name": "FileEditTool.edit",
                        "file_path": file_path,
                        "replacements_made": replacements_made,
                        "replace_all": bool(replace_all),
                        "total_lines_after": len(lines),
                    },
                )
            except Exception:
                pass
            for i, line in enumerate(lines):
                if new_string in line:
                    start = max(0, i - 3)
                    end = min(len(lines), i + 4)
                    
                    snippet_lines = []
                    for j in range(start, end):
                        snippet_lines.append(f"{j+1:6}|{lines[j]}")
                    
                    replacement_info = f" ({replacements_made} replacement{'s' if replacements_made > 1 else ''} made)" if replace_all else ""
                    result = f"The file {file_path} has been updated{replacement_info}. Here's the result:\n"
                    result += '\n'.join(snippet_lines)
                    return result
            
            replacement_info = f" ({replacements_made} replacement{'s' if replacements_made > 1 else ''} made)" if replace_all else ""
            print(f"The file {file_path} has been updated successfully{replacement_info}.")
            return f"The file {file_path} has been updated successfully{replacement_info}."
            
        except Exception as e:
            return f"Error editing file: {str(e)}"

class WriteFileTool:
    """File creation tool for writing full content to a new or existing file"""
    
    @staticmethod
    def write(
        file_path: Annotated[str, "Absolute path to the file to create/write"],
        content: Annotated[str, "Full file content to write (UTF-8)"],
        overwrite: Annotated[bool, "Overwrite if file exists (default false)"] = False
    ) -> Annotated[str, "Write result information or error message"]:
        """
        Create a new file (or overwrite if allowed) with the provided content.
        
        Usage Rules:
        - Prefer this tool for first-time file creation
        - If the file already exists and overwrite is False, the write will fail
        - For incremental changes to existing files, use the Edit tool instead
        """
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            if os.path.exists(file_path) and not overwrite:
                return f"Error: File already exists: {file_path}. Use Edit tool or set overwrite=True."
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Return brief confirmation (avoid dumping full content)
            lines = content.split('\n')
            # Structured audit log for write
            try:
                log_event(
                    "tool_file_write",
                    payload={
                        "tool_name": "WriteFileTool.write",
                        "file_path": file_path,
                        "lines_written": len(lines),
                        "overwrite": bool(overwrite),
                    },
                )
            except Exception:
                pass
            preview = '\n'.join(lines[:10])
            suffix = "" if len(lines) <= 10 else f"\n... (total {len(lines)} lines)"
            return f"File written: {file_path}\nPreview:\n{preview}{suffix}"
        
        except Exception as e:
            return f"Error writing file: {str(e)}"
