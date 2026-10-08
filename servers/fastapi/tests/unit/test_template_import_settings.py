import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context

import pytest

from templates.v2.import_settings import (
    TemplateImportSettings,
    get_template_import_settings,
    template_import_settings,
)


def test_import_settings_restore_after_failure():
    with pytest.raises(RuntimeError):
        with template_import_settings(TemplateImportSettings(allow_text_growth=False)):
            assert not get_template_import_settings().allow_text_growth
            raise RuntimeError("generation failed")
    assert get_template_import_settings() == TemplateImportSettings()


def test_concurrent_requests_and_copied_workers_keep_their_own_options():
    async def run_request(settings):
        with template_import_settings(settings):
            await asyncio.sleep(0)
            with ThreadPoolExecutor(max_workers=1) as executor:
                result = executor.submit(copy_context().run, get_template_import_settings).result()
            return result

    async def run():
        return await asyncio.gather(
            run_request(TemplateImportSettings(replace_visuals=False)),
            run_request(TemplateImportSettings(flexible_grouping=False)),
        )

    assert asyncio.run(run()) == [
        TemplateImportSettings(replace_visuals=False),
        TemplateImportSettings(flexible_grouping=False),
    ]
    assert get_template_import_settings() == TemplateImportSettings()
