import sys
from file import PNGfile


class Menu:
    def __init__(self, path):
        self.file = PNGfile(path)

    def start(self):

        def display_menu():
            print("What do you want to do?")
            print("[1] - change file")
            print("[2] - display chunks")
            print("[3] - display info of each chunk")
            print("[4] - display fft")
            print("[5] - make anonymized file")
            print("[6] - quit")

        def ask_if_enough():
            d = input("Go back to menu? [YES/NO]")
            if d == str.lower("YES"):
                display_menu()
            else:
                sys.exit()

        while True:
            display_menu()
            decision = input("Please choose number ")

            if int(decision) == 1:
                new_path = input("Enter new files path: ")
                self.file = PNGfile(new_path)
                ask_if_enough()

            if int(decision) == 2:
                self.file.display_chunks()
                ask_if_enough()

            if int(decision) == 3:
                self.file.display_chunks_info()
                ask_if_enough()

            if int(decision) == 4:
                self.file.fourier_analise()
                ask_if_enough()

            if int(decision) == 5:
                self.file.anonimyzation()
                ask_if_enough()

            if int(decision) == 6:
                sys.exit()

