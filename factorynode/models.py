class Fabric:
    id:int
    name:str

class Factory:
    id:int
    name:str
    fabric:Fabric

class Machine:
    id:int
    name:str
    fabric:Fabric
    factory:Factory

class Entity:
    id:int
    name:str
    fabric:Fabric
    factory:Factory
    machine:Machine
    status:str

class User:
    id:int
    machine:Machine