from datetime import datetime

def getPrefix(severity=None):
    now = datetime.now()
    match severity:
        case 0:
            severityCharacter = "🛈 "
        case 1:
            severityCharacter = "⚠ "
        case 2:
            severityCharacter = "🅧 "
        case None:
            severityCharacter = "? "
    current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    return severityCharacter + current_time + " > "


class logger:
    def __init__(self, fileName, settings=None) -> None:
        self.file = open(fileName, "a", encoding="utf-8")
        initMessage = True
        if not settings == None:
            for i in list(settings.keys()):
                match i:
                    case "initMessage":
                        initMessage = settings["initMessage"]
                    case _:
                        self.file.write(f"{getPrefix(0)}{i} is not a valid setting.")
        if initMessage:
            self.file.write("-----------------------" + "\n")
            self.file.write(getPrefix(0) + "Initalized logger." + "\n")
    
    def info(self, message):
        self.file.write(getPrefix(0) + message + "\n")

    def warn(self, message):
        self.file.write(getPrefix(1) + message + "\n")
    
    def error(self, message):
        self.file.write(getPrefix(2) + message + "\n")
    
    def sendRawMessage(self, message):
        self.file.write(message + "\n")

    def logPrint(self, message, prefix=0):
        self.file.write(getPrefix(prefix) + message + "\n")
        print(message)

__all__ = [logger]