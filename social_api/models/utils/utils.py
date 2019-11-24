from google.cloud.firestore_v1 import Increment
import logging
import typing
from functools import total_ordering, wraps
import itertools
from social_api import firestoreDB


async def increase_or_decrease_a_document_field(collection, docId: str, fieldName: str, amount: typing.Union[int, float] = 1) -> None:
    """
        collection is a firestore collection, defined in __init__.py files
        docId: document id to delete
        fieldName: which field to update
        amount: integer number to add or minus from "fieldName"
        e.g:
            USER_COLLECTION.document(
                u"{}".format(docId)
            ).update({
                u"{}".format(fieldName): Increment(amount)
            })
    """
    try:
        collection.document(
            u"{}".format(docId)
        ).update({
            u"{}".format(fieldName): Increment(amount)
        })
    except Exception as e:
        logging.error(f"Error updating {fieldName!r}: {e}")
    else:
        logging.info(
            f"Successfully updated collection {repr(collection)}, id: {docId}"
        )


async def remove_documents_from_a_collection(documentSnapshotList: list) -> None:
    """
        iterates over "documentSnapshotList"
        refers to their documentReference
        add them to delete stage using batch delete
    """
    # refer to: https://firebase.google.com/docs/firestore/manage-data/transactions#batched-writes
    batch = firestoreDB.batch()
    for docSnapshot in documentSnapshotList:
        batch.delete(docSnapshot.reference)
    # commit the batch:
    batch.commit()


class Promise:
    pass


def lazy(func, *resultclasses):
    """
    Turn any callable into a lazy evaluated callable. result classes or types
    is required -- at least one is needed so that the automatic forcing of
    the lazy evaluation code is triggered. Results are not memoized; the
    function is evaluated on every access.
    """

    @total_ordering
    class __proxy__(Promise):
        """
        Encapsulate a function call and act as a proxy for methods that are
        called on the result of that function. The function is not evaluated
        until one of the methods on the result is called.
        """
        __prepared = False

        def __init__(self, args, kw):
            self.__args = args
            self.__kw = kw
            if not self.__prepared:
                self.__prepare_class__()
            self.__class__.__prepared = True

        def __reduce__(self):
            return (
                _lazy_proxy_unpickle,
                (func, self.__args, self.__kw) + resultclasses
            )

        def __repr__(self):
            return repr(self.__cast())

        @classmethod
        def __prepare_class__(cls):
            for resultclass in resultclasses:
                for type_ in resultclass.mro():
                    for method_name in type_.__dict__:
                        # All __promise__ return the same wrapper method, they
                        # look up the correct implementation when called.
                        if hasattr(cls, method_name):
                            continue
                        meth = cls.__promise__(method_name)
                        setattr(cls, method_name, meth)
            cls._delegate_bytes = bytes in resultclasses
            cls._delegate_text = str in resultclasses
            assert not (cls._delegate_bytes and cls._delegate_text), (
                "Cannot call lazy() with both bytes and text return types.")
            if cls._delegate_text:
                cls.__str__ = cls.__text_cast
            elif cls._delegate_bytes:
                cls.__bytes__ = cls.__bytes_cast

        @classmethod
        def __promise__(cls, method_name):
            # Builds a wrapper around some magic method
            def __wrapper__(self, *args, **kw):
                # Automatically triggers the evaluation of a lazy value and
                # applies the given magic method of the result type.
                res = func(*self.__args, **self.__kw)
                return getattr(res, method_name)(*args, **kw)
            return __wrapper__

        def __text_cast(self):
            return func(*self.__args, **self.__kw)

        def __bytes_cast(self):
            return bytes(func(*self.__args, **self.__kw))

        def __bytes_cast_encoded(self):
            return func(*self.__args, **self.__kw).encode()

        def __cast(self):
            if self._delegate_bytes:
                return self.__bytes_cast()
            elif self._delegate_text:
                return self.__text_cast()
            else:
                return func(*self.__args, **self.__kw)

        def __str__(self):
            # object defines __str__(), so __prepare_class__() won't overload
            # a __str__() method from the proxied class.
            return str(self.__cast())

        def __eq__(self, other):
            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() == other

        def __lt__(self, other):
            if isinstance(other, Promise):
                other = other.__cast()
            return self.__cast() < other

        def __hash__(self):
            return hash(self.__cast())

        def __mod__(self, rhs):
            if self._delegate_text:
                return str(self) % rhs
            return self.__cast() % rhs

        def __deepcopy__(self, memo):
            # Instances of this class are effectively immutable. It's just a
            # collection of functions. So we don't need to do anything
            # complicated for copying.
            memo[id(self)] = self
            return self

    @wraps(func)
    def __wrapper__(*args, **kw):
        return __proxy__(args, kw)

    return __wrapper__


def _lazy_proxy_unpickle(func, args, kwargs, *resultClasses):
    return lazy(func, *resultClasses)(*args, **kwargs)


def keep_lazy(*resultClasses):
    """
    A decorator that allows a function to be called with one or more lazy
    arguments. If none of the args are lazy, the function is evaluated
    immediately, otherwise a __proxy__ is returned that will evaluate the
    function when needed.
    """
    if not resultClasses:
        raise TypeError("You must pass at least one argument to keep_lazy().")

    def decorator(func):
        lazy_func = lazy(func, *resultClasses)

        @wraps(func)
        def wrapper(*args, **kwargs):
            if any(isinstance(arg, Promise) for arg in itertools.chain(args, kwargs.values())):
                return lazy_func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def keep_lazy_text(func):
    """
    A decorator for functions that accept lazy arguments and return text.
    """
    return keep_lazy(str)(func)


@keep_lazy_text
def slugify(value: str, allowUnicode: bool = False) -> str:
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    import re
    from unicodedata import normalize
    if allowUnicode:
        value = normalize('NFKC', value)
    else:
        value = normalize('NFKD', value).encode(
            'ascii', 'ignore'
        ).decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)
