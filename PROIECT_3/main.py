import sys
import os

# Ne asiguram ca directorul curent este in sys.path pentru importuri relative corecte
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()