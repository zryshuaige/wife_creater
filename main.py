import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('老婆生成器')
        self.setGeometry(100, 100, 100+1440, 100+1080)

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(1920,1080)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid black;")

        self.load_button = QPushButton('生成老婆', self)
        self.load_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; }")
        self.load_button.clicked.connect(self.on_load_button_clicked)

        self.save_button = QPushButton('保存图片到本地', self)
        self.save_button.setStyleSheet("QPushButton { background-color: blue; color: white; border: none; padding: 10px; border-radius: 5px; }")
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.save_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.image_label)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_data = None

    def on_load_button_clicked(self):
        api_url = "https://api.btstu.cn/sjbz/api.php?lx=dongman&format=json"

        manager = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(api_url))
        manager.finished.connect(self.on_api_response)
        manager.get(request)

    def on_save_button_clicked(self):
        if self.image_data:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Images (*.png *.jpg *.jpeg)')
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(self.image_data)
                    print(f"Image saved to: {file_path}")
        else:
            print("No image data available to save.")

    def on_api_response(self, reply):
        if reply.error() == QNetworkReply.NoError:
            response_data = reply.readAll()
            try:
                response_json = json.loads(str(response_data, 'utf-8'))
                image_url = response_json.get('imgurl')
                if image_url:
                    self.download_image(image_url)
                else:
                    print("Image URL not found in response.")
            except json.JSONDecodeError:
                print("Failed to parse JSON response.")
        else:
            print("Network error occurred:", reply.errorString())

        reply.deleteLater()

    def download_image(self, image_url):
        manager = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(image_url))
        manager.finished.connect(self.on_image_downloaded)
        manager.get(request)

    def on_image_downloaded(self, reply):
        if reply.error() == QNetworkReply.NoError:
            self.image_data = reply.readAll()
            image = QImage()
            ok = image.loadFromData(self.image_data)

            if ok:
                pixmap = QPixmap.fromImage(image)
                self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatio))
                self.save_button.setEnabled(True)
            else:
                print("Failed to load image from data.")
        else:
            print("Network error occurred:", reply.errorString())

        reply.deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
