Reference
=========

Functions
---------

.. automodule:: django_auto_url.urls.urls
    :members: get_urls_from_module, reverse_classname, reverse_classname_lazy,
              reverse_local_classname

Template Tags
-------------
.. templatetag:: url_from_class

    Return the absolute URL for a class, providing the full module path.

    This is the equivalent to the `url <https://docs.djangoproject.com/en/stable/ref/templates/builtins/#url>`_
    template tag of Django_.

    The only important difference is, that you can only use keyword arguments!

    .. rubric:: Example

    .. code-block:: html

        {% load auto_url %}

        <a href="{% url_from_class "my_app.views.MyView" bool_arg="False" say_this="New String" my_age="32" %}">Click me!</a>

    :parameters: * **viewname** (*str*) -- The full module path to the view.
                 * **\*\*kwargs** (*any*) -- Keyword arguments for the view.

    :returns: *str* -- The absolute URL.

Mixins
------

.. automodule:: django_auto_url.mixins.mixins
    :members: AutoUrlMixin


Keyword Arguments
-----------------

Keyword arguments can be specified by using the :code:`url_kwargs` class variable of
the view. You can specify a default value, but in this case, the order matters:
You cannot define a Keyword argument without a default after one for which
you have specified one.

Example
#######

.. code-block:: python

    class MyView(AutoUrlMixin, TemplateView):
        url_kwargs = [
                        kwargs.String('my_string'),
                        kwargs.Int('my_int', 42)
                     ]

.. automodule:: django_auto_url.kwargs.kwargs
    :members: string, int, bool

.. include:: links.rst