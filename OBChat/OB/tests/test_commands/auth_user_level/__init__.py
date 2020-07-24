"""
This enables pytest assertion rewriting (detailed logs for why assertions failed) for this package.

See the pytest documentation on assertion & assertion rewriting for more information.
https://docs.pytest.org/en/stable/assert.html
https://docs.pytest.org/en/latest/writing_plugins.html#assertion-rewriting
"""

import pytest

pytest.register_assert_rewrite("OB.tests.test_commands.auth_user_level.apply")
pytest.register_assert_rewrite("OB.tests.test_commands.auth_user_level.create")
