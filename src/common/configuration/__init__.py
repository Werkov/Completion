__all__ = [
    'Configuration',
    'fillSubparsers',
    'createFromArgs',
    'current'
]

# Current configuration
current = None

class Configuration:
    """
    Represents a container of service objects.

    To access the desired object call it as a configuration instance attribute –
    – either cached object is returned or factory method is called to create one.

    Dependencies are hard-coded into the factory methods in descedants.
    BEWARE of cycles in dependency graph.

    Configuration has text metainformation and could specify its parameter
    retrieval via argparse.ArgumentParser class.
    """
    _cache              = dict()
    _params             = dict()
    _factoryPrefix      = "_create"

    def __init__(self, **kwargs):
        """
        Configuration can be parametrized via keyword arguments for use in factory methods.
        """
        self._params = kwargs

    def __getattr__(self, name):
        """Lazily create desired objects."""
        if name not in self._cache:
            try:
                factoryMethod = self.__getattribute__(self._factoryPrefix + name[0].upper() + name[1:])
                self._cache[name] = factoryMethod()
            except KeyError:
                raise AttributeError(name)

        return self._cache[name]

    #
    # Argument parsing facilities
    #

    def configureArgParser(parser):
        """Configure argparse.ArgumentParser for parameters required by the configuration."""
        pass

    description = None
    aliases     = []


def fillSubparsers(subparsers):
    """Create subparsers for known configurations."""
    # more configuration modules could be set here
    import common.configuration.basic as bas

    for name, val in vars(bas).items():
        try:
            # val is descedant class of `Configuration`
            if issubclass(val, Configuration) and not issubclass(Configuration, val):
                parser = subparsers.add_parser(name.lower(), help=val.description, aliases=val.aliases)
                val.configureArgParser(parser)
                parser.set_defaults(confClass=val)
        except TypeError:
            continue
    pass

    
    return


def createFromArgs(args):
    """Initialize module attribute with chosen configuration."""
    global current
    current = args.confClass(**vars(args))

