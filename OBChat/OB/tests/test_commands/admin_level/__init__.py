"""
This enables pytest assertion rewriting (detailed logs for why assertions failed) for this package.

See the pytest documentation on assertion and assertion rewriting for more information.
https://docs.pytest.org/en/stable/assert.html
https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting
"""

import pytest

pytest.register_assert_rewrite("OB.tests.test_commands.admin_level.ban")
pytest.register_assert_rewrite("OB.tests.test_commands.admin_level.kick")
pytest.register_assert_rewrite("OB.tests.test_commands.admin_level.lift_ban")
