# Form implementation generated from reading ui file 'source\view.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(905, 589)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 110, 161, 16))
        self.label.setObjectName("label")
        self.doc_textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.doc_textEdit.setGeometry(QtCore.QRect(214, 130, 361, 401))
        self.doc_textEdit.setReadOnly(True)
        self.doc_textEdit.setObjectName("doc_textEdit")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(214, 110, 81, 16))
        self.label_2.setObjectName("label_2")
        self.link_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.link_label.setGeometry(QtCore.QRect(440, 110, 131, 20))
        self.link_label.setObjectName("link_label")
        self.add_pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.add_pushButton.setGeometry(QtCore.QRect(10, 540, 111, 23))
        self.add_pushButton.setObjectName("add_pushButton")
        self.del_pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.del_pushButton.setGeometry(QtCore.QRect(260, 540, 121, 23))
        self.del_pushButton.setObjectName("del_pushButton")
        self.groupBox = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 491, 91))
        self.groupBox.setObjectName("groupBox")
        self.label_4 = QtWidgets.QLabel(parent=self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(10, 20, 171, 16))
        self.label_4.setObjectName("label_4")
        self.search_lineEdit = QtWidgets.QLineEdit(parent=self.groupBox)
        self.search_lineEdit.setGeometry(QtCore.QRect(10, 40, 341, 31))
        self.search_lineEdit.setObjectName("search_lineEdit")
        self.search_pushButton = QtWidgets.QPushButton(parent=self.groupBox)
        self.search_pushButton.setGeometry(QtCore.QRect(370, 40, 111, 31))
        self.search_pushButton.setObjectName("search_pushButton")
        self.chat_textEdit = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.chat_textEdit.setGeometry(QtCore.QRect(600, 300, 291, 201))
        self.chat_textEdit.setReadOnly(True)
        self.chat_textEdit.setObjectName("chat_textEdit")
        self.label_6 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(600, 280, 47, 13))
        self.label_6.setObjectName("label_6")
        self.send_pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.send_pushButton.setGeometry(QtCore.QRect(810, 510, 81, 23))
        self.send_pushButton.setAutoFillBackground(False)
        self.send_pushButton.setObjectName("send_pushButton")
        self.chat_lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.chat_lineEdit.setGeometry(QtCore.QRect(600, 510, 201, 20))
        self.chat_lineEdit.setObjectName("chat_lineEdit")
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(600, 20, 141, 241))
        self.groupBox_2.setObjectName("groupBox_2")
        self.volume_verticalSlider = QtWidgets.QSlider(parent=self.groupBox_2)
        self.volume_verticalSlider.setGeometry(QtCore.QRect(90, 70, 22, 141))
        self.volume_verticalSlider.setProperty("value", 50)
        self.volume_verticalSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.volume_verticalSlider.setObjectName("volume_verticalSlider")
        self.speed_verticalSlider = QtWidgets.QSlider(parent=self.groupBox_2)
        self.speed_verticalSlider.setGeometry(QtCore.QRect(10, 70, 22, 141))
        self.speed_verticalSlider.setProperty("value", 50)
        self.speed_verticalSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.speed_verticalSlider.setObjectName("speed_verticalSlider")
        self.voice_type_comboBox = QtWidgets.QComboBox(parent=self.groupBox_2)
        self.voice_type_comboBox.setGeometry(QtCore.QRect(10, 40, 121, 22))
        self.voice_type_comboBox.setObjectName("voice_type_comboBox")
        self.label_7 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_7.setGeometry(QtCore.QRect(10, 20, 47, 13))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_8.setGeometry(QtCore.QRect(10, 220, 61, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.label_9.setGeometry(QtCore.QRect(70, 220, 61, 16))
        self.label_9.setObjectName("label_9")
        self.change_pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.change_pushButton.setGeometry(QtCore.QRect(130, 540, 121, 23))
        self.change_pushButton.setObjectName("change_pushButton")
        self.voice_pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.voice_pushButton.setGeometry(QtCore.QRect(780, 540, 111, 41))
        self.voice_pushButton.setObjectName("voice_pushButton")
        self.line = QtWidgets.QFrame(parent=self.centralwidget)
        self.line.setGeometry(QtCore.QRect(574, 20, 20, 551))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.docs_listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        self.docs_listWidget.setGeometry(QtCore.QRect(10, 131, 191, 401))
        self.docs_listWidget.setObjectName("docs_listWidget")
        self.tts_pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.tts_pushButton.setGeometry(QtCore.QRect(390, 540, 181, 23))
        self.tts_pushButton.setObjectName("tts_pushButton")
        self.commands_listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        self.commands_listWidget.setGeometry(QtCore.QRect(750, 41, 141, 221))
        self.commands_listWidget.setObjectName("commands_listWidget")
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(750, 20, 141, 16))
        self.label_3.setObjectName("label_3")
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(590, 530, 181, 51))
        self.groupBox_3.setObjectName("groupBox_3")
        self.ru_radioButton = QtWidgets.QRadioButton(parent=self.groupBox_3)
        self.ru_radioButton.setGeometry(QtCore.QRect(10, 20, 91, 17))
        self.ru_radioButton.setObjectName("ru_radioButton")
        self.en_radioButton = QtWidgets.QRadioButton(parent=self.groupBox_3)
        self.en_radioButton.setGeometry(QtCore.QRect(90, 20, 91, 17))
        self.en_radioButton.setObjectName("en_radioButton")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "VoiceHelper"))
        self.label.setText(_translate("MainWindow", "Список документов"))
        self.label_2.setText(_translate("MainWindow", "Содержимое"))
        self.link_label.setText(_translate("MainWindow", "Ссылка на документ"))
        self.add_pushButton.setText(_translate("MainWindow", "Добавить"))
        self.del_pushButton.setText(_translate("MainWindow", "Удалить"))
        self.groupBox.setTitle(_translate("MainWindow", "Фильтр"))
        self.label_4.setText(_translate("MainWindow", "Ключевые слова"))
        self.search_pushButton.setText(_translate("MainWindow", "Поиск"))
        self.label_6.setText(_translate("MainWindow", "Чат"))
        self.send_pushButton.setText(_translate("MainWindow", "Отправить"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Настройки голоса"))
        self.label_7.setText(_translate("MainWindow", "Голос"))
        self.label_8.setText(_translate("MainWindow", "Скорость"))
        self.label_9.setText(_translate("MainWindow", "Громкость"))
        self.change_pushButton.setText(_translate("MainWindow", "Изменить"))
        self.voice_pushButton.setText(_translate("MainWindow", "Упр. голосом"))
        self.tts_pushButton.setText(_translate("MainWindow", "Воспроизвести"))
        self.label_3.setText(_translate("MainWindow", "Доступные команды"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Выбор языка общения"))
        self.ru_radioButton.setText(_translate("MainWindow", "Русский"))
        self.en_radioButton.setText(_translate("MainWindow", "Английский"))