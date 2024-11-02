import pygame
import sys
import threading
import time
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import (
    QSettings,
    QUrl, 
    QEvent,
    Qt
)
from PySide6.QtWidgets import (
    QApplication, 
    QFileDialog, 
    QHBoxLayout,
    QLabel, 
    QPushButton, 
    QSlider,
    QSpinBox, 
    QVBoxLayout,
    QWidget, 
)

class SoundPlayerApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        self.setWindowTitle("Sound Player")
        self.setGeometry(200, 200, 300, 200)
        
        self.settings = QSettings("SoundReminder", "SR App")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.sound_file = self.settings.value("sound_file", None)
        self.interval = int(self.settings.value("interval", 15))
        
        self.is_playing = False
        self.thread = None
        
        # UI Setup
        layout = QVBoxLayout()

        # Sound file selector
        self.file_label = QLabel("No file selected")
        file_button = QPushButton("Select Sound File")
        file_button.clicked.connect(self.select_sound_file)
        self.file_label.setText(self.sound_file.split("/")[-1] if self.sound_file else "No file selected")

        # Interval selector
        interval_label = QLabel("Interval (seconds):")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(5, 300)
        self.interval_spinbox.setValue(self.interval)
        self.interval_spinbox.valueChanged.connect(self.set_interval)
        
        # Play/Stop Button
        self.toggle_button = QPushButton("Start Playing")
        self.toggle_button.clicked.connect(self.toggle_playing)
        self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white;")

        # Layouts
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_button)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)

        # Add "Create Audio" button
        create_audio_button = QPushButton("Create New Audio")
        create_audio_button.clicked.connect(self.open_ttsmp3)
        
        # Add to the layout
        layout.addLayout(file_layout)
        layout.addLayout(interval_layout)
        layout.addWidget(create_audio_button)
        layout.addWidget(self.toggle_button)
        
        # Volume Slider
        self.volume_slider = QSlider()
        self.volume_slider.setOrientation(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)  # Volume range from 0 to 100
        self.volume_slider.setValue(50)  # Default volume set to 50%
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Add the slider to the layout
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)
        
        self.set_volume(float(self.settings.value("volume", 50)), startup=True)
        self.set_dark_mode()

    def select_sound_file(self) -> None:
        file_dialog = QFileDialog(self)
        self.sound_file, _ = file_dialog.getOpenFileName(self, "Select Sound File", "", "Sound Files (*.mp3 *.wav)")
        if self.sound_file:
            self.file_label.setText(self.sound_file.split("/")[-1])
            self.settings.setValue("sound_file", self.sound_file)
        else:
            self.file_label.setText("No file selected")
    
    def set_interval(self, value: int) -> None:
        self.interval = value
        self.settings.setValue("interval", self.interval)

    def set_volume(self, value: int, startup: bool = False) -> None:
        if startup is True:
            self.volume_slider.setValue(value)
            
        volume = value / 100  # Convert slider value to range 0.0 - 1.0
        pygame.mixer.music.set_volume(volume)
        self.settings.setValue("volume", value)
    
    def play_sound_periodically(self) -> None:
        while self.is_playing:
            if self.sound_file:
                try:
                    pygame.mixer.music.load(self.sound_file)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Error playing sound: {e}")
            for _ in range(self.interval):
                if self.is_playing is False:
                    break
                time.sleep(1)

    def set_dark_mode(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e; 
                color: #ffffff;
            }
            QPushButton {
                background-color: #444444; 
                color: #ffffff;
                border: 1px solid #666666;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555555; 
            }
            QLabel {
                color: #ffffff;
            }
            QSpinBox {
                background-color: #444444; 
                color: #ffffff; 
                border: 1px solid #666666;
            }
        """)
        
    def toggle_playing(self) -> None:
        if self.is_playing:
            self.is_playing = False
            self.toggle_button.setText("Start Playing")
            self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white;")
            pygame.mixer.music.stop()
        else:
            if self.sound_file:
                self.is_playing = True
                self.toggle_button.setText("Stop Playing")
                self.thread = threading.Thread(target=self.play_sound_periodically)
                self.toggle_button.setStyleSheet("background-color: #F44336; color: white;")
                self.thread.start()
            else:
                self.file_label.setText("Please select a sound file")
    
    def open_ttsmp3(self) -> None:
        QDesktopServices.openUrl(QUrl("https://ttsmp3.com/"))

    def closeEvent(self, event: QEvent) -> None:
        self.is_playing = False  # Stop the sound loop
        if self.thread and self.thread.is_alive():
            self.thread.join()  # Wait for the thread to finish
            
        pygame.mixer.music.stop()  # Ensure playback stops
        event.accept()  # Allow the window to close

# Main app execution
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SoundPlayerApp()
    window.show()

    sys.exit(app.exec())
