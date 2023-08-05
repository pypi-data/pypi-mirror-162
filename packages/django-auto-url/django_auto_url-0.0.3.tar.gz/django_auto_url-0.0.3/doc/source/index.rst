Welcome to django_auto_url's documentation!
=================================================

django_auto_url is a Django_ app that liberates you from maintaining the
:code:`urls.py` files.

The principle is that a website (or a webapp) basically consists of a bunch
of :class:`~django.views.generic.base.View` and the user navigates from one
:class:`~django.views.generic.base.View` to the next or gets directed to
:class:`~django.views.generic.base.View` after some interaction.

So why the hassle with manually creating URL patterns and names?

django_auto_url provides functions and mixins to automate this process.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference

Quickstart
----------

Install
_______

.. code-block::

    pip install django_auto_url

Configure
_________

Next, include :code:`django_auto_url` in the :code:`INSTALLED_APPS` section of the Django_ :code:`settings.py`:

.. code-block:: python

   INSTALLED_APPS = [
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django_auto_url'
       ]

Prepare the views
_________________

Now include the :class:`~django_auto_url.mixins.mixins.AutoUrlMixin` in the
mixins of your view class:

.. attention:: Always include mixins **before** the view class!

.. code-block:: python

    from django.views.generic import TemplateView
    from django_auto_url.mixins import AutoUrlMixin

    class MyView(AutoUrlMixin, TemplateView):
        template_name = 'my_template.html'

Prepare urls.py
_______________

Now we need to generate the :code:`urlpatterns` for our view in the :code:`urls.py` file.

The :code:`urls.py` file would look like this:

.. code-block:: python

    from my_app import views
    from django_auto_url.urls import get_urls_from_module

    urlpatterns = get_urls_from_module(views)

Get the URL for the view
________________________

django_auto_url provides several methods to get the URL of a view.

Use the template tag
####################

Getting the absolute URL for a view in Django_ is done using the
`url <https://docs.djangoproject.com/en/stable/ref/templates/builtins/#url>`_
template tag. django_auto_url provides a similar template tag, called
:ttag:`url_from_class` that performs the same task but takes the full module
path to a view as the argument.

Let's consider that the view class we created above lives in the :code:`views`
package of your app called :code:`my_app`.

Here is how to create a link to it from a template:

.. code-block:: html

        {% load auto_url %}

        <a href="{% url_from_class "my_app.views.MyView" %}">Click me!</a>

Use the Python functions
########################

In order to get the URL for a view, use one of the following functions:

* :func:`~django_auto_url.urls.urls.reverse_classname`
* :func:`~django_auto_url.urls.urls.reverse_classname_lazy`
* :func:`~django_auto_url.urls.urls.reverse_local_classname`

All these function are quite similar in how they work: You provide the view
class or the full module path as a string and you get the URL returned.

.. code-block:: python

    from my_app import views
    from django_auto_url.urls import reverse_classname

    # resolve now. views.MyView must have already been declared.
    url_for_view = reverse_classname(views.MyView)
    url_for_view = reverse_classname('my_app.views.MyView')

    # resolve later. views.MyView can be declared later.
    # This is very useful if you need to provide a URL as a class variable.
    url_for_view = reverse_classname_lazy(views.MyView)
    url_for_view = reverse_classname_lazy('my_app.views.MyView')

For further details, please refer to the
:doc:`appropriate section in the reference <reference>`.

Use Arguments for the View
--------------------------

As usual, views can accept arguments by their URL patterns. You can do this
for your :class:`~django_auto_url.mixins.mixins.AutoUrlMixin` views by
specifying :code:`url_kwargs` like this:

.. code-block:: python

    from django.views.generic import TemplateView
    from django_auto_url.mixins import AutoUrlMixin
    from django_auto_url import kwargs

    class MyView(AutoUrlMixin, TemplateView):
        template_name = 'my_template.html'
        url_kwargs = [
            kwargs.String('my_string'),
            kwargs.Int('my_int', 42)
        ]

In this case, we have specified that the view takes two arguments, one
string and one int. And there is a default value for the integer value.

The values of these arguments are provided as kwargs to the respective methods
of the view as well as to the context.

From your template, here is how you would link to it:

.. code-block:: html

        {% load auto_url %}

        <a href="{% url_from_class "my_app.views.MyView" my_string="Hello World" %}">Click me!</a>
        <a href="{% url_from_class "my_app.views.MyView" my_string="Hello" my_int=32 %}">Click me, too!</a>

The respective python function provide a args and kwargs parameter you can use:

.. code-block:: python

    from my_app import views
    from django_auto_url.urls import reverse_classname

    # resolve now. views.MyView must have already been declared.
    url_for_view = reverse_classname(views.MyView, kwargs = {
                                                        'my_string': 'Hello World'
                                                    })

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
