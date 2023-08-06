# compr - handy comparing and matching

Handy wrappers to compare/match objects with extra conditions.

Comparator objects bind value(s) AND compare logic into single item.
Similarly to pytest.approx(...)

This allows comfortable code for assertions, filters, dispatchers etc.

Human readable `__repr__` is also available!

> NOTE: Examples below are purely synthetic to illustrate usage scenarios.

## Example 0:
```
# Assert actual value is greater than 5
>>> import compr
>>> expected = compr.gt(5)  # gt stands for greater than as in __gt__
>>> actual = 3
>>> assert expected == actual, f'{actual=} does not match {expected=}'
```

## Example 1: A function to validate HTTP response object attributes
```
>>> dir(response)
['status', 'headers', 'body', 'body_len'] # int, dict, str, int respectively

# Simple validator with parateters may look like:

>>> def validate(response, **kwargs):
>>>     """
>>>     Check if all given kwargs equal to response attributes
>>>     """
>>>     for k, v in kwargs.items():
>>>         if getattr(response, k) == v:
>>>             continue
>>>         else:
>>>             raise AssertionError(k, v)
```

Usage (check if status is 200 and body is 'asdf'):
```
>>> validate(response, status=200, body='asdf')
```

Now let's expand our requirements. Check if:
* body_len is between 300 and 400 bytes (inclusive)
* status code is < 206.

Pushing compare logic into validator will eventually overwhelm it with complex
code, arguments or even magic.

Instead we may keep method above unchanged and use comparators:
```
>>> from compr import lt, within  # less-than, fits-range
>>> validate(response, status=lt(206), body_len=within(300, 400))
```

Now when validator tries to `==` status, it will check if its less-than 206.
Similarly with `==` body_len, it will check if it fits into range [300..400].

Profit!

Few more steps make things even prettier:

```
>>> from compr import kwargs2cmp
>>>
>>> def validate(response, **kwargs):
>>>     for k, v in kwargs2cmp(kwargs):  # arg name parsing kicks in here
>>>     # allow kwargs to be interpreted as
>>>     # <argument-name>_<compare-logic>=<expected-value>
>>>         if getattr(response, k) == v:
>>>             continue
>>>         else:
>>>             raise AssertionError(k, v)
```

And usage becomes even simpler:
```
>>> validate(response, status_lt=206, body_len_within=[300, 400])
```

After more refactoring validate becomes (see all_attrs doc for help):

```
from complr import all_attrs

def validate(response, **kwargs):
        if not all_attrs(response, kwargs2cmp(kwargs)):
            raise AssertionError(response, kwargs)
```

## Creating Your own comparator object:
```
@compr.comparator
def almost_equal(val, other):
    return 0.9*val < other < 1.1*val
```
