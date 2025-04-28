from src.views.mainwindow import MainWindow


class Application:
    def __init__(self):
        pass

    def run(self):
        self.mainwindow = MainWindow()
        self.mainwindow.show()
        print("Scraper application is running ...")
