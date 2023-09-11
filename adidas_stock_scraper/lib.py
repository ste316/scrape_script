class tool:
    from os import environ
    # this color below works only on unixlike shell
    # unsupported shell will use plain text without color
    OKGREEN = '\033[92m'
    WARNING_YELLOW = '\033[93m'
    FAIL_RED = '\033[91m'
    ENDC = '\033[0m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'

    bool_term_program = False
    if 'TERM_PROGRAM' in environ.keys():
        bool_term_program = True

    @staticmethod
    def logConsole(text: str, color: str, end: str):
        if tool.bool_term_program:
            print(f'{color}{text} {tool.ENDC}', end=end)
        else:
            print(text, end=end)

    @staticmethod
    def printOk(text: str, end = "\n", returnOnly: bool = False):
        return tool.handlePrint(text, color=tool.OKGREEN, symbol="[+]", end=end, returnOnly=returnOnly)

    @staticmethod
    def printWarn(text: str, end = "\n", returnOnly: bool = False):
        return tool.handlePrint(text, color=tool.WARNING_YELLOW, symbol="[+]", end=end, returnOnly=returnOnly)

    @staticmethod
    def printFail(text: str, end = "\n", returnOnly: bool = False):
        return tool.handlePrint(text, color=tool.FAIL_RED, symbol="[-]", end=end, returnOnly=returnOnly)

    @staticmethod
    def printBlue(text: str, end = "\n", returnOnly: bool = False):
        return tool.handlePrint(text, color=tool.BLUE, symbol="[x]", end=end, doubleSymbol=False, returnOnly=returnOnly)

    @staticmethod
    def printPurple(text: str, end= "\n", returnOnly: bool = False):
        return tool.handlePrint(text, color=tool.PURPLE, symbol="[!]", end=end, returnOnly=returnOnly)

    @staticmethod
    def handlePrint(text: str, color: str, symbol: str, end: str = "\n", doubleSymbol: bool = False, returnOnly: bool = False):
        temp = tool.formatInput(text)
        for item in temp[0]:
            if tool.ENDC in item:
                item = item.replace(tool.ENDC, tool.ENDC+color)
            
            if returnOnly:
                return tool.returnFormatText(f'{symbol} {item} {symbol if doubleSymbol else ""}', color=color, end=end)
            else:
                return tool.logConsole(f'{symbol} {item} {symbol if doubleSymbol else ""}', color=color, end=end)

    @staticmethod
    def formatInput(text: str):
        if "\n" in text:
            text = text.split('\n') 
            return text, True
        return [text], False

    @staticmethod
    def returnFormatText(text: str, color: str, end: str):
        if tool.bool_term_program:
            return f'{color}{text} {tool.ENDC}{end}'
        else:
            return f'{text}{end}'
    
    @staticmethod
    def getTime():
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S:%f")

if __name__ == '__main__':
    pass