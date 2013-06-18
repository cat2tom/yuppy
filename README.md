## Yuppy
#### Python Programming for the Privileged Class
-----

_Yuppy is released under the [MIT License](http://opensource.org/licenses/MIT)._

Yuppy is a small library that integrates seamlessly with Python to promote
data integrity by adding common object-oriented language features to
Python applications. It intends to provide fully integrated support for
interfaces, encapsulation and built-in member validation - features that
are commonly found in other object-oriented languages - in a manner that
preserves much of the dynamic nature of Python. While this library should
certainly not always be used when developing with Python, it can improve
the integrity of your data and the stability of your code without
comprimising usability.

_I have heard and understand the arguments against encapsulation in Python.
Virtually all Python variables are public in some sense. But I do believe
there is a time and a place for these features, and I learned a lot about the
language in writing this library. Yuppy should be used responsibly,
meaning some features should not be used in libraries with a significant
user base. That said, many Yuppy features - such as duck-typing based
interfaces, constant attributes, and abstract and final classes - can be
very useful within the context of a dynamic language. Be mindful of your
users and of the language when using Yuppy._

### Table of contents
-------------------
1. [Introduction](#but-encapsulation-is-bad)
1. [A Complete Example](#a-complete-example)
1. [Class Decorators](#class-decorators)
   * [Encapsulation](#encapsulate)
   * [Abstract Classes](#abstract)
   * [Final Classes](#final)
1. [Member Decorators](#member-decorators)
   * [Abstract Attributes](#abstract-2)
   * [Variable Attributes](#variable)
   * [Constant Attributes](#constant)
   * [Method Attributes](#method)
   * [Public Attributes](#public)
   * [Protected Attributes](#protected)
   * [Private Attributes](#private)
   * [Static Attributes](#static)
   * [Type Validation](#type-validation)
1. [Interfaces](#interfaces)
   * [Interfaces](#interface)
   * [Implements](#implements)
   * [Type Checking](#instanceof)

##### _"But encapsulation is bad!"_
But options are good. Sure, Python is a dynamic language, and often its
flexibility can be used to creatively conquer complex problems (indeed,
Yuppy was developed using many of these features). But lax access
restrictions are not _always_ beneficial. Yuppy can help protect the
integrity of your data by preventing important internal instance data
from being changed.

##### _"What about the type checking then!?"_
Sure, duck typing often allows for more flexibility for users of libaries.
But without the proper precautions a lack of type checking can ultimately
lead to unpredictable code. What if some code somewhere is changing your
FTP class's `port` attribute to an invalid string? You won't find out
about it until your code tries to connect to the FTP server. By that
time, it can be hard to tell where that bad port number came from. Yuppy
can automatically type check class or instance variables _at the point
at which they are set_ to ensure that your data is not corrupted.

### A Complete Example
Yuppy is easy to use, implementing common object-oriented programming
features in a manner that is consistent with implementations in other
languages, making for more clear, concise, and reliable code.

With Yuppy, you do not have to extend a special base class. Simply use
the `encapsulate` decorator on any class. Internally, Yuppy wraps the class,
returning a child of the class that protects internal class members.
Sure, there's a way around everything in Python, but Yuppy goes to
a long way towards protecting internal object data, and circumventing
the Yuppy API would be more work than it's worth.

```python
# When importing yuppy.*, the following decorators will be imported:
# encapsulate, variable/var, constant/const, method, public, protected,
# private, static, final, interface, implements, and instanceof.
from yuppy import *

# Use the 'encapsulate' decorator to decorate the class.
@encapsulate
class Apple(object):
  """An abstract apple."""
  # Instance attributes can be automatically validated.
  weight = private(float)

  def __init__(self, weight):
    self.weight = weight

  @protected
  def get_weight(self):
    return self.weight

  @protected
  def set_weight(self, weight):
    self.weight = weight

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, self.weight)

@encapsulate
class GreenApple(Apple):
  """A green apple."""
  color = const('green')

  def __init__(self, weight):
    # Green apples are .5 lbs heavier on average.
    self.override_weight(weight+.5)

  @private
  def override_weight(self, weight):
    return self.set_weight(weight)

  @public
  def get_weight(self):
    return self.weight

  @public
  def get_color(self):
    return self.color

# Interface definitions are simply classes that implement normal methods.
@interface
class AppleTreeInterface(object):
  """An apple tree interface."""
  def add_apple(self, apple):
    """Adds an apple to the tree."""

  def count_apples(self):
    """Returns the number of apples on the tree."""

# Interface implementations can be validated using either duck-typing
# or strict implementation-based validation. In this case we actually
# implement the interface, but even without implementing the interface,
# this class would pass validation via yuppy.instanceof based on the
# fact that it contains the required interface methods.
@encapsulate
@implements(AppleTreeInterface)
class AppleTree(object):
  """An apple tree."""
  apples = protected(list)

  def __init__(self):
    self.apples = []

  @protected
  def clear_apples(self):
    self.apples = []

  @public
  def add_apple(self, apple):
    self.apples.append(apple)
    return self

  @public
  def count_apples(self):
    return len(self.apples)

@interface
class GreenAppleTreeInterface(AppleTreeInterface):
  """A green apple tree interface."""
  def pick_apple(self):
    """Picks an apple from the tree."""

@encapsulate
@implements(GreenAppleTreeInterface)
class GreenAppleTree(AppleTree):
  """A green apple tree."""
  @public
  def add_apple(self, apple):
    if apple.color != 'green':
      raise ValueError("%s apples cannot be added to the green apple tree." % (apple.color,))

  @public
  def pick_apple(self):
    return self.apples.pop()
```

#### Testing the example
```
>>> apple = Apple('two')
AttributeError: Invalid attribute value for 'weight'.
>>> apple = Apple(2.0)
>>> apple.set_weight(2.5)
AttributeError: Cannot access protected Apple object member 'set_weight'.
>>> apple.get_weight()
AttributeError: Cannot access protected Apple object member 'get_weight'.
>>> GreenApple.color
'green'
>>> greenapple = GreenApple(2.0)
>>> greenapple.color
'green'
>>> greenapple.color = 'red'
AttributeError: Cannot override GreenApple object constant 'color'.
>>> greenapple.weight
AttributeError: GreenApple object has not attribute 'weight'.
>>> greenapple.get_weight()
2.5
>>> greenapple.set_weight()
AttributeError: Cannot access protected GreenApple object member 'set_weight'.
>>> tree = GreenAppleTree()
>>> len(tree.apples)
AttributeError: Cannot access protected GreenAppleTree object member 'apples'.
>>> tree.count_apples()
0
>>> tree.apples.append(GreenApple(1.0))
AttributeError: Cannot access protected GreenAppleTree object member 'apples'.
>>> tree.add_apple(GreenApple(1.0))
>>> tree.pick_apple()
GreenApple(1.0)
```

## Class Decorators
Yuppy primarily uses decorators to decorate classes and thus hide
otherwise public class attributes.

### encapsulate
Declares a class definition to be encapsulated.

```
encapsulate(cls)
```

_This decorator is required in order to encapsulate class members._
Calling this decorator will cause the given class to be dynamically
extended by a class that monitors instance attribute access. Internally,
the wrapper class exposes Python's magic `__getattribute__`, `__setattr__`,
and `__delattr__` methods to prevent protected or private attributes
from being accessed.

##### Example
```python
@encapsulate
class Apple(object):
  color = const('red')
  weight = private(float)

  @public
  def get_weight(self):
    return self.weight
```

### abstract
Creates an abstract class.

```
abstract(cls)
```

Abstract classes are classes that cannot themselves be instantiates, but
can be extended and instantiated.

##### Example
```python
from yuppy import *

@abstract
class Apple(object):
  """An abstract apple."""
  weight = protected(float)

  def get_weight(self):
    return self.weight

  def set_weight(self, weight):
    self.weight = weight

class GreenApple(Apple):
  """A concrete green apple."""
```

We will be able to create instances of `GreenApple`, which inherits from
`Apple`, but any attempts to instantiate an `Apple` will result in a
`TypeError`.

```
>>> apple = GreenApple()
>>> apple.set_weight(1.0)
>>> apple.get_weight()
1.0
>>> apple = Apple()
TypeError: Cannot instantiate abstract class 'Apple'.
```

### final
Declares a class definition to be final.

The final Yuppy decorator is, well, `final`, which allows users to define
classes that _cannot be extended._ This is a common feature in several
other object-oriented languages.
```
final(cls)
```

##### Example

```python
from yuppy import *

@final
class Apple(object):
  weight = private(float, default=None)
```

```
>>> apple = Apple()
>>> class GreenApple(Apple):
...   pass
...
TypeError: ...
```

## Member Decorators

### abstract
Creates an abstract method.
```
abstract(method)
```

Abstract methods can be applied to *any* python class, even without
declaring the class to be abstract. This means that if the method is
not re-defined in a child class, an `AttributeError` will be raised if
the abstract method is accessed. Therefore, it is strongly recommended
that any class that contains abstract methods be declared abstract.

##### Example
```python
from yuppy import *

@abstract
class Apple(object):
  """An abstract apple."""
  @abstract
  def get_color(self):
    """Gets the apple color."""
```

Once we've defined an abstract class, we can extend it and override the
abstract methods.

```
>>> class GreenApple(object):
...   def get_color(self):
...     return 'green'
...
>>> apple = GreenApple()
>>> apple.get_color()
'green'
```

Note what happens if we try to use abstract methods or fail to override them.

```
>>> class GreenApple(object):
...   pass
...
>>> # We can still instantiate green apples since the class isn't declared abstract.
>>> apple = GreenApple()
>>> # But we can't access the get_color() method.
>>> apple.get_color()
AttributeError: Cannot access abstract 'GreenApple' object member 'bar'.
```

### variable
Creates a public variable attribute.
```
variable([default=None[, validate=None[, *types]]])
var([default=None[, validate=None[, *types]]])
```

##### Example
```python
from yuppy import *

@encapsulate
class Apple(object):
  foo = var(int, default=None, validate=lambda x: x == 1)
```

```
>>> apple = Apple()
```

### constant
Creates a public constant attribute.

Constants are attributes which have a permanent value. They can be used for
any value which should never change within the application, such as an
application port number, for instance. With Yuppy we can use the `const`
decorator to create a constant, passing a single permanent value to the
constructor.
```
constant(value)
const(value)
```

##### Example
```python
from yuppy import *

@encapsulate
class RedApple(object):
  color = const('red')
```

Note that while the class constant can be overridden, the instance constant
will not change regardless of the class constant value.

```
>>> RedApple.color
'red'
>>> apple = RedApple()
>>> apple.color
'red'
>>> RedApple.color = 'blue'
>>> RedApple.color
'blue'
>>> apple.color
'red'
>>> apple = RedApple()
>>> apple.color
'red'
>>> apple.color = 'blue'
AttributeError: Cannot override Apple object constant 'color'.
```

### method
Creates a public method attribute.
```
method(callback)
```

##### Example
```python
from yuppy import *

@encapsulate
class Apple(object):
  color = private(default='red')

  @method
  def getcolor(self):
    return self.color
```

```
>>> apple = Apple()
>>> apple.getcolor()
'red'
```

### public
Creates a public attribute.

All class members are naturally public in Python. Therefore, Yuppy's
`public` decorator is generally used simply for readability.

Note that if an attribute (`var`, `const`, or `method`) is not passed as the
first argument, this decorator will create a public `method` if the argument
is a `FunctionType`, or `var` otherwise.
```
public([value=None[, default=None[, validate=None[, *types]]]])
```

##### Example
```python
from yuppy import *

@encapsulate
class Apple(object):
  """An abstract apple."""
  # The two following lines result in the exact same property.
  foo = var(int)
  bar = public(validate=lambda x: isinstance(x, int))

  @public
  def baz(self):
    return self.bar
```

### protected
Creates a protected attribute.

Protected members are variables that can be accessed only from within a
class or a sub-class of the declaring class. Thus, while protected
members have more relaxed access restriction, values are still hidden
from outside users. With Yuppy we can use the `protected` decorator to
declare any class member protected.

Note that if an attribute (`var`, `const`, or `method`) is not passed as
the first argument, this decorator will create a protected `method` if
the argument is a `FunctionType`, or `var` otherwise.
```
protected([value=None[, default=None[, validate=None[, *types]]]])
```

##### Example

```python
from yuppy import *

@encapsulate
class Apple(object):
  """An abstract apple."""
  weight = private(float, default=None)

  def __init__(self, weight):
    self.weight = weight

  @protected
  def _get_weight(self):
    return self.weight

@encapsulate
class GreenApple(Apple):
  """A green apple."""
  @public
  def get_weight(self):
    return self._get_weight()
```

With this interface, we can access `Apple.weight` through `GreenApple.get_weight()`.
This is because `GreenApple` has access to the `Apple._get_weight()` method
which subsequently has access to the private `Apple.weight` attribute.

```
>>> apple = GreenApple(2.5)
>>> apple.weight
AttributeError: GreenApple object has not attribute 'weight'.
>>> apple._get_weight()
AttributeError: Cannot access protected GreenApple object member '_get_weight'.
>>> apple.get_weight()
2.5
```

### private
Creates a private attribute.

Private members are variables that can only be accessed from within a class.
They support data integrity by preventing class users from altering internal attribute.
With Yuppy we can decorate any class member with `private` to hide it from outside access.
Note that Yuppy variables must be defined within the class definition, not
arbitrarily defined within class code. This is common in other object-oriented
languages as well.

Note that if an attribute (`var`, `const`, or `method`) is not passed as the
first argument, this decorator will create a private `method` if the argument
is a `FunctionType`, or `var` otherwise.
```
private([value=None[, default=None[, validate=None[, *types]]]])
```

##### Example

```python
from yuppy import *

@encapsulate
class Apple(object):
  """An abstract apple."""
  weight = private(float, default=None)

  def __init__(self, weight):
    self.weight = weight

  @private
  def _get_weight(self):
    return self.weight

  def get_weight(self):
    return self._get_weight()
```

Now, if we create a new `Apple` instance and try to access its attributes
from outside the class we will fail. However, we'll see that access from
within the class works just fine.

```
>>> apple = Apple(2.5)
>>> apple.weight
AttributeError: Cannot access private Apple object member 'weight'.
>>> apple._get_weight()
AttributeError: Cannot access private Apple object member '_get_weight'.
>>> apple.get_weight()
2.5
```

### static
Creates a static attribute.

Static Yuppy members are equivalent to standard Python class members. This is
essentially the same parallel that exists between Python's class members
and static variables in many other object-oriented languages. With Yuppy we
can use the `static` decorator to create static methods or properties. Note
that `static` members can be further decorated with `public`, `private`,
or `protected`.

Note that if an attribute (`var`, `const`, or `method`) is not passed as
the first argument, this decorator will create a public static `method`
if the argument is a `FunctionType`, or `var` otherwise.
```
static([value=None[, default=None[, validate=None[, *types]]]])
```

##### Example

```python
from yuppy import *

@encapsulate
class Apple(object):
  """An abstract apple."""
  weight = static(float, default=None)
```

With static members, changes to a member variable will be applied to
all instances of the class. So, even after instantiating a new instance
of the class, the `weight` attribute value will remain the same.

```
>>> apple1 = Apple()
>>> apple1.weight
None
>>> apple1.weight = 2.0
>>> apple1.weight
2.0
>>> apple2 = Apple()
>>> apple2.weight
2.0
```

### Type Validation
Yuppy can perform direct type checking and arbitrary execution of validation
callbacks. When a mutable Yuppy attribute is set, validators will automatically
be executed. This ensures that values are validated at the time they're
set rather than when they're accessed.

Any `var` type can perform data validation. When creating a new `var`,
we can pass either `<type>` or `validate=<func>` to the object
constructor.

##### Example

```python
from yuppy import *

@encapsulate
class Apple(object):
  """An abstract apple."""
  weight = var(float)

  def __init__(self, weight):
    self.weight = weight
```

Now, if we create an `Apple` instance we can see how the validation works.
Note that if an improper value is passed to the constructor, the validator
will automatically try to cast it to the correct type if only one type
is provided.

```
>>> apple = Apple(1)
>>> apple = Apple('one')
AttributeError: Invalid attribute value for 'weight'.
```

Note also that instance variable type checking is integrated with the
Yuppy interface system. This means that an interface can be passed to
any variable definition as the `type` argument, and Yuppy will validate
variable values based on duck typing. This can be very useful within the
context of the Python programming language.

## Interfaces
Interfaces are a partcilarly useful feature with Python. Since Python
promotes duck typing, Yuppy interfaces can be used to ensure that any
object walks and talks like a duck. For this reason, Yuppy interface
evaluation supports both explicit interface implementation checks _and_
implicit interface implementation checks, or duck typing.

### interface
Declares a class definition to be an interface.

```
interface(cls)
```

Abstract interface attributes are declared by simply creating them. Yuppy
will evaluate the interface for any public attributes and consider those
to be required of any implementing classes.

##### Example

```python
from yuppy import *

@interface
class AppleInterface(object):
  """An apple interface."""
  def get_color(self):
    """Returns the apple color."""

  def get_weight(self):
    """Returns the apple weight."""
```

### implements
Declares a class definition to implement an interface.

When a class implements an interface, it must define all abstract attributes
of that interface. Yuppy will automatically evaluate the class definition
to ensure it conforms to the indicated interface.

##### Example
Continuing with the previous example, we can implement the `AppleInterface`
interface.

```
>>> @implements(AppleInterface)
... class Apple(object):
...   """An apple."""
...
TypeError: 'Apple' definition missing attribute 'get_color' from 'AppleInterface' interface.
```

Note that if we don't implement the `AppleInterface` attributes a `TypeError`
will be raised. Let's try that again.

```
>>> @implements(AppleInterface)
... class Apple(object):
...   """An apple."""
...   color = const('red')
...   weight = const(2.0)
...   def get_color(self):
...     """Returns the apple color."""
...     return self.color
...   def get_weight(self):
...     """Returns the apple weight."""
...     return self.weight
...
>>> apple = Apple()
>>> apple.get_color()
'red'
```

### instanceof
Determines whether an instance's class implements an interface.

```
implements(instance, interface[, ducktype=True])
```

Finally, it's important that we be able to evaluate objects for adherence
to any interface requirements. The `instanceof` function behaves similarly
to Python's built-in `isinstance` function, but for Yuppy interfaces.
However, _Yuppy's implementation can also evaluate interface implementation
based on duck typing._ This means that object classes do not necessarily
have to implement a specific interface, they simply need to behave in the
manner that the interface requires.

```
>>> from yuppy import instanceof
>>> apple = Apple()
>>> instanceof(apple, AppleInterface)
True
>>> instanceof(apple, AppleInterface, False)
True
>>> instanceof(apple, Apple)
True
```

_Copyright (c) 2013 Jordan Halterman_
