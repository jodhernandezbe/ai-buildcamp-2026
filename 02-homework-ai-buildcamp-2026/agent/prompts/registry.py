from dataclasses import dataclass
from pathlib import Path
from string import Template

import frontmatter

TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptNotFoundError(KeyError):
    pass


@dataclass(frozen=True)
class Prompt:
    """A prompt template with its metadata. Variables are written as `$name`."""

    name: str
    template: str
    version: int
    description: str

    def render(self, **variables: str) -> str:
        """Substitute `$variables`; raises KeyError if one is missing (use `$$` for a literal `$`)."""
        return Template(self.template).substitute(variables)


class PromptRegistry:
    """Loads versioned Markdown prompts (with YAML front matter) from a directory.

    Prompts live in `.md` files rather than Python strings so they can be reviewed,
    diffed and edited without touching code.
    """

    def __init__(self, directory: Path = TEMPLATES_DIR):
        self._directory = directory
        self._cache: dict[str, Prompt] = {}

    def names(self) -> list[str]:
        return sorted(path.stem for path in self._directory.glob("*.md"))

    def get(self, name: str) -> Prompt:
        if name not in self._cache:
            self._cache[name] = self._load(name)
        return self._cache[name]

    def _load(self, name: str) -> Prompt:
        # Resolve through the known file list so a name can never escape the directory.
        if name not in self.names():
            raise PromptNotFoundError(f"Unknown prompt {name!r}. Available: {self.names()}")
        post = frontmatter.load(self._directory / f"{name}.md")
        return Prompt(
            name=name,
            template=post.content,
            version=int(post.metadata.get("version", 1)),
            description=str(post.metadata.get("description", "")),
        )
