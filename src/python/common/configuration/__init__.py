__all__ = [
    'Configuration',
    'updateParser',
    'createFromArgs',
    'current'
]

from io import TextIOWrapper
import argparse

# Current configuration
current = None
aliasMap = {}

class Configuration:
    """
    Represents a container of service objects.

    To access the desired object call it as a configuration instance attribute –
    – either cached object is returned or factory method is called to create one.

    Dependencies are hard-coded into the factory methods in descedants.
    BEWARE of cycles in dependency graph.

    Configuration can be parametrized. Basically, it reads parameters from
    a dictionary (mapping protocol object) loaded from INI file. Each
    constructed object has it's own section.

    Some additional parameters can also be read from command line. Their
    specification is in `configureArgParser` method. Usually, they override
    INI file parameter, however it depends on concrete Configuration.
    """
    _cache              = dict()
    _params             = dict()
    _factoryPrefix      = "_create"

    def __init__(self, INIparams, CLIparams):
        """
        INIparams       dict    parameters from INI file
        CLIparams       dict    parameters from `argparse.ArgumentParser`
                                (in dictionary format)
        """
        self._INIparams = INIparams
        self._CLIparams = CLIparams

    def __getattr__(self, name):
        """Lazily create desired objects."""
        if name not in self._cache:
            try:
                factoryMethod = self.__getattribute__(self._factoryPrefix + name[0].upper() + name[1:])
                if name in self._INIparams:
                    self._cache[name] = factoryMethod(self._INIparams[name])
                else:
                    self._cache[name] = factoryMethod(self._INIparams["DEFAULT"])
            except KeyError as e:
                if e.args[0] != name:
                    raise e
                else:
                    raise AttributeError(name)
                

        return self._cache[name]

    def _initialize(self):
        """To create objects immediately instead of lazy loading and to break
        dependency cycles."""
        pass

    #
    # Argument parsing facilities
    #
    @staticmethod
    def configureArgParser(parser):
        """Configure argparse.ArgumentParser for parameters required by the configuration."""
        pass

    def __str__(self):
        result = ['# Configuration:\t' + self.__class__.__name__]
        result.append('')
        result.append('CLI params:')
        for k, v in self._CLIparams.items():
            if isinstance(v, list):
                v = [str(file) for file in v]
            elif isinstance(v, TextIOWrapper):
                v = v.name
            result.append('\t{}:\t{}'.format(k, v))

        result.append('')
        result.append('INI params:')
        for section in self._INIparams:
            result.append('\t[{}]'.format(section))
            for k in self._INIparams[section]:
                result.append('\t\t{}={}'.format(k, self._INIparams[section][k]))        
        result.append('')        
        return '\n# '.join(result)

    # metainformation
    description = None
    aliases     = []

def updateParser(parser):
    global aliasMap
    # more configuration modules could be set here
    import common.configuration.basic as bas

    choices = []
    helps = []
    for name, cls in vars(bas).items():
        try:
            # cls is descedant class of `Configuration`
            if issubclass(cls, Configuration) and not issubclass(Configuration, cls):
                choices.append(cls.alias)
                helps.append(cls.description)
                aliasMap[cls.alias] = cls
                try:
                    cls.configureArgParser(parser)
                except argparse.ArgumentError:
                    continue
                    
        except TypeError:
            continue

    rows = []
    for c, h in zip(choices, helps):
        rows.append('\t{}:\t{}'.format(c, h))
    helpMessage = '\n'.join(rows)
    parser.add_argument('-c', '--configuration', choices=choices, help=helpMessage, required=True)

def createFromParams(args, INIparams):
    """Initialize the module attribute with chosen configuration."""
    global current
    current = aliasMap[args.configuration](INIparams, vars(args))
    current._initialize()

