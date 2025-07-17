
# 🗺️ Route Optimizer

A Python-based route optimization tool that helps you plan the most efficient path to visit multiple locations using Google Maps API and Dijkstra’s Algorithm.

## 🚀 Features

- 🔍 Automatically finds the shortest route between multiple destinations  
- 📍 Integrates with Google Maps API to fetch real-time distance data  
- ⚡ Uses Dijkstra’s algorithm for accurate shortest path calculation  
- 💻 Easy to customize for different input locations and city-based routes

## 🛠️ Tech Stack

- **Python**  
- **Google Maps API**  
- **Dijkstra’s Algorithm**  
- **NetworkX** *(optional, for visualization/graph representation)*

## 📦 Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/your-username/route-optimizer.git
   cd route-optimizer
   ```

2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Google Maps API key in a `.env` or config file

## 📌 Usage

```bash
python route_optimizer.py
```

- Input your current location and list of places to visit
- The script fetches distances using Google Maps API
- It calculates and displays the shortest route

## 🧠 Algorithm Logic

- Constructs a weighted graph using the Distance Matrix from Google Maps
- Applies Dijkstra’s algorithm to determine the optimal visiting sequence

## 🧪 Sample Input

```
Start: RSET, Kochi
Places: Lulu Mall, Infopark, Marine Drive, Fort Kochi
```

## 📤 Output Example

```
Optimized Order:
1. RSET
2. Infopark
3. Lulu Mall
4. Marine Drive
5. Fort Kochi
```
