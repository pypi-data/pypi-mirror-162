import os, importlib, importlib.util

class InvalidPlugin(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class InvalidPluginDirectory(Exception):
    def __init__(self, dir):
        super().__init__("The plugin directory '"+dir+"' is not valid.")

class PluginType():
    def __init__(self, name, shared={}, load_path:str=None, event_handler=None):
        self.name, self.shared, self.load_path = name, shared, load_path if not load_path or load_path.endswith("/") else load_path+"/"
        self.plugins = {}
        self.event_handler = event_handler
    def load(self, plugin_name=None, file_name=None, full_path=None, module_path=None):
        if bool(plugin_name)+bool(file_name)+bool(full_path)+bool(module_path) != 1:
            raise TypeError("PluginType.load() needs exactly one of these parameters: plugin_name, file_name, full_path or module_path")

        # Resolving module path of plugin
        if plugin_name:
            file_name = plugin_name+".py"
        if file_name:
            full_path = (self.load_path if self.load_path else "")+file_name
        if full_path and not plugin_name:
            plugin_name = full_path.split("/")[-1][:-3]
        if plugin_name in self.plugins:
            return
        if not os.path.isfile(full_path):
            raise InvalidPlugin("Plugin named '"+plugin_name+"' at '"+full_path+"' does not exist.")
        if module_path:
            module=importlib.import_module(module_path)
        else:
            spec = importlib.util.spec_from_file_location(plugin_name, full_path)
            module=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        # Getting & Checking plugin
        plugin = getattr(module, self.name, None)
        if not plugin:
            raise InvalidPlugin("Plugin "+plugin_name+" does not contain a class named '"+self.name+"'")
        if not issubclass(plugin, Plugin):
            raise InvalidPlugin("The class named '"+self.name+"' in the plugin is not a subclass of Plugin")
        # Plugin setup
        plugin.__prepare__(plugin, self, self.shared, self.event_handler)

        for n in self.shared:
            setattr(plugin, n, self.shared[n])
        self.plugins[plugin_name] = plugin()


    def load_all(self):
        if not os.path.exists(self.load_path):
            os.mkdir(self.load_path)
        elif not os.path.isdir(self.load_path):
            raise 
        for f in os.listdir(self.load_path):
            if os.path.isfile(self.load_path+"/"+f) and len(f) > 3 and f[-3:] == ".py":
                self.load(file_name=f)

class EventAlreadyExists(Exception):
    def __init__(self, event_name):
        super().__init__("'"+event_name+"' already exists.")

class EventDoesNotExist(Exception):
    def __init__(self, event_name):
        super().__init__("'"+event_name+"' does not exist.")

class EventHandler():
    def __init__(self, allow_unregistered_events:bool, events=[]):
        self.allow_unregistered_events = allow_unregistered_events
        self.events = {}
        for event in events:
            self.events[event] = []
        self.__funcs__ = {}
        self.__plugin_types__ = []
    def add(self, event_name:str):
        # TODO: event_name has to be a string
        if event_name in self.events:
            raise EventAlreadyExists(event_name)
        self.events[event_name] = []
    def call(self, event_name, *args, **kwargs):
        if not self.allow_unregistered_events and event_name not in self.events:
            raise EventAlreadyExists(event_name)
        if event_name not in self.events:
            return
        
        for func in self.events[event_name]:
            if hasattr(func, "__plugin_listener__"):
                plugins = func.__plugin_listener__.__plugin_type__.plugins
                for plugin_name in plugins:
                    if isinstance(plugins[plugin_name], func.__plugin_listener__):
                        plugin = plugins[plugin_name]
                        break
                func(plugin, *args, **kwargs)

            else:
                func(*args, **kwargs)
    def event(self, event_name):
        if not self.allow_unregistered_events and event_name not in self.events:
            raise EventDoesNotExist(event_name)
        def decorator(func):
            if func not in self.__funcs__:
                self.__funcs__[func] = [event_name]
            else:
                self.__funcs__[func].append(event_name)
            if not event_name in self.events:
                self.events[event_name] = [func]
            else:
                self.events[event_name].append(func)
            return func
        return decorator

class Plugin():
    __plugin_type__:PluginType
    __shared__:dict
    __event_handler__:EventHandler
    """This class should not be called directly, use PluginType instead."""
    
    def require(self, plugin_name):
        if plugin_name not in self.__plugin_type__.plugins:
            self.__plugin_type__.load(plugin_name=plugin_name)
    def __prepare__(cls, plugin_type:PluginType, shared:dict, event_handler:EventHandler=None):
        if event_handler:
            cls.__event_handler__ = event_handler
            event_triggered = [attribute for attribute in dir(cls) if callable(getattr(cls, attribute)) and attribute.startswith('__') is False and getattr(getattr(cls, attribute), "__event_triggered__", None)]
            for method_name in event_triggered:
                method = getattr(cls, method_name)
                method.__plugin_listener__ = cls
                cls.__event_handler__.__funcs__[method] = method.__events__
                for event in method.__events__:
                    try:
                        cls.__event_handler__.events[event].append(method)
                    except AttributeError:
                        cls.__event_handler__.events[event] = [method]
        cls.__plugin_type__ = plugin_type
        cls.__shared__ = shared
        for n in shared:
            setattr(cls, n, shared[n])
    

    @classmethod
    def event(cls, event_name):
        """A decorator to use events in a plugin subclass"""
        #if not isinstance(cls, Plugin):
        #    raise TypeError("The decorator Plugin.event has to be used for plugin methods")
        #if not (hasattr(cls, "__event_handler__") and cls.__event_handler__):
        #    raise AttributeError("The plugin does not have an event handler.")
        #if not cls.allow_unregistered_events and event_name not in cls.events:
        #    raise EventDoesNotExist(event_name)
        def decorator(fn):
            fn.__event_triggered__ = True
            try:
                fn.__events__.append(event_name)
            except AttributeError:
                fn.__events__ = [event_name]
            return fn
        return decorator

