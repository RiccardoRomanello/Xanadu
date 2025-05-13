# Riccardo Romanello – Code Assignment

This assignment requires compiling a quantum circuit according to a given topology.

The first assumption we make is the following: **the circuit has already been decomposed into Clifford+T gates**.  
Note that this assumption can be easily relaxed by assuming the circuit is already compiled into this class of gates.

A less strict assumption would be that the circuit is composed of just single and two-qubit gates. However, Clifford+T is mentioned due to its popularity.

---

## 🧠 The Task in a Nutshell

We formalize the task as follows:  
We are given a circuit $\mathcal{C}$, composed solely of single- and two-qubit operations.  
Additionally, we are given a topology $G = (V, E)$, which imposes constraints on the execution of two-qubit gates (single-qubit gates are unaffected by $G$).

The graph $G$ represents the physical connectivity of the quantum hardware.  
Thus, logical qubits (those in the circuit) must be mapped to physical qubits (nodes of $G$).  
We must create a **bijection** between the logical qubits in $\mathcal{C}$ and the nodes in $G$.

Once this is done, we compile $\mathcal{C}$ to adhere to $G$. In particular, whenever a two-qubit gate between $q_i$ and $q_j$ is to be executed, we must ensure the nodes containing $q_i$ and $q_j$ are adjacent.  
If so, the CNOT can proceed. Otherwise, we must apply a series of **SWAP** gates to move the qubits within the graph until they are adjacent.

Clearly, the goal is to minimize the number of SWAP gates added.

The overall problem reduces to two **non-independent** steps:
1. **Mapping**
2. **Routing**

- **Mapping** is the process of finding a bijection $\varphi$ between the logical qubits in $\mathcal{C}$ and the nodes in $G$.
- **Routing** uses $\varphi$ and a list of CNOTs $C$ to add the SWAPs required to execute all CNOTs.

Roughly:
1. Let $(c, t)$ be the next CNOT in $C$.
2. Let $u = \varphi(c)$ and $v = \varphi(t)$.
3. If $\{u, v\} \in E$, execute the CNOT and proceed.
4. Else, modify $\varphi$ so that $c$ and $t$ are moved to adjacent nodes.

---

## ✅ Assumptions

- The topology graph is undirected and consists of a single connected component.
- The $n$ nodes in $G$ are labeled from $0$ to $n-1$.
- The number of qubits in $\mathcal{C}$ must be less than or equal to the number of nodes in $G$.  
  If there are fewer qubits, ancilla qubits are added to match the counts.

---

## 🗺️ Mapping

The mapping phase uses a base class that defines a `compute_mapping` method.  
Each strategy implements this method differently.

### Strategies:

#### 🔹 Random Mapping
Shuffles the identity mapping to randomly assign logical qubits to physical nodes.

#### 🔹 Majority Mapping
Uses a max-heap to prioritize:
- Graph nodes with the highest number of neighbors.
- Logical qubits that interact with the most others.

It pops the most connected node and qubit pair until all logical qubits are mapped (padded as needed).

#### 🔹 Max Interacting Pairs
The most complex strategy.

- Defines a *free* node/qubit as one not yet mapped.
- Chooses the free node with the most free neighbors.
- For each free qubit $q$, computes the set of up to $d$ free qubits $q_1, ..., q_k$ that maximize: ``` \sum_{i = 1}^{k}{\delta(q, q_i)}```
  where $\delta(q', q'')$ is the number of CNOTs between $q'$ and $q''$ (cannot really make that mathmode to compile as Latex).

- This identifies the qubit that can **use** the connections of the selected node most effectively.
- The top-k interacting qubits are recursively mapped to the neighbors of the chosen node.

This process continues until all qubits are mapped.

---

## 🔁 Routing

With a mapping in place, routing ensures all CNOTs can be executed under the topology.

- If the mapped qubits for a CNOT are adjacent: execute.
- If not: insert SWAP gates to bring them together.

### Strategy

Three movement strategies are considered:
1. Move the target toward the control.
2. Move the control toward the target.
3. Move both halfway.

Paths are computed using Floyd-Warshall on the unchanging graph $G$.

### Lookahead Heuristic

A lookahead value `l` is used to inspect the next `l` CNOTs:
- If neither control nor target is reused soon → choose randomly.
- If control is used significantly more → move target.
- If target is used significantly more → move control.
- Otherwise → move both halfway.

---

## 🧩 Overall Process

1. Select a mapping strategy to compute $\varphi$.
2. Simulate routing for the first `k` CNOTs using $\varphi` to get an updated mapping $\varphi'`.
3. Compare the number of swaps:
   - If $\varphi'$ performs better, use it.
   - Otherwise, stick with $\varphi`.
4. Apply the final routing step to produce the transformed circuit with inserted SWAPs.

---

A notebook with a demo has been provided. Notice that the whole process applied to the circuit is logged in files that can be found in the log directory. 
