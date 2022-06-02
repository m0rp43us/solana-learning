import lockfile
import os
import simplejson

from enum import Enum
from spl.errors import CannotGetStateLockException


_INITIAL_STATE = {
    'installed_resources': {},
}

_STATE_DIR = '.spl/'
_STATE_FILE = _STATE_DIR + 'spl-state-v1.json'


def acquire_lock_or_die():
    try:
        lf = lockfile.LockFile(_STATE_DIR)
        lf.acquire(timeout=0)
        return lf
    except lockfile.AlreadyLocked:
        raise CannotGetStateLockException()


class StateLock(object):

    def __enter__(self):
        self.lf = acquire_lock_or_die()

    def __exit__(self, ttype, value, traceback):
        if self.lf and self.lf.i_am_locking():
            self.lf.release()


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class EnumEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return {"__enum__": str(obj)}
        return simplejson.JSONEncoder.default(self, obj)


def deserialize_objects(spiget):
    def inner(obj):
        if "__enum__" in obj:
            name, member = obj["__enum__"].split(".")
            return getattr(globals()[name], member)
        elif 'type' in obj:
            clazz = my_import(obj['type'])
            return clazz(spiget, obj)
        return obj
    return inner


class State(StateLock):
    _singleton = None

    def __init__(self, state=_INITIAL_STATE):
        self._state = state

    @staticmethod
    def load(spiget):
        if State._singleton is None:
            with StateLock():
                if os.path.exists(_STATE_FILE):
                    with open(_STATE_FILE, 'r') as stateFile:
                        object_hook = deserialize_objects(spiget)
                        state = simplejson.load(stateFile, object_hook=object_hook)
                        State._singleton = State(state)
                else:
                    State._singleton = State()
        return State._singleton

    def save(self):
        with StateLock():
            with open(_STATE_FILE, 'w') as stateFile:
                return simplejson.dump(self._state, stateFile, for_json=True, cls=EnumEncoder)

    def __enter__(self):
        StateLock.__enter__(self)
        return self

    def __exit__(self, ttype, value, traceback):
        self.save()
        StateLock.__exit__(self, ttype, value, traceback)

    def get_plugins_dir(self):
        path = os.path.join(_STATE_DIR, "plugins/")
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    @property
    def installed_resources(self):
        return self._state['installed_resources'].copy()

    def resource_state(self, resource):
        if str(resource.id) in self._state['installed_resources']:
            return self._state['installed_resources'][str(resource.id)]['state']
        return ResourceState.NOT_INSTALLED

    def resource_is_installed(self, resource):
        return self.resource_state(resource) != ResourceState.NOT_INSTALLED

    def install_resource(self, resource):
        self._state['installed_resources'][str(resource.id)] = {'resource': resource, 'state': ResourceState.INSTALLED_DISABLED}

    def enable_resource(self, resource):
        self._state['installed_resources'][str(resource.id)]['state'] = ResourceState.INSTALLED_ENABLED

    def disable_resource(self, resource):
        self._state['installed_resources'][str(resource.id)]['state'] = ResourceState.INSTALLED_DISABLED

    def resource_jar_file(self, resource):
        return os.path.join(self.get_plugins_dir(), "{}.jar".format(resource.id))


class ResourceState(Enum):
    NOT_INSTALLED = 0
    INSTALLED_DISABLED = 1
    INSTALLED_ENABLED = 2
