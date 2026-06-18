from PySide6.QtWidgets import QLineEdit

from ui.node import Node, NodeContent

ROOT = "C:/"

class BaseManchineContent(NodeContent):
    def __init__(self,node):
        super().__init__(node)
        self.out_to_in = {"INPUT":"OUTPUT"}
        # self.out_to_in = {"path":"path",
        #                   "file":"file"}

    def create_widgets(self):
        pass
        self.add_content("INPUT", QLineEdit())
        self.add_content("OUTPUT", QLineEdit())

    def core(self):
        try:
        #     if self._data["INPUT"].text() not in ["","None"]:
        #         self._out_data["path"]="/".join([self._data["path"].text(),self._data["task_name"].text()])
        #     else:
        #         self._out_data["path"]="".join([ROOT,self._data["task_name"].text()])

        #     self._out_data["signal"]= self.node.node_widget.custom_name.toPlainText()
            super().core()
        except:
            self.on_recursion("path")
        
class BaseManchine(Node):
    def __init__(self, scene, title="Undefined Node",inputs=["INPUT"],outputs=["OUTPUT"]):
        super().__init__(scene,title,inputs,outputs)

    def init_contents(self):
        return BaseManchineContent(self)
