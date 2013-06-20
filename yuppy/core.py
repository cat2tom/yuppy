# Copyright (c) 2013 Jordan Halterman
# See LICENSE for details.
from types import FunctionType, MethodType
import inspect

def isattribute(obj):
  """
  Returns a boolean value indicating whether an object is an attribute.
  """
  return isinstance(obj, Attribute)

def abstract(obj):
  """
  Makes a class or method abstract.
  """
  if inspect.isclass(obj):
    obj.__abstract__ = True
    return obj
  else:
    if isinstance(obj, FunctionType):
      return AbstractMethod(obj)
    raise TypeError("Invalid abstract attribute %s." % (obj,))

def isabstract(obj):
  """
  Returns a boolean value indicating whether an object is abstract.
  """
  if hasattr(obj, '__dict__'):
    return obj.__dict__.get('__abstract__', False)
  else:
    return getattr(obj, '__abstract__', False)

def final(obj):
  """
  Makes a class or method final.
  """
  if inspect.isclass(obj):
    obj.__final__ = True
    return obj
  else:
    if isinstance(obj, FunctionType):
      return FinalMethod(obj)
    raise TypeError("Invalid final attribute %s." % (obj,))

def isfinal(obj):
  """
  Returns a boolean value indicating whether an object is final.
  """
  return getattr(obj, '__final__', False)

class Attribute(object):
  """
  A basic attribute.
  """
  __name__ = None

class Constant(Attribute):
  """
  A constant attribute.
  """
  def __init__(self, value):
    self.__value__ = value

  def __get__(self, instance=None, owner=None):
    """Returns the constant value."""
    return self.__value__

  def __set__(self, instance, value):
    """Raises an attribute error when an attempt is made to override the constant value."""
    raise AttributeError("Cannot override constant value.")

  def __del__(self, instance):
    """Raises an attribute error when an attempt is made to delete the constant value."""
    raise AttributeError("Cannot delete constant value.")

class Variable(Attribute):
  """
  A variable attribute.
  """
  def __init__(self, *args, **kwargs):
    if len(args) == 0:
      self.__type__ = None
    elif len(args) == 1:
      if not isinstance(args[0], (list, tuple)):
        self.__type__ = (args[0],)
      else:
        self.__type__ = args[0]
    else:
      self.__type__ = args
    try:
      kwargs['default']
    except KeyError:
      self.__hasdefault__ = False
      self.__default__ = None
    else:
      self.__hasdefault__ = True
      self.__default__ = kwargs['default']
    try:
      self.__validate__ = kwargs['validate']
    except KeyError:
      self.__validate__ = None
    try:
      self.__interface__ = kwargs['interface']
    except KeyError:
      self.__interface__ = None
    super(Variable, self).__init__()

  def _validate(self, value):
    """
    Validates a value.
    """
    if self.__interface__ is not None and not instanceof(value, self.__interface__):
      raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
    if self.__type__ is not None and not isinstance(value, self.__type__):
      if not isinstance(self.__type__, (list, tuple)):
        try:
          value = self.__type__(value)
        except TypeError:
          raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
        except ValueError:
          raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
        else:
          return value
      else:
        raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
    if self.__validate__ is not None:
      if not self.__validate__(value):
        raise AttributeError("Invalid attribute value for '%s'." % (self.__name__,))
    return value

  def __get__(self, instance=None, owner=None):
    """Gets the variable value."""
    try:
      return instance.__dict__[self.__name__]
    except KeyError:
      if self.__hasdefault__:
        return self.__default__
      else:
        raise AttributeError("'%s' object has no attribute '%s'." % (instance.__class__.__name__, self.__name__))
    except AttributeError:
      raise AttributeError("Instance member '%s' cannot be accessed from the class scope." % (self.__name__,))

  def __set__(self, instance, value):
    """Sets the variable value."""
    try:
      instance.__dict__[self.__name__]
    except AttributeError:
      raise AttributeError("Instance member '%s' cannot be accessed from the class scope." % (self.__name__,))
    else:
      instance.__dict__[self.__name__] = self._validate(value)

  def __del__(self, instance=None):
    """Sets the variable value to None."""
    if instance is not None:
      try:
        instance.__dict__[self.__name__] = None
      except AttributeError:
        raise AttributeError("Instance member '%s' cannot be accessed from the class scope." % (self.__name__,))

class Method(Attribute):
  """
  A method attribute.
  """
  def __init__(self, method):
    self.__method__ = method

  def __get__(self, instance=None, owner=None):
    return self.__method__

class AbstractMethod(Method):
  """
  An abstract method attribute.
  """
  def __init__(self, method):
    self.__abstract__ = True
    super(AbstractMethod, self).__init__(method)

  def __get__(self, instance=None, owner=None):
    raise AttributeError("Cannot call abstract method %s." % (self.__method__.__name__,))

class FinalMethod(Method):
  """
  A final method attribute.
  """
  def __init__(self, method):
    self.__final__ = True
    super(FinalMethod, self).__init__(method)

class StaticType(type):
  """
  A base yuppy static type.
  """
  def _findattr(cls, attrname, *args):
    for base in cls.__mro__:
      try:
        return base.__dict__[attrname]
      except KeyError:
        continue

    if len(args) > 0:
      return args[0]
    else:
      raise AttributeError("Attribute not found.")

  @property
  def __attributes__(cls):
    attrs = {}
    for base in cls.__mro__:
      for attrname, attr in base.__dict__.items():
        if attrname not in attrs and isattribute(attr):
          attrs[attrname] = attr
    return attrs

  def __getattr__(cls, name):
    """Supports accessing attributes via class calls."""
    attr = cls._findattr(name, None)
    if isattribute(attr):
      return getattr(cls, name)
    return super(StaticType, cls).__getattr__(name, value)

  def __setattr__(cls, name, value):
    """Prevents overriding explicitly set attributes."""
    if isinstance(name, basestring) and not (name.startswith('__') and name.endswith('__')):
      if isattribute(cls._findattr(name, None)):
        raise TypeError("Cannot override '%s' attribute '%s' by assignment." % (cls.__name__, name))
    super(StaticType, cls).__setattr__(name, value)

  def __delattr__(cls, name):
    """Prevents deleting explicitly set attributes."""
    if isinstance(name, basestring) and not (name.startswith('__') and name.endswith('__')):
      if isattribute(cls._findattr(name, None)):
        raise TypeError("Cannot delete '%s' attribute '%s'." % (cls.__name__, name))
    super(StaticType, cls).__delattr__(name)

class InterfaceType(StaticType):
  """
  A yuppy interface.
  """
  def __init__(cls, name, bases, attrs):
    for attrname, attr in attrs.items():
      if isattribute(attr):
        attr.__name__ = attrname
      if not attrname.startswith('_') and isinstance(attr, FunctionType):
        attrs[attrname] = AbstractMethod(attr)
    super(InterfaceType, cls).__init__(name, bases, attrs)

class ClassType(StaticType):
  """
  A yuppy class type.
  """
  def __init__(cls, name, bases, attrs):
    super(ClassType, cls).__init__(name, bases, attrs)
    class_isabstract = False
    interfaces = getattr(cls, '__interfaces__', [])
    for interface in interfaces:
      for base in interface.__mro__:
        for attrname, attr in base.__dict__.items():
          if isinstance(getattr(base, attrname), (FunctionType, MethodType)):
            if not hasattr(cls, attrname):
              raise AttributeError("Class '%s' is missing abstract method '%s' and must be declared abstract." % (name, attrname))
            elif not isinstance(getattr(cls, attrname), (FunctionType, MethodType)):
              raise AttributeError("Class '%s' attribute '%s' is not a method." % (name, attrname))

    for base in cls.__mro__:
      if isfinal(base) and cls is not base:
        raise TypeError("Cannot override final class '%s'." % (base.__name__,))
      for attrname, attr in base.__dict__.items():
        if isattribute(attr):
          attr.__name__ = attrname
        if isabstract(attr):
          func = cls._findattr(attrname)
          try:
            func = func.__method__
          except AttributeError:
            pass
          try:
            meth = attr.__method__
          except AttributeError:
            meth = attr
          if func is meth:
            class_isabstract = True
        if base is not cls and isfinal(attr):
          func = cls._findattr(attrname)
          try:
            func = func.__method__
          except AttributeError:
            pass
          try:
            func = func.im_func
          except AttributeError:
            pass
          try:
            meth = attr.__method__
          except AttributeError:
            meth = attr
          if func is not meth:
            raise TypeError("Cannot override final '%s' method '%s'." % (base.__name__, attrname))

    if class_isabstract:
      setattr(cls, '__abstract__', True)

class Object(object):
  """
  A yuppy base class.
  """
  __metaclass__ = ClassType
  def __new__(cls, *args, **kwargs):
    if isabstract(cls):
      raise TypeError("Cannot instantiate abstract class '%s'." % (cls.__name__,))
    return object.__new__(cls, *args, **kwargs)

  def __setattr__(self, name, value):
    if isattribute(value):
      setattr(self.__class__, name, value)
    else:
      super(Object, self).__setattr__(name, value)

def yuppy(cls):
  """
  Decorator for yuppy classes.
  """
  class Object(cls):
    __metaclass__ = ClassType
    def __new__(cls, *args, **kwargs):
      if isabstract(cls):
        raise TypeError("Cannot instantiate abstract class '%s'." % (cls.__name__,))
      return object.__new__(cls, *args, **kwargs)
  Object.__name__ = cls.__name__
  return Object

class Interface(object):
  """
  A yuppy interface class.
  """
  __metaclass__ = InterfaceType

  def __new__(cls, *args, **kwargs):
    raise TypeError("Cannot instantiate interface '%s'." % (cls.__name__,))

def isinterface(cls):
  """
  Indicates whether the given class is an interface.
  """
  return isinstance(cls, Interface)

def instanceof(obj, interface, ducktype=True):
  """
  Indicates whether the given object is an instance of the given interface.
  """
  if ducktype:
    for base in interface.__mro__:
      for attrname, attr in base.__dict__.items():
        if isinstance(getattr(base, attrname), FunctionType):
          if not hasattr(obj, attrname):
            return False
          elif not isinstance(getattr(obj, attrname), FunctionType):
            return False
    return True
  else:
    if isinstance(obj, interface):
      return True
    try:
      if interface in obj.__interfaces__:
        return True
      else:
        return False
    except AttributeError:
      return False

def implements(interface):
  """
  Decorator for implementing an interface.
  """
  def wrap(cls):
    try:
      isclasstype = cls.__metaclass__ is ClassType
    except AttributeError:
      isclasstype = False
    if not isclasstype:
      cls = yuppy(cls)
    try:
      cls.__interfaces__
    except AttributeError:
      cls.__interfaces__ = []
    if interface not in cls.__interfaces__:
      cls.__interfaces__.append(interface)
    class _Implements(cls):
      pass
    _Implements.__name__ = cls.__name__
    return _Implements
  return wrap
