"""A None-guarding safe referencer"""
import sys


class SafeReference:

    def __init__(self, object, default):
        self.object = object
        self.default = default

    def __getattr__(self, item):
        try:
            return SafeReference(getattr(self.object, item), self.default)
        except:
            if self.object is not self.default:
                print(f"SafeReference: Dereference fault: {self.object.__class__.__name__}.{item}", file=sys.stderr)
            return SafeReference(self.default, self.default)

    def __getitem__(self, item):
        try:
            return SafeReference(self.object.__getitem__(item), self.default)
        except:
            return SafeReference(self.default, self.default)

    def __len__(self):
        return len(self.object)

    def __repr__(self):
        return str(self.object)

    def __bool__(self):
        return bool(self.object)

    def __eq__(self, other):
        return other == self.object

    def __call__(self, *args, **kwargs):
        try:
            return SafeReference(self.object(*args, *kwargs), self.default)
        except TypeError:
            return SafeReference(self.default, self.default)
