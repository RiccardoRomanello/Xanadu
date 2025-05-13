import pennylane as qml
from transform.routing_transform import apply_routing
import networkx as nx
from functools import partial


# connectivity = {
#    0 : {1},
#    1 : {0, 2},
#    2 : {1, 3, 5},
#    3 : {2, 5},
#    4 : {5},
#    5 : {2, 3, 4} 
#}

connectivity = {
    0 : {1},
    1 : {0, 2},
    2 : {1, 3},
    3 : {2}
}

dev = qml.device("default.qubit", wires=6)

@qml.qnode(dev)
def circuit():
    qml.PauliX(wires=0)
    qml.CNOT(wires=[0, 1])
    qml.PauliX(wires=0)
    return qml.state()

print("Circuit before compilation")
print(qml.draw(circuit)())

circuit()
compiled, measurements, qubits = apply_routing(circuit._tape, nx.Graph(connectivity), "random")
second_device = qml.device("default.qubit", wires=qubits)
@qml.qnode(second_device)
def new_circuit():
    for op in compiled:
        qml.apply(op)
    return qml.state()

print("Circuit after compilation")
print(qml.draw(new_circuit)())