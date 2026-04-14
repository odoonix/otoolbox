# Odoo Test Framework Comprehensive Guide

## Overview
Odoo uses a custom testing framework based on Python's `unittest` module. It provides sophisticated test orchestration, database transaction management, and test discovery mechanisms. Tests are run through the Odoo CLI server command.

---

## 1. Test Runner Entry Points

### Main Entry Point
- **Path:** `/home/maso/Projects/18.0/odoo/odoo/odoo-bin`
- **Command:** `./odoo-bin` (uses `odoo.cli.main()`)

### Test Execution Flow
```
odoo-bin → odoo.cli.main() → server.run() → Service/Loader
```

### Test Running Through Server
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/service/server.py`

When `test_enable` flag is set or `test_file` is provided, tests are executed via:
```python
from odoo.tests import loader
suite = loader.make_suite(module_names, 'at_install')  # or 'post_install'
results = loader.run_suite(suite, global_report=registry._assertion_report)
```

### Key Test Loading Functions
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/loader.py`

```python
def make_suite(module_names, position='at_install'):
    """Creates a test suite for specified modules

    - Filters by position ('at_install' or 'post_install')
    - Applies test tag filtering
    - Returns OdooSuite with sorted tests
    """

def run_suite(suite, global_report=None):
    """Executes the test suite

    - Marks module.current_test and threading.testing
    - Uses OdooTestResult for result tracking
    - Handles test retry logic
    """
```

---

## 2. Test Discovery Patterns

### Module Test Discovery
**Pattern:** Tests must be in `{module}/tests/test_*.py` files

**Example paths:**
```
odoo/addons/base/tests/
├── __init__.py
├── test_ir_model.py
├── test_orm.py
├── test_res_users.py
└── test_res_partner.py
```

### Test Class Discovery
- **Pattern:** Classes must inherit from `TransactionCase`, `SingleTransactionCase`, `BaseCase`, or `HttpCase`
- **Method Discovery:** All methods starting with `test_` are discovered as test methods
- **Loader:** `get_module_test_cases(module)` in `loader.py` yields individual test instances

### Test Methods
- **Format:** `def test_<name>(self):`
- **Special Methods:** `setUpClass()` and `setUp()` run before tests

---

## 3. Test Base Classes and Inheritance

### Class Hierarchy
```
unittest.TestCase (Python stdlib)
    ↓
case.TestCase (Odoo customized)
    ↓
BaseCase (Odoo-specific features)
    ├── TransactionCase
    ├── SingleTransactionCase
    └── HttpCase → TransactionCase
```

### BaseCase
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/common.py` line 931

**Features:**
- `self.env` - Odoo environment with current user
- `self.registry` - Database registry
- `self.cr` - Database cursor
- `self.uid` - Current user ID
- Custom assertion methods (assertQueryCount, assertRecordValues, etc.)
- Automatic HTTP request blocking (external requests forbidden)
- Retry mechanism for flaky tests (via `ODOO_TEST_FAILURE_RETRIES` env var)

**Key Methods:**
```python
def ref(self, xid):
    """Get database ID by XML ID"""
    return self.browse_ref(xid).id

def browse_ref(self, xid):
    """Get record by XML ID"""
    return self.env.ref(xid)

def with_user(self, login):
    """Context manager to switch user temporarily"""

def patch(self, obj, key, val):
    """Patch object attribute with automatic cleanup"""

def assertQueryCount(self, default=0, **counters):
    """Count and verify SQL queries executed"""
```

### TransactionCase
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/common.py` line 1163

**Characteristics:**
- Each test method runs in a **savepoint** within a single transaction
- Transaction is rolled back after each test (no commits)
- Common setup in `setUpClass()` runs once for all test methods
- Data from `setUpClass()` is shared across all test methods
- **Best for:** Tests requiring database setup

**Savepoint Management:**
```python
# Automatic in setUp():
self.cr.execute('SAVEPOINT test_%d' % self._savepoint_id)
# Automatic rollback in tearDown()
self.cr.execute('ROLLBACK TO SAVEPOINT test_%d' % self._savepoint_id)
```

### SingleTransactionCase
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/common.py` line 1171

**Characteristics:**
- All test methods run in the **same transaction**
- Transaction rolls back only after all tests complete
- No savepoints per test
- **Best for:** Tests that are independent and don't need isolation

### HttpCase
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/common.py` line 2119

**Characteristics:**
- Extends `TransactionCase`
- Provides browser automation via Chrome headless
- HTTP request testing
- JavaScript execution in browser context

**Usage:**
```python
class TestWeb(HttpCase):
    def test_tour(self):
        self.start_tour('/web', 'web_tour_name')

    def test_javascript(self):
        self.browser_js('/path', 'console.log("test")',
                        ready='document.readyState === "complete"')
```

---

## 4. Test Configuration and Tags

### Test Tags System
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/tag_selector.py`

**Default Tags** (auto-assigned by MetaCase):
- `'standard'` - Normal tests
- `'at_install'` - Run when module is installed
- Module name - Automatically added

**Tag Decorator:**
```python
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestPostInstall(TransactionCase):
    """Runs only after module installation"""
    pass

@tagged('post_install', '-at_install', 'performance')
class TestPerformance(TransactionCase):
    """Custom tag for performance tests"""
    pass
```

**Tag Filtering Syntax:**
```
-tag          # Exclude tag
tag           # Include tag (requires 'standard' unless specified)
*             # All tests (overrides 'standard' default)
/module.py    # Specific module
:ClassName    # Specific test class
.method_name  # Specific test method
```

### Command-Line Test Execution

```bash
# Run all standard tests at install time
./odoo-bin -c config.conf --test-enable -d mydb

# Run specific tags
./odoo-bin -c config.conf --test-enable --test-tags=post_install -d mydb

# Run all tests (not just standard)
./odoo-bin -c config.conf --test-enable --test-tags='*' -d mydb

# Run specific module tests
./odoo-bin -c config.conf --test-enable --test-tags=base -d mydb

# Run specific test class
./odoo-bin -c config.conf --test-enable --test-tags=base:TestRules -d mydb
```

### Configuration Parameters

**Environment Variables:**
```bash
ODOO_TEST_FAILURE_RETRIES=2  # Retry flaky tests N times
ODOO_BROWSER_CPU_THROTTLING=2  # Slow down browser tests 2x
ODOO_BROWSER_BIN=/path/to/chrome  # Custom Chrome binary
```

**Config File Settings:**
```ini
[odoo]
test_enable = True
test_file = addons/module/tests/test_file.py
test_tags = post_install,-standard
```

---

## 5. Test Decorators and Patterns

### @tagged Decorator
```python
from odoo.tests import tagged

@tagged('post_install', '-at_install', 'custom_tag')
class MyTest(TransactionCase):
    pass

# On individual test methods:
@tagged('slow')
def test_slow_operation(self):
    pass
```

### @skipIf and @skip
```python
from unittest import skip, skipIf

@skip("Not implemented yet")
def test_future_feature(self):
    pass

@skipIf(not hasattr(module, 'feature'), "Feature not available")
def test_conditional(self):
    pass
```

### Retry Behavior
```python
# Disable retry for a specific test
def test_no_retry(self):
    self._retry = False

# Disable retry for a method
test_method._retry = False
```

### Freeze Time
```python
from odoo.tests.common import freeze_time

@freeze_time('2023-01-01 12:00:00')
class TimeTests(TransactionCase):
    def test_with_frozen_time(self):
        # All tests in class run with frozen time
        pass

# Or as context manager:
def test_context(self):
    with freeze_time('2023-01-01'):
        # Code here runs with frozen time
        pass
```

---

## 6. Custom Test Runners and Results

### OdooTestResult
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/result.py`

Customized from `unittest.TestResult`:
```python
class OdooTestResult:
    - failures_count: int
    - errors_count: int
    - testsRun: int
    - skipped: int
    - stats: defaultdict(Stat)  # Performance stats per test
    - shouldStop: bool

    def total_errors_count()
    def startTest(test)
    def stopTest(test)
    def addError(test, err)
    def addFailure(test, err)
    def addSkip(test, reason)
```

### Test Statistics
Each test tracks:
- Execution time
- Number of SQL queries executed
- Query execution time

**Accessed via:**
```python
result.stats[test.id()] = Stat(time=..., queries=...)
```

### OdooSuite
**Location:** `/home/maso/Projects/18.0/odoo/odoo/odoo/tests/suite.py`

Handles:
- Test sequencing
- Per-module and per-class setup/teardown
- Transaction management at module/class level

---

## 7. Example Test Files Structure

### Example 1: Basic TransactionCase
**Path:** `/home/maso/Projects/18.0/odoo/odoo/odoo/addons/test_access_rights/tests/test_ir_rules.py`

```python
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger
from odoo import Command

class TestRules(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # One-time setup for all test methods
        ObjCateg = cls.env['test_access_right.obj_categ']
        cls.categ = ObjCateg.create({'name': 'Food'})

        # Create access rules
        cls.env['ir.rule'].create({
            'name': 'Forbid negatives',
            'model_id': cls.env.ref('...').id,
            'domain_force': "[('val', '>', 0)]"
        })

    @mute_logger('odoo.addons.base.models.ir_rule')
    def test_basic_access(self):
        # Each test runs in a savepoint
        allowed = self.categ.with_env(self.env(user=self.env.ref('base.public_user')))
        with self.assertRaises(AccessError):
            allowed.read(['name'])

    def test_group_rule(self):
        # Another isolated test
        pass
```

### Example 2: Tagged Tests with Retry
**Path:** `/home/maso/Projects/18.0/odoo/odoo/odoo/addons/base/tests/test_test_retry.py`

```python
from odoo.tests import BaseCase, TransactionCase, tagged

@tagged('test_retry', 'test_retry_success')
class TestRetry(TransactionCase):
    def test_retry_success(self):
        # This test can be retried if it fails
        self.assertEqual(1, 1)

    @tagged('slow')
    def test_slow_operation(self):
        # Custom tag on method
        import time
        time.sleep(1)
        self.assertTrue(True)

    @tagged('-standard', 'performance')
    def test_performance(self):
        # Skipped by default unless explicitly included
        self.assertQueryCount(admin=5)
```

### Example 3: Assert Query Count
```python
def test_query_optimization(self):
    # Verify exact number of queries
    with self.assertQueryCount(42):
        records = self.env['model'].search([...])
        for record in records:
            _ = record.field_name

    # Different counts per user
    with self.assertQueryCount(admin=3, demo=5):
        self.env['model'].search([...])
```

### Example 4: Record Value Assertions
```python
def test_record_values(self):
    record1 = self.env['model'].create({'name': 'Test', 'value': 10})
    record2 = self.env['model'].create({'name': 'Test2', 'value': 20})

    self.assertRecordValues([record1, record2], [
        {'name': 'Test', 'value': 10.0, 'active': True},
        {'name': 'Test2', 'value': 20.0, 'active': True},
    ])
```

---

## 8. Configuration Files

### No pytest.ini
Odoo does not use pytest. It uses its own custom test runner.

### setup.cfg
**Path:** `/home/maso/Projects/18.0/odoo/odoo/setup.cfg`

Contains only flake8 configuration, not test configuration:
```ini
[install]
optimize=1

[flake8]
extend-exclude = .git, .tx, debian, doc, setup
```

### Tox Configuration
No `tox.ini` found - Odoo doesn't use tox for testing.

---

## 9. Test Execution Workflow

### Phase 1: Test Discovery
1. Loader calls `get_test_modules(module_name)`
2. Finds all `test_*.py` files in `{module}/tests/`
3. For each test module, `get_module_test_cases()` yields test instances

### Phase 2: Tag Filtering
1. `TagsSelector` evaluates `--test-tags` parameter
2. Includes/excludes tests based on tags
3. Supports complex selectors: `post_install,-standard,/module:Class.method`

### Phase 3: Test Execution
1. `OdooSuite` organizes tests by module/class
2. Per-module setup runs once
3. Per-class `setUpClass()` runs once for all methods in class
4. For each test method:
   - `setUp()` creates savepoint
   - Test method executes
   - Savepoint rolled back in tearDown
5. `OdooTestResult` tracks failures, errors, stats

### Phase 4: Results
- Test statistics logged to `odoo.tests.stats`
- Failures written to standard output
- Exit code reflects success/failure

---

## 10. Performance Testing Features

### Query Counting
```python
def test_query_count(self):
    with self.assertQueryCount(default=5, admin=3, demo=7):
        # Count queries by user
        self.env['model'].search([...])

    # Or assert queries contain specific patterns
    with self.assertQueriesContain(['SELECT', 'FROM model']):
        self.env['model'].search([...])
```

### Profiling
```python
def test_with_profiling(self):
    with self.profile(description='test description'):
        self.env['model'].search([...])
```

### Warm vs Cold Phase
- `self.warm = False` during warmup phase
- `self.warm = True` during normal execution
- Useful for skipping strict assertions during warmup

---

## 11. Key Files Reference

| File | Purpose |
|------|---------|
| `/odoo-bin` | Main entry point |
| `odoo/tests/__init__.py` | Package initialization |
| `odoo/tests/common.py` | BaseCase, TransactionCase, HttpCase, decorators |
| `odoo/tests/case.py` | Custom TestCase (unittest override) |
| `odoo/tests/loader.py` | Test discovery and suite creation |
| `odoo/tests/suite.py` | OdooSuite for test organization |
| `odoo/tests/result.py` | OdooTestResult for tracking results |
| `odoo/tests/tag_selector.py` | Tag filtering logic |
| `odoo/cli/server.py` | Server command that triggers tests |
| `odoo/service/server.py` | Service layer that runs tests |
| `odoo/modules/loading.py` | Module loading with test execution |

---

## 12. Running Tests Programmatically

```python
from odoo.tests import loader

# Create test suite
suite = loader.make_suite(['base', 'web'], position='at_install')

# Run suite
results = loader.run_suite(suite)

# Check results
print(f"Tests run: {results.testsRun}")
print(f"Failures: {results.failures_count}")
print(f"Errors: {results.errors_count}")
print(f"Skipped: {results.skipped}")
```

---

## Summary

Odoo's test framework is a sophisticated, custom implementation built on `unittest` with:
- **Custom test runners** for database transaction management
- **Automatic test discovery** from `tests/test_*.py` modules
- **Advanced tag filtering** for selective test execution
- **Performance tracking** with query counting and profiling
- **Browser automation** via Chrome headless
- **Savepoint-based isolation** for TransactionCase tests
- **Automatic retry** for flaky tests via environment variable

Tests are primarily executed via the `./odoo-bin` server command with `--test-enable` flag and tag filtering via `--test-tags`.
