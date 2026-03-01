import sys

# PyQt Stuff
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QImage, QPixmap

# Designer Stuff
from app import Ui_MainWindow  # Import the class from your exported file

# Camera testing
import cv2

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):

        # Setup Designer stuff 
        super().__init__()
        self.setupUi(self)
        
        # Button connections
        self.eStop.clicked.connect(self.handle_estop)
        self.cStop.clicked.connect(self.handle_cstop)
        self.Continue.clicked.connect(self.handle_continue)

        # Video Thread
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def handle_estop(self):
        print("EMERGENCY STOP")
    
    def handle_cstop(self):
        print("CONTROLLED STOP")
    
    def handle_continue(self):
        print("CONTINUING OPERATIONS")
    
    def update_image(self, frame):
        self.VideoStream.setPixmap(QPixmap.fromImage(frame))

class VideoThreadNetwork(QThread):
    """ Class for you to implement! :) See VideoThread for some tips 
        Ideally this method will actually capture a video from some internet broadcast source.
        Maybe we set up a separate python file that streams a video that this one catches over the network? 
    """

class VideoThread(QThread):

    """ 
    Use the web cam to demo working thread for video stuff. 
    """
    change_pixmap_signal = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0) 
        while True:
            ret, cv_img = cap.read()

            if ret: 
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch*w
                
                convert_to_Qt_Format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                frame = convert_to_Qt_Format.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

                self.change_pixmap_signal.emit(frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())