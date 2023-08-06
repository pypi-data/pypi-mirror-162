class MCDependency:
    def __init__(self, modid: str, version: str):
        self.__id = modid
        self.__ver = version

    @property
    def version(self):
        return self.__ver


class MCMod:
    def __init__(self, modid, mcversion):
        # TODO implement version ranges; also consider @version.setter self.version() functionality
        mcversion = mcversion

        self.__id = modid
        self.__deps = [MCDependency('minecraft', mcversion)]
        self.__name = self.__id
        self.__ver = 'unknown'  # self version, not to be confused with minecraft version
        self.__loader = 'unknown'
        self.__desc = 'Another Minecraft mod...'

    @property
    def modid(self):
        return self.__id

    @modid.setter
    def modid(self, val):
        self.__id = val

    @property
    def dependencies(self):
        return self.__deps

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, val):
        self.__name = val

    @property
    def version(self):
        return self.__ver

    @version.setter
    def version(self, val):
        self.__ver = val

    @property
    def description(self):
        return self.__desc

    @description.setter
    def description(self, val):
        self.__desc = val

    @property
    def loader(self):
        return self.__loader

    @loader.setter
    def loader(self, val):
        self.__loader = val
