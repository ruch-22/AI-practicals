import math
import heapq

# Coordinates (lat, lon) of some Indian cities (approximate)
city_coords = {
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873)
}

# Graph with distances (in km, approximate road/air distances)
graph = {
    "Delhi": {"Jaipur": 280, "Mumbai": 1400, "Kolkata": 1500, "Hyderabad": 1250},
    "Mumbai": {"Delhi": 1400, "Pune": 150, "Bangalore": 980, "Hyderabad": 710},
    "Bangalore": {"Mumbai": 980, "Chennai": 350, "Hyderabad": 570},
    "Chennai": {"Bangalore": 350, "Hyderabad": 630, "Kolkata": 1650},
    "Kolkata": {"Delhi": 1500, "Chennai": 1650},
    "Hyderabad": {"Delhi": 1250, "Mumbai": 710, "Bangalore": 570, "Chennai": 630},
    "Pune": {"Mumbai": 150, "Hyderabad": 560},
    "Jaipur": {"Delhi": 280, "Mumbai": 1150}
}

# Heuristic function: Euclidean distance between two cities (using lat, lon)
def euclidean_heuristic(city1, city2):
    x1, y1 = city_coords[city1]
    x2, y2 = city_coords[city2]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) * 111  # convert degrees → km approx

# A* Algorithm
def a_star_search(start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {city: float("inf") for city in city_coords}
    g_score[start] = 0
    
    f_score = {city: float("inf") for city in city_coords}
    f_score[start] = euclidean_heuristic(start, goal)
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            # reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], g_score[goal]
        
        for neighbor, cost in graph.get(current, {}).items():
            tentative_g = g_score[current] + cost
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + euclidean_heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return None, float("inf")

# Example usage
start_city = "Delhi"
goal_city = "Chennai"
path, distance = a_star_search(start_city, goal_city)

print(f"Shortest path from {start_city} to {goal_city}: {path}")
print(f"Total distance: {distance} km")