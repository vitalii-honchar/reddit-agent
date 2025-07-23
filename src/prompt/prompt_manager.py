from pathlib import Path
from typing import Dict, Optional


class PromptManager:
    """Manages loading and caching of prompt templates."""
    
    def __init__(self, prompt_folder: Path):
        """Initialize the prompt manager with the base prompt folder path."""
        self.prompt_folder = Path(prompt_folder)
        self._cache: Dict[str, str] = {}
    
    def load_prompt(self, prompt_name: str, subfolder: Optional[str] = None) -> str:
        """
        Load a prompt from the prompts folder.
        
        Args:
            prompt_name: Name of the prompt file (without .md extension)
            subfolder: Optional subfolder within the prompts directory
            
        Returns:
            The prompt content as a string
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
            ValueError: If the prompt file is empty
        """
        # Build cache key
        cache_key = f"{subfolder}/{prompt_name}" if subfolder else prompt_name
        
        # Return cached version if available
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build file path
        if subfolder:
            prompt_path = self.prompt_folder / subfolder / f"{prompt_name}.md"
        else:
            prompt_path = self.prompt_folder / f"{prompt_name}.md"
        
        # Check if file exists
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        # Load and cache the prompt
        try:
            content = prompt_path.read_text(encoding="utf-8").strip()
            if not content:
                raise ValueError(f"Prompt file is empty: {prompt_path}")
            
            self._cache[cache_key] = content
            return content
            
        except Exception as e:
            raise ValueError(f"Failed to read prompt file {prompt_path}: {e}")
    
    def clear_cache(self) -> None:
        """Clear the prompt cache."""
        self._cache.clear()
    
    def get_cached_prompts(self) -> Dict[str, str]:
        """Get all cached prompts."""
        return self._cache.copy()