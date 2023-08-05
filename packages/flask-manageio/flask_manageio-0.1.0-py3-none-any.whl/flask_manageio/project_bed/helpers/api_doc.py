import inspect
from collections import defaultdict
from operator import itemgetter
from flask import current_app


class Apidoc(object):

    def __init__(self, app=None):
        self.app = app
        self.func_groups = defaultdict(set)
        self.func_locations = defaultdict(dict)

    def init_app(self, app):
        self.app = app

    def doc(self, groups=None):
        """Add flask route to autodoc for automatic documentation
        Any route decorated with this method will be added to the list of
        routes to be documented by the generate() method.
        By default, the route is added to the 'all' group.
        By specifying group or groups argument, the route can be added to one
        or multiple other groups as well, besides the 'all' group.
        """

        def decorator(f):
            # Set group[s]
            if type(groups) is list:
                groupset = set(groups)
            else:
                groupset = set()
                if type(groups) is str:
                    groupset.add(groups)
            groupset.add('all')
            self.func_groups[f] = groupset

            # Set location
            caller_frame = inspect.stack()[1]
            self.func_locations[f] = {
                'filename': caller_frame[1],
                'line': caller_frame[2],
            }

            return f

        return decorator

    def generate(self, groups='all', sort=None):
        """Return a list of dict describing the routes specified by the
        doc() method

        Each dict contains:
         - methods: the set of allowed methods (ie ['GET', 'POST'])
         - rule: relative url (ie '/user/<int:id>')
         - endpoint: function name (ie 'show_user')
         - doc: docstring of the function
         - args: function arguments
         - defaults: defaults values for the arguments

        By specifying the group or groups arguments, only routes belonging to
        those groups will be returned.

        Routes are sorted alphabetically based on the rule.
        """
        groups_to_generate = list()
        if type(groups) is list:
            groups_to_generate = groups
        elif type(groups) is str:
            groups_to_generate.append(groups)

        links = []
        for rule in current_app.url_map.iter_rules():

            if rule.endpoint == 'static':
                continue

            func = current_app.view_functions[rule.endpoint]
            arguments = rule.arguments if rule.arguments else ['None']
            func_groups = self.func_groups[func]
            location = self.func_locations.get(func, None)

            if func_groups.intersection(groups_to_generate):
                links.append(
                    dict(
                        methods=rule.methods,
                        rule="%s" % rule,
                        endpoint=rule.endpoint,
                        docstring=func.__doc__,
                        args=arguments,
                        defaults=rule.defaults,
                        location=location,
                    )
                )
        if sort:
            return sort(links)
        else:
            return sorted(links, key=itemgetter('rule'))
