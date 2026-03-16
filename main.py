import sys
import socket
import struct
import pickle
import cv2

# PyQt Stuff
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QImage, QPixmap

# Designer Stuff
from app import Ui_MainWindow  

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Button connections
        self.eStop.clicked.connect(self.handle_estop)
        self.cStop.clicked.connect(self.handle_cstop)
        self.Continue.clicked.connect(self.handle_continue)

        # NETWORK THREAD ONLY (Removed the conflicting local webcam thread)
        self.thread = VideoThreadNetwork()
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

    # RESTORED: Prevents the "Abort trap: 6" crash on exit
    def closeEvent(self, event):
        print("Closing application, stopping video thread...")
        self.thread.stop()
        event.accept()

class VideoThreadNetwork(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = True  # Flag to control the loop safely

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_ip = '127.0.0.1' 
        port = 9999

        try:
            client_socket.connect((host_ip, port))
        except Exception as e:
            print(f"Could not connect to stream: {e}")
            return 

        data = b""
        payload_size = struct.calcsize("Q") 

        # RESTORED: Checks the run flag instead of 'while True:'
        while self._run_flag: 
            try:
                while len(data) < payload_size and self._run_flag:
                    client_socket.settimeout(1.0) # Prevents socket from freezing on shutdown
                    try:
                        packet = client_socket.recv(4096) 
                        if not packet: break
                        data += packet
                    except socket.timeout:
                        continue 
                
                if not data or not self._run_flag: break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size and self._run_flag:
                    try:
                        data += client_socket.recv(4096)
                    except socket.timeout:
                        continue
                    
                if not self._run_flag: break

                frame_data = data[:msg_size]
                data = data[msg_size:] 

                frame = pickle.loads(frame_data)
                
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                
                convert_to_Qt_Format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                qt_frame = convert_to_Qt_Format.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

                self.change_pixmap_signal.emit(qt_frame)
                
            except Exception as e:
                print(f"Network stream ended or errored: {e}")
                break
                
        client_socket.close()

    def stop(self):
        self._run_flag = False
        self.wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())