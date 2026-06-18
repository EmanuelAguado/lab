import sys
from PySide6.QtWidgets import (
    QApplication, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout
)
from PySide6.QtCore import QSize, Qt


class TreeWidgetInListWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal para la ventana
        main_layout = QVBoxLayout(self)

        # Crear un QListWidget para contener el QTreeWidget
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # Crear un QListWidgetItem para contener el QTreeWidget
        list_item = QListWidgetItem(self.list_widget)

        # Crear el QTreeWidget
        self.tree_widget = QTreeWidget()
        self.tree_widget.header().hide()
        self.tree_widget.setHeaderLabels(['Column 1'])

        # Desactivar los scrollbars
        self.tree_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Crear un QWidget para contener el QTreeWidget y gestionar el layout
        container_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)
        container_widget.setLayout(layout)

        # Asignar el QWidget al QListWidgetItem
        self.list_widget.setItemWidget(list_item, container_widget)

        # Botón para añadir topLevelItems
        add_button = QPushButton("Añadir Item")
        main_layout.addWidget(add_button)

        # Conectar el botón con la función de añadir elementos
        add_button.clicked.connect(lambda: self.add_top_level_item(list_item, container_widget))

    def add_top_level_item(self, list_item, container_widget):
        """Añadir un nuevo topLevelItem al QTreeWidget."""
        item_count = self.tree_widget.topLevelItemCount()
        new_item = QTreeWidgetItem([f'Item {item_count + 1}'])
        self.tree_widget.addTopLevelItem(new_item)

        # Ajustar el tamaño del QListWidgetItem según el nuevo contenido del QTreeWidget
        self.adjust_item_size(list_item, container_widget)

    def adjust_item_size(self, list_item, container_widget):
        """Actualizar el tamaño del QListWidgetItem según el contenido del QTreeWidget."""
        total_height = 20

        # Recorrer todas las filas visibles (topLevelItems) y sumar sus alturas
        for row in range(self.tree_widget.topLevelItemCount()):
            total_height += self.tree_widget.sizeHintForRow(row)  # Obtener la altura de la fila

        # Ajustar el tamaño mínimo del widget contenedor según el contenido del QTreeWidget
        container_widget.setMinimumHeight(total_height)

        # Ajustar el QListWidgetItem al tamaño del widget contenedor
        list_item.setSizeHint(QSize(self.tree_widget.frameSize().width(), total_height))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TreeWidgetInListWidget()
    window.show()

    sys.exit(app.exec())
