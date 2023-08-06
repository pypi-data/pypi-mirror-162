import inspect
import re
from flask_apispec import doc


def ddoc(*args, **kwargs):
    '''
    Decorator generating proper documentation from docstrings

    '''
    def get_object(func, obj_name):
        """
        Find a specific tag in docstrings (could be multiline)
        """
        text = inspect.getdoc(func)
        splitted = re.split(r':([A-Za-z]*):', text)
        if obj_name in splitted:
            obj_index = splitted.index(obj_name)
            return splitted[obj_index + 1].strip()
        else:
            return None

    def get_tags(func):
        tags_str = get_object(func, 'Tags')
        if not tags_str:
            tags = ['default']
        else:
            tags = [a.strip() for a in tags_str.split(',')]

        return tags

    def get_docs(func):
        summary = get_object(func, 'Summary')
        if not summary:
            summary = 'Default, edit docstrings of summary/description'
        description = get_object(func, 'Description')
        if not description:
            description = summary
        return summary, description

    def wrapper(func):
        # print type(func), dir(func)
        if inspect.isclass(func):
            kwargs['tags'] = get_tags(func)
        elif inspect.isfunction(func):
            kwargs['summary'], kwargs['description'] = get_docs(func)
        k = doc(func, **kwargs)
        return k(func)

    if kwargs:
        return wrapper
    else:
        return wrapper(args[0])
