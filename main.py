from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from PIL import Image
import sqlite3
import os
import sys

con = sqlite3.connect('contacts.db')
cur = con.cursor()
defaultImg = "images/person.png"
person_id = None
selected_index = 0


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icons/person.png'))
        self.setWindowTitle("My Contacts")
        self.setGeometry(450, 150, 750, 600)
        self.UI()
        self.show()

    def UI(self):
        self.mainDesign()  # Setting Style, buttons. Also connecting buttons to functions
        self.layouts()  # Setting Layouts and adding buttons to the layouts
        self.getEntry()  # Display all the entries in the list widget
        self.displayFirstRecord()  # select first item in the list when program starts

    def mainDesign(self):
        self.setStyleSheet("font-size:10pt; font-family:Arial Bold;")
        self.EntryList = QListWidget()
        self.EntryList.itemSelectionChanged.connect(self.singleClick)
        self.btnNew = QPushButton("New")
        self.btnNew.clicked.connect(self.addEntry)
        self.btnUpdate = QPushButton("Update")
        self.btnUpdate.clicked.connect(self.updateEntry)
        self.btnDelete = QPushButton("Delete")
        self.btnDelete.clicked.connect(self.deleteEntry)

    def layouts(self):
        # Setting layouts
        self.mainLayout = QHBoxLayout()
        self.leftLayout = QFormLayout()
        self.rightMainLayout = QVBoxLayout()
        self.rightTopLayout = QHBoxLayout()
        self.rightBottomLayout = QHBoxLayout()

        # Adding Child Layouts to main layout
        self.rightMainLayout.addLayout(self.rightTopLayout)
        self.rightMainLayout.addLayout(self.rightBottomLayout)
        self.mainLayout.addLayout(self.leftLayout, 40)
        self.mainLayout.addLayout(self.rightMainLayout, 60)

        # Adding Widgets to Layouts
        self.rightTopLayout.addWidget(self.EntryList)
        self.rightBottomLayout.addWidget(self.btnNew)
        self.rightBottomLayout.addWidget(self.btnDelete)
        self.rightBottomLayout.addWidget(self.btnUpdate)

        # Setting Main Window Layout
        self.setLayout(self.mainLayout)

    def addEntry(self):
        self.newEntry = AddEntry(self)

    def getEntry(self):
        query = "SELECT _id, name, surname FROM contacts"
        entries = cur.execute(query).fetchall()
        for entry in entries:
            self.EntryList.addItem(str(entry[0]) + "-" + str(entry[1]) + " " + str(entry[2]))

    def refreshList(self):
        self.EntryList.blockSignals(True)
        self.EntryList.clear()
        self.EntryList.blockSignals(False)
        self.getEntry()

    def displayFirstRecord(self):
        self.EntryList.setCurrentRow(0)

    def displayUpdatedRecord(self):
        global selected_index
        self.EntryList.setCurrentRow(selected_index)

    def singleClick(self):
        global person_id
        global selected_index
        for i in reversed(range(self.leftLayout.count())):
            widget = self.leftLayout.takeAt(i).widget()

            if widget:
                widget.deleteLater()

        entry = self.EntryList.currentItem().text()
        person_id = entry.split("-")[0]
        query = "SELECT * FROM contacts WHERE _id = ?"
        person = cur.execute(query, (person_id,)).fetchone()
        img = QLabel()
        img.setPixmap(QPixmap(person[5]))
        name = QLabel(person[1])
        surname = QLabel(person[2])
        phone = QLabel(person[3])
        email = QLabel(person[4])
        address = QLabel(person[6])
        self.leftLayout.setVerticalSpacing(20)
        self.leftLayout.addRow("", img)
        self.leftLayout.addRow("Name:", name)
        self.leftLayout.addRow("Surname: ", surname)
        self.leftLayout.addRow("Phone: ", phone)
        self.leftLayout.addRow("Email:", email)
        self.leftLayout.addRow("Address: ", address)
        selected_index = self.EntryList.currentRow()


    def deleteEntry(self):
        global person_id
        if self.EntryList.selectedItems():
            person = self.EntryList.currentItem().text()
            person_id = person.split("-")[0]
            mbox = QMessageBox.question(self, "Warning", "Are you sure you want to delete this entry?",
                                        QMessageBox.Yes, QMessageBox.No)
            if mbox == QMessageBox.Yes:
                try:
                    query = "DELETE FROM contacts WHERE _id=?"
                    cur.execute(query, (person_id,))
                    con.commit()
                    QMessageBox.information(self, "Success!", "Entry was deleted")
                    self.refreshList()
                    self.displayFirstRecord()
                except:
                    QMessageBox.information(self, "Warning!", "Entry was not deleted")
        else:
            QMessageBox.information(self, "Warning!", "Please select an entry to delete")

    def updateEntry(self):
        global person_id
        if self.EntryList.selectedItems():
            person = self.EntryList.currentItem().text()
            person_id = person.split("-")[0]
            self.updateWindows = UpdateEntry(self)
        else:
            QMessageBox.information(self, "Warning!", "Please select an entry to update")


class UpdateEntry(QWidget):
    def __init__(self, main: Main):
        super().__init__()
        self.main = main
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("Update Contact")
        self.setGeometry(450, 180, 520, 600)
        self.setWindowIcon(QIcon('icons/person.png'))
        self.UI()
        self.show()

    def UI(self):
        self.getPerson()
        self.mainDesign()
        self.layouts()

    def closeEvent(self, event):
        global defaultImg
        self.main.refreshList()
        self.main.displayUpdatedRecord()

    def getPerson(self):
        global person_id
        query = "SELECT * FROM contacts WHERE _id=?"
        self.entry = cur.execute(query, (person_id, )).fetchone()

    def mainDesign(self):
        ### Top Layout Widgets ###
        self.setStyleSheet("background-color: white; font-size:12pt;font-family:Arial")
        self.title = QLabel("Update Person")
        self.title.setStyleSheet('font-size: 25pt; font-family:Arial Bold')
        self.imgAdd = QLabel()
        self.imgAdd.setPixmap(QPixmap(self.entry[5]))

        ### bottom layout widgets ###
        self.nameLbl = QLabel("Name:")
        self.nameEntry = QLineEdit()
        self.nameEntry.setText(self.entry[1])

        self.surnameLbl = QLabel("Surname:")
        self.surnameEntry = QLineEdit()
        self.surnameEntry.setText(self.entry[2])

        self.phoneLbl = QLabel("Phone:")
        self.phoneEntry = QLineEdit()
        self.phoneEntry.setText(self.entry[3])

        self.emailLbl = QLabel("Email:")
        self.emailEntry = QLineEdit()
        self.emailEntry.setText(self.entry[4])

        self.imgLbl = QLabel("Picture:")
        self.imgButton = QPushButton("Browse")
        self.imgButton.setStyleSheet("background-color:orange; font-size:10pt;"
                                     " font-family:Arial Bold; border-style:inset;border-width: 2px")
        self.imgButton.clicked.connect(self.uploadImage)

        self.addressLbl = QLabel("Address: ")
        self.addressEditor = QTextEdit()
        self.addressEditor.setText(self.entry[6])

        self.addButton = QPushButton("Update")
        self.addButton.setStyleSheet("background-color:orange; font-size:10pt;"
                                     " font-family:Arial Bold; border-style:inset;border-width: 2px")
        self.addButton.clicked.connect(self.updateEntry)

    def layouts(self):
        # Creating main layouts
        self.mainLayout = QVBoxLayout()
        self.topLayout = QVBoxLayout()
        self.bottomLayout = QFormLayout()
        # creating sub layouts
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.bottomLayout)

        # adding widgets to layouts
          # Top Layout #
        self.topLayout.addStretch()
        self.topLayout.addWidget(self.title)
        self.topLayout.addWidget(self.imgAdd)
        self.topLayout.addStretch()
        self.topLayout.setContentsMargins(110, 20, 10, 30)  #Left, top, right, bottom
          # Bottom Layout #
        self.bottomLayout.addRow(self.nameLbl, self.nameEntry)
        self.bottomLayout.addRow(self.surnameLbl, self.surnameEntry)
        self.bottomLayout.addRow(self.phoneLbl, self.phoneEntry)
        self.bottomLayout.addRow(self.emailLbl, self.emailEntry)
        self.bottomLayout.addRow(self.imgLbl, self.imgButton)
        self.bottomLayout.addRow(self.addressLbl, self.addressEditor)
        self.bottomLayout.addRow("", self.addButton)

        # setting main layout for window
        self.setLayout(self.mainLayout)

    def uploadImage(self):
        global defaultImg
        size = (128, 128)
        self.fileName, ok = QFileDialog.getOpenFileName(self, "Upload Image", "", "Image Files(*.jpg *.png)")

        if ok:
            defaultImg = self.fileName
            img = Image.open(defaultImg)
            img = img.resize(size)
            defaultImg = "images/" + os.path.basename(self.fileName)
            img.save(defaultImg)
            self.imgAdd.setPixmap(QPixmap(defaultImg))

    def updateEntry(self):
        global defaultImg
        global person_id

        name = self.nameEntry.text()
        surname = self.surnameEntry.text()
        phone = self.phoneEntry.text()
        email = self.emailEntry.text()
        img = defaultImg
        address = self.addressEditor.toPlainText()

        if name and surname and phone:
            try:
                query = "UPDATE contacts SET name = ?, surname = ?, phone = ?, email = ?, img = ?," \
                       " address = ? WHERE _id = ?"
                cur.execute(query, (name, surname, phone, email, img, address, person_id))
                con.commit()
                QMessageBox.information(self, "Success!", "Entry has been updated")
                self.close()
            except Exception as e:
                QMessageBox.information(self, "Warning!", "Entry has not been updated")
        else:
            QMessageBox.information(self, "Warning!", "Fields can not be empty")


class AddEntry(QWidget):
    def __init__(self, main: Main):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.main = main
        self.setWindowTitle("Add Contacts")
        self.setGeometry(450, 180, 520, 600)
        self.setWindowIcon(QIcon('icons/person.png'))
        self.UI()
        self.show()

    def UI(self):
        self.mainDesign()
        self.layouts()

    def closeEvent(self, event):
        self.main.refreshList()

    def mainDesign(self):
        # Top Layout Widgets
        global defaultImg
        defaultImg = "images/person.png"
        self.setStyleSheet("background-color: white; font-size:12pt;font-family:Arial")
        self.title = QLabel("Add Person")
        self.title.setStyleSheet('font-size: 25pt; font-family:Arial Bold')
        self.imgAdd = QLabel()
        self.imgAdd.setPixmap(QPixmap(defaultImg))

        # bottom layout widgets
        self.nameLbl = QLabel("Name:")
        self.nameEntry = QLineEdit()
        self.nameEntry.setPlaceholderText("Enter contact Name")

        self.surnameLbl = QLabel("Surname:")
        self.surnameEntry = QLineEdit()
        self.surnameEntry.setPlaceholderText("Enter contact Surname")

        self.phoneLbl = QLabel("Phone:")
        self.phoneEntry = QLineEdit()
        self.phoneEntry.setPlaceholderText("Enter contact phone number")

        self.emailLbl = QLabel("Email:")
        self.emailEntry = QLineEdit()
        self.emailEntry.setPlaceholderText("Enter contact Email")

        self.imgLbl = QLabel("Picture:")
        self.imgButton = QPushButton("Browse")
        self.imgButton.setStyleSheet("background-color:orange; font-size:10pt;"
                                     " font-family:Arial Bold; border-style:inset;border-width: 2px")
        self.imgButton.clicked.connect(self.uploadImage)

        self.addressLbl = QLabel("Address: ")
        self.addressEditor = QTextEdit()

        self.addButton = QPushButton("Add")
        self.addButton.setStyleSheet("background-color:orange; font-size:10pt;"
                                     " font-family:Arial Bold; border-style:inset;border-width: 2px")
        self.addButton.clicked.connect(self.addEntry)

    def layouts(self):
        # Creating main layouts
        self.mainLayout = QVBoxLayout()
        self.topLayout = QVBoxLayout()
        self.bottomLayout = QFormLayout()
        # creating sub layouts
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addLayout(self.bottomLayout)

        # adding widgets to layouts
          # Top Layout
        self.topLayout.addStretch()
        self.topLayout.addWidget(self.title)
        self.topLayout.addWidget(self.imgAdd)
        self.topLayout.addStretch()
        self.topLayout.setContentsMargins(110, 20, 10, 30)  # Left, top, right, bottom
          # Bottom Layout
        self.bottomLayout.addRow(self.nameLbl, self.nameEntry)
        self.bottomLayout.addRow(self.surnameLbl, self.surnameEntry)
        self.bottomLayout.addRow(self.phoneLbl, self.phoneEntry)
        self.bottomLayout.addRow(self.emailLbl, self.emailEntry)
        self.bottomLayout.addRow(self.imgLbl, self.imgButton)
        self.bottomLayout.addRow(self.addressLbl, self.addressEditor)
        self.bottomLayout.addRow("", self.addButton)

        # setting main layout for window
        self.setLayout(self.mainLayout)

    def uploadImage(self):
        global defaultImg
        size = (128, 128)
        self.fileName, ok = QFileDialog.getOpenFileName(self, "Upload Image", "", "Image Files(*.jpg *.png)")

        if ok:
            defaultImg = self.fileName
            img = Image.open(defaultImg)
            img = img.resize(size)
            defaultImg = "images/" + os.path.basename(defaultImg)
            img.save(defaultImg)
            self.imgAdd.setPixmap(QPixmap(defaultImg))


    def addEntry(self):
        global defaultImg

        name = self.nameEntry.text()
        surname = self.surnameEntry.text()
        phone = self.phoneEntry.text()
        email = self.emailEntry.text()
        img = defaultImg
        address = self.addressEditor.toPlainText()

        if name and surname and phone:
            try:
                query = "INSERT INTO contacts (name, surname, phone, email, img, address) VALUES(?,?,?,?,?,?)"
                cur.execute(query, (name, surname, phone, email, img, address))
                con.commit()
                QMessageBox.information(self, "Success!", "Person has been added")
                self.close()
            except:
                QMessageBox.information(self, "Warning!", "Person has not been added")
        else:
            QMessageBox.information(self, "Warning!", "Fields can not be empty")


def main():
    APP = QApplication(sys.argv)
    window = Main()
    sys.exit(APP.exec_())


if __name__ == "__main__":
    main()
