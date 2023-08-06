# Django Legate

Simple to django guardian, but defines user permissions for models based on some general relation.

For example: Company -> Blog post. Add a `blog.change_post` permission to User+Company to add an ability for user to edit all companies block posts.

## Installation

```sh
pip install px-django-legate
```

Depends on: [px-django-combinable-groups](https://pypi.org/project/px-django-combinable-groups/).

In `settings.py`:

```python
INSTALLED_APPS += [
  # ...
  'django.contrib.auth',
  # ...
  # Depends on:
  'pxd_tree.adjacency_list',
  'pxd_combinable_groups',
  'pxd_legate',
]

PXD_LEGATE = {
  # Will automatically add content types to admin interface.
  'ADMIN_REGISTER_CONTENT_TYPE': True,
  # Will automatically add permissions to admin interface.
  'ADMIN_REGISTER_PERMISSION': True,
}
```

## Usage

### Assign permissions

```python
from pxd_legate.services import assigner
from pxd_combinable_groups.services import permissions_collector


# To add additional access capabilities to user for some "root" objects:
accesses = assigner.add_access(
  # User identifier
  user.id,
  # Any number of objects to add access to
  [company_1, company_2],
  # List of additional permissions to add. Optional.
  permission_ids=permissions_collector.keys_to_ids((
    'blog.view_post', 'blog.change_post'
  )),
  # You may also add groups, not only the permissions. Optional.
  group_ids=[1, 2, 3],
)

# Opposite to adding access, you may also partially withdraw it:
accesses = assigner.withdraw_access(
  user.id,
  [company_1],
  permission_ids=[4, 5], # Optional
  group_ids=None, # Optional
)

# To completely remove user access to some root object there is `remove_access`
# method:
assigner.remove_access(user.id, [company_2])

# This method sets user permissions "strictly" to a provided values:
accesses = assigner.set_access(
  user.id,
  [company_1],
  # Whatever the permissions user had before, now he will have only a
  # 'blog.view_post' permission.
  # Optional. But be careful! Passing an empty list `[]` will remove
  # all permissions at all. Only `None` will tell method that there is
  # no need to do something with `permission_ids`.
  permission_ids=permissions_collector.keys_to_ids(['blog.view_post']),
  # Same as for `permission_ids` goes here.
  # With such a value we removing groups from access object entirely.
  group_ids=[],
  # For such value groups wil stay untouched.
  group_ids=None,
)
```

**Be careful!** Method `set_access` optional parameters are optional only if they're `None`. Empty list `[]` is also a value. Check comments higher.

### Check permissions

Checker service provides `Checker` class. You will need to create separate checker class for every model your'e going to check access for.

```python
from pxd_legate.services import checker
from pxd_combinable_groups.services import permissions_collector


posts_checker = checker.Checker(
  # Model for what your'e going to check user's access.
  Post,
  # Full path to a root object to check access against.
  'department__company',
  # Root model to check access info. Optional.
  root_model=Company,
  # Special comparator object. Instance of `checker.CheckCMP`.
  # It will be used to compare passed permission_ids with existing ones.
  # There are 2 built in:
  # - `checker.ALL_CMP` - User must have all permission_ids.
  # - `checker.ANY_CMP` - User must have any of provided permission_ids.
  cmp=checker.ALL_CMP,
  # Determines whether the user personal permissions should be checked.
  # So in case of user has it's own permission not to add additional
  # check mechanics into the query.
  # It's `True` by default, but there might be cases when there is no such
  # check required.
  should_check_global=True,
)

# To check whether the user can do something with some object:
can_edit = posts_checker.for_object(
  # Object to check access to.
  some_post,
  # User.
  user,
  # Permission ids to check user's abilities. Optional.
  permission_ids=permissions_collector.keys_to_ids(['blog.change_post']),
  # For cases with a different comparison method you may provide a custom
  # comparator. Event without `permission_ids` at all.
  cmp=None,
)

# QuerySet can also be filtered base on the user's ability to do
# something with it:
only_editable = posts_checker.for_queryset(
  # QuerySet to filter.
  Post.objects.all(),
  # User.
  user,
  # Permission ids to check user's abilities. Optional.
  permission_ids=permissions_collector.keys_to_ids(['blog.change_post']),
  # For cases with a different comparison method you may provide a custom
  # comparator. Event without `permission_ids` at all.
  cmp=None,
  # It will be passed to a `with_annotation` method(see next).
  annotation_field_name=None,
)
```

Underneath the `for_queryset` method checker uses `with_annotation`.
It could be used for more complex situations.
For example some model has two root models, where user access can be defined.

```python
posts_department_checker = checker.Checker(
  Post, 'department', root_model=Department,
)
company_field, query = posts_checker.with_annotation(
  Post.objects.all(),
  user,
  permission_ids=permissions_collector.keys_to_ids(['blog.change_post']),
  cmp=None,
  # Name of the field that check annotation will be inserted into.
  # Could be empty. In that case it will be auto-generated.
  annotation_field_name=None,
)
department_field, query = posts_department_checker.with_annotation(
  # Query from above will again be "checked".
  query,
  user,
  permission_ids=permissions_collector.keys_to_ids(['blog.change_post']),
)

only_editable = query.filter(
  # It has access through the company.
  models.Q(**{company_field: True})
  | # Or
  # Through it's department.
  models.Q(**{department_field: True})
)
```

### Access manual change

If your going to change `ObjectAccess` manually then after that you must gather actual permissions that it has.

In Administration panel it's already done.

There is a simple service for that:

```python
from pxd_legate.services import gatherer

any_object = ObjectAccess.objects.first()

# Some changes happening...

gatherer.gather_object_accesses(
  # You should gather accesses in bulk. It's faster.
  [any_object]
)
```

## TODO

- [_] - Checkers registry for dynamic queryset and objects access control.
