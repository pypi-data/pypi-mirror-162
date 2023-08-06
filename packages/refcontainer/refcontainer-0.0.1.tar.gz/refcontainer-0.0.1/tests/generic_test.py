from refcontainer.strong_generic import StrongGeneric


def test_strong_generic():
    class Typed(StrongGeneric[str]):
        @classmethod
        def get_constraints(cls):
            return cls._type_constraints()
    assert Typed().get_constraints() == str
