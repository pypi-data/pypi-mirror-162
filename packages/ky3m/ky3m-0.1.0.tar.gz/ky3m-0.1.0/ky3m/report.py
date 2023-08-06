class Report:
    def __init__(self, method_name: str) -> None:
        self.__method_name = method_name
        self.__log = []
        self.__result = ''

    def __str__(self):
        return self.__result

    def record(self, text: str, name: str) -> None:
        n = '\n'
        nt = '\n\t'
        self.__log.append(f'[{name}] {text.replace(n, nt)}')

    def describe(self, text: str) -> None:
        self.__result = text

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, value):
        self.__result = value

    @property
    def log(self):
        return self.__log
