# src/app.py
from views.mainwindow import MainWindow

from database.database import initialize_database


class Application:
    def __init__(self):
        pass

    def run(self):
        if not initialize_database():
            raise Exception("initialize database failed!")

        self.mainwindow = MainWindow()
        self.mainwindow.show()
        print("Scraper application is running ...")
