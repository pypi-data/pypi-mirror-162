from AEngine.ArgParser import *
from AEngine import print


class App:
    __banner = ""
    __description = ""
    __instances = 0

    def __new__(cls):
        cls.__instances += 1
        if cls.__instances > 1:
            raise SystemError("Can not create more then one App instance")
        return super(App, cls).__new__(cls)

    def __init__(self):
        self.args = ArgumentList()
        ArgumentParser.without_values.append("-h")

    def set_banner(self, banner):
        self.__banner = banner

    def load_banner(self, filename):
        with open(filename, "r") as file:
            self.set_banner(file.read())

    def set_description(self, description):
        self.__description = description

    def content(self):
        raise NotImplementedError("'content' method of 'App' was not implemented")

    def run(self):
        ArgumentParser.parse()
        if "h" in self.args.keys():
            print(self.__description)
            raise SystemExit(0)
        print(self.__banner)
        self.content()
