# VikunjaWorker Task Filtering Logic Verification

## Step 6: Test VikunjaWorker task filtering logic

### Verification Date
2026-03-23

### Verification Summary
✅ VikunjaWorker task filtering logic tested and verified successfully

### Detailed Verification Results

#### 1. Task Filtering Implementation
The `_filter_tasks_by_tag` method filters tasks based on label requirements:
- Filters tasks by matching label titles (case-insensitive)
- Handles edge cases: missing labels, None labels, empty labels list
- Preserves original task order
- Returns empty list for empty input

#### 2. Test Coverage Added
Added comprehensive tests covering the following scenarios:

- ✅ **test_keeps_tasks_with_matching_label**: Verifies tasks with matching labels are kept
- ✅ **test_removes_tasks_without_matching_label**: Verifies tasks without matching labels are removed
- ✅ **test_case_insensitive_match**: Verifies label matching is case-insensitive
- ✅ **test_no_labels_field**: Verifies tasks without labels field are filtered out
- ✅ **test_none_labels_field**: Verifies tasks with None labels are filtered out
- ✅ **test_mixed_tasks**: Verifies correct filtering of mixed task lists

New comprehensive tests added:
- ✅ **test_empty_task_list**: Verifies empty task list returns empty result
- ✅ **test_empty_labels_list**: Verifies tasks with empty labels list are filtered out
- ✅ **test_label_with_empty_string_title**: Verifies labels with empty titles are filtered out
- ✅ **test_multiple_labels_with_different_cases**: Verifies tasks with multiple labels in different cases are matched
- ✅ **test_tag_name_with_different_cases**: Verifies tag name matching works with different cases
- ✅ **test_preserves_task_order**: Verifies task order is preserved after filtering

#### 3. Test Results
- ✅ All 12 task filtering tests pass
- ✅ All 45 VikunjaWorker tests pass
- ✅ All 331 project tests pass
- ✅ All linting checks pass (black, isort, flake8)
- ✅ All security checks pass (safety, bandit)

#### 4. Integration with Worker Workflow
The task filtering is used in the `run` method at line 124:
```python
tasks = self._filter_tasks_by_tag(tasks, settings.github_issue_worker_required_label)
```

This ensures only tasks with the required label are processed.

#### 5. Edge Cases Handled
- Empty task list → Returns []
- Tasks without labels field → Filtered out
- Tasks with None labels → Filtered out
- Tasks with empty labels list → Filtered out
- Labels with empty string titles → Filtered out
- Multiple labels with varying case → Correctly matched
- Tag name with different cases → Correctly matched
- Task order → Preserved

#### 6. Configuration
- Required label: "ai" (from settings.github_issue_worker_required_label)
- Matching is case-insensitive
- Original task order is preserved after filtering

### Test Statistics

| Test Category | Total Tests | Passing |
|--------------|-------------|---------|
| Task Filtering Tests | 12 | 12 ✅ |
| VikunjaWorker Tests | 45 | 45 ✅ |
| Project Tests | 331 | 331 ✅ |
| Linting Checks | 3 | 3 ✅ |
| Security Checks | 2 | 2 ✅ |

### Code Changes
- Modified: tests/test_vikunja_worker.py
  - Added 6 new comprehensive test methods
  - Total lines added: 50
  - All existing tests continue to pass

### Implementation Details

The `_filter_tasks_by_tag` method implementation (lines 459-478 in vikunja_worker.py):
```python
def _filter_tasks_by_tag(self, tasks: List[Dict[str, Any]], tag_name: str) -> List[Dict[str, Any]]:
    """Filter tasks to only those whose labels contain a label with a matching title.

    Args:
        tasks: List of task dictionaries from Vikunja
        tag_name: Tag title to filter by (case-insensitive)

    Returns:
        List of tasks that have the specified tag
    """
    tag_lower = tag_name.lower()
    filtered = []
    for task in tasks:
        labels = task.get("labels") or []
        label_titles = [label.get("title", "").lower() for label in labels]
        if tag_lower in label_titles:
            filtered.append(task)
        else:
            self.logger.info(f"Skipping task #{task.get('id')} '{task.get('title')}': missing tag '{tag_name}'")
    return filtered
```

### Conclusion
The VikunjaWorker task filtering logic is working correctly and comprehensively tested. All edge cases are handled properly, the implementation is robust, and all tests pass successfully. The filtering correctly identifies tasks with the required label and handles various edge cases gracefully.
