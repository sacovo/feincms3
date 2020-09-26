from django.template import Context, Engine


__all__ = (
    "PluginNotRegistered",
    "TemplatePluginRenderer",
    "default_context",
    "render_in_context",
)


class PluginNotRegistered(Exception):
    pass


def default_context(plugin, context):
    """
    Return the default context for plugins rendered with a template, which
    simply is a single variable named ``plugin`` containing the plugin
    instance.
    """
    return {"plugin": plugin}


class TemplatePluginRenderer:
    """
    This renderer allows registering functions, templates and context providers
    for plugins. It also supports rendering plugins' templates using the
    rendering context of the surrounding template without explicitly copying
    required values into the local rendering context.
    """

    def __init__(self):
        self._renderers = {}

    def register_string_renderer(self, plugin, renderer):
        """
        Register a rendering function which is passed the plugin instance and
        returns a HTML string:

        .. code-block:: python

            renderer.register_string_renderer(
                RichText,
                lambda plugin: mark_safe(plugin.text),
            )
        """
        self._renderers[plugin] = (None, renderer)

    def register_template_renderer(
        self, plugin, template_name, context=default_context
    ):
        """register_template_renderer(self, plugin, template_name,\
context=default_context)
        Register a renderer for ``plugin`` using a template. The template uses
        the same mechanism as ``{% include %}`` meaning that the full template
        context is available to the plugin renderer.

        ``template_name`` can be one of:

        - A template path
        - A list of template paths
        - An object with a ``render`` method
        - A callable receiving the plugin as only parameter and returning any
          of the above.

        ``context`` must be a callable receiving the plugin instance and the
        template context and returning a dictionary. The default implementation
        simply returns a dictionary containing a single key named ``plugin``
        containing the plugin instance.

        .. code-block:: python

            # Template snippets have access to everything in the template
            # context, including for example ``page``, ``request``, etc.
            renderer.register_template_renderer(
                Snippet,
                lambda plugin: plugin.template_name,
            )

            # Additional context can be provided:
            renderer.register_template_renderer(
                Team,
                "pages/plugins/team.html",  # Can also be a callable
                lambda plugin, context: {
                    "persons": Person.objects.filter(
                        # Assuming that the page has a team foreign key:
                        team=plugin.parent.team,
                    ),
                },
            )
        """
        self._renderers[plugin] = (template_name, context)

    def plugins(self):
        """
        Return a list of all registered plugins, and is most useful when passed
        directly to one of django-content-editor's contents utilities:

        .. code-block:: python

            page = get_object_or_404(Page, ...)
            contents = contents_for_item(page, renderer.plugins())
        """

        return list(self._renderers.keys())

    def render_plugin_in_context(self, plugin, context=None):
        """
        Render a plugin, passing on the template context into the plugin's
        template (if the plugin uses a template renderer).
        """
        if plugin.__class__ not in self._renderers:
            raise PluginNotRegistered(
                "Plugin %s is not registered" % plugin._meta.label_lower
            )
        template, local_context = self._renderers[plugin.__class__]

        if template is None:
            # Simple string renderer
            return local_context(plugin) if callable(local_context) else local_context

        if context is None:
            context = Context()

        if callable(template):
            template = template(plugin)
        if callable(local_context):
            local_context = local_context(plugin, context)

        return render_in_context(context, template, local_context)


def render_in_context(context, template, local_context=None):
    """Render using a template rendering context

    This utility avoids the problem of ``render_to_string`` requiring a
    ``dict`` and not a full-blown ``Context`` instance which would needlessly
    burn CPU cycles."""

    if context is None:
        context = Context()

    if not hasattr(template, "render"):  # Quacks like a template?
        try:
            engine = context.template.engine
        except AttributeError:
            engine = Engine.get_default()

        if isinstance(template, (list, tuple)):
            template = engine.select_template(template)
        else:
            template = engine.get_template(template)

    with context.push(local_context):
        return template.render(context)
