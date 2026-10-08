from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

from pydantic import BaseModel, ConfigDict


class TemplateImportSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    allow_text_growth: bool = True
    replace_visuals: bool = True
    flexible_grouping: bool = True


_import_settings: ContextVar[TemplateImportSettings] = ContextVar(
    "template_import_settings", default=TemplateImportSettings()
)


def get_template_import_settings() -> TemplateImportSettings:
    return _import_settings.get()


@contextmanager
def template_import_settings(settings: TemplateImportSettings) -> Iterator[None]:
    """Scope options to one request and its copied generation worker contexts."""
    token = _import_settings.set(settings)
    try:
        yield
    finally:
        _import_settings.reset(token)
