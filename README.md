# 🧠 AI and Seek

This project is a hide-and-seek simulation where AI agents (one seeker and two hiders) gradually develop intelligent strategies using the *Q-learning* algorithm.  
Through trial and error, agents learn about their environment and each other's behavior to maximize their chances of survival and success.

---

## 🎮 How the Simulation Works

The simulation is built on several key mechanisms that enable agents to exhibit complex behaviors:

### 🗺️ Game Environment
Agents move in a *16x16 grid world* filled with randomly generated walls.  
These walls act as both obstacles and strategic cover for seekers and hiders alike.

### 🧩 Learning Algorithm (Q-Learning)
At the core of the project lies *Q-learning*, a model-free reinforcement learning technique.  
Each agent maintains its own *Q-table (brain)*, which helps it estimate which action will yield the best outcome in a given state.

### ⚖️ Reward Shaping
To accelerate learning, agents are rewarded or penalized not only for major events (like catching or being caught) but also for smaller, incremental actions:

- *Seeker:* Gains rewards when approaching visible hiders and penalties when moving away.  
- *Hiders:* Receive rewards for increasing real (path-based) distance from the seeker and penalties for getting closer.  
  If a hider is strategically hidden *behind a wall while the seeker is nearby and line-of-sight is blocked*, it earns a bonus reward.

### 🧮 Smart Perception Systems
Advanced algorithms are used to help agents perceive the world more accurately:

- *BFS (Breadth-First Search) Distance:* Calculates the shortest walking path between agents while considering obstacles.  
- *Bresenham Line of Sight (LOS):* Checks whether a wall exists between two agents at pixel-level precision to ensure fair rewards.

---

## ✨ Features

- *Graphical Mode:* Watch the agents’ learning process and see their evolving strategies in real time.  
- *Headless Training Mode:* Run simulations without graphics to train agents faster — utilize all CPU cores and simulate thousands of rounds in seconds! (İt all depends on your cpu's power)  
- *Strategic AI:* Once trained, agents start using walls for cover, seekers develop corner-trapping tactics, and hiders discover the safest escape paths.

---

## 🚀 How to Run
### 1. Clone the repo
```
https://github.com/Handsomeskull/Al-and-Seek.git
```

### 2. Install Dependencies
```bash
pip install pygame numpy
```
## 3. Start the Simulation
```
python main.py
```
## 4. Choose Mode

When prompted, select Graphical Mode or Fast Training(Headless) Mode.
It’s recommended to start with fast training and then visualize the trained agents' performance.

---

### 🧭 Future Improvements & Contributions

This project serves as a great introduction to reinforcement learning and offers many ways to expand and experiment.
If youd like to contribute, consider doing deez(to myself and the nerd guys out in the wild):

```
1 More Agents: Add additional seekers or hiders for more complex dynamics.

2 Alternative Algorithms: Integrate advanced learning methods such as DQN (Deep Q-Networks).

3 Dynamic Maps: Generate environments with moving or evolving obstacles.

4 Save/Load Training: Save and reload Q-tables (agent “brains”) to continue training from where you left off.

5 Player Interaction: Let a human player control an agent and compete against trained AI.
```

All contributions and suggestions are welcome!
Feel free to open an issue or submit a pull request.


---

### Acknowledgments

Thank you for checking out, using, or contributing to this project!
I hope AI and Seek serves as a fun and educational resource for understanding the fundamentals of reinforcement learning....and I know the short name of the project is AAS..My A-
