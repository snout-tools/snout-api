class AppHierarchy(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._children = []
        self.parent = kwargs.get('parent', None)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if not value:
            self._parent = None
        elif isinstance(value, AppHierarchy):
            self._parent = value
            self._parent.children.append(self)
        else:
            raise TypeError(
                f'The parent of {self.__class__.__name__} must be an instance of SnoutAgent or None.'
            )

    @property
    def children(self):
        """Children of the AppHierarchy object.

        Returns:
            AppHierarchy object: Children of this AppHierarchy object.
        """
        return self._children
