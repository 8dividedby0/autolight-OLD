import infi.systray

class trayApp:
    def __init__(self, darkFunction, lightFunction, shutdownFunction, icon, logger):
        menu_options = (
            ("Go to dark now", "icons/night.ico", darkFunction),
            ("Go to light now", "icons/day.ico", lightFunction),
        )
        self.logger = logger
        self.systray = infi.systray.SysTrayIcon(icon, "AutoLight", menu_options, on_quit=shutdownFunction)
        self.systray.start()

    def changeIcon(self, icon):
        self.systray.update(icon)
        self.logger.logPrint(f"Updated icon to {icon}")

    def updateHoverText(self, text):
        self.systray.update(hover_text=text)
        

__all__ = [trayApp]