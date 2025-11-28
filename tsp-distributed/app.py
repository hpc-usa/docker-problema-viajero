from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def calculate_euclidean_distance(coord1, coord2):
    """
    Calcula la distancia euclidiana entre dos coordenadas
    coord1, coord2: tuplas (x, y)
    """
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    """
    Endpoint para calcular la distancia total de una ruta
    Input JSON: {
        "cities": [
            {"name": "A", "x": 0, "y": 0},
            {"name": "B", "x": 1, "y": 1},
            ...
        ]
    }
    Output JSON: {"total_distance": valor}
    """
    try:
        data = request.get_json()
        cities = data.get('cities', [])
        
        if len(cities) < 2:
            return jsonify({"error": "Se necesitan al menos 2 ciudades"}), 400
        
        total_distance = 0.0
        
        # Calcular distancia entre cada par consecutivo de ciudades
        for i in range(len(cities) - 1):
            coord1 = (cities[i]['x'], cities[i]['y'])
            coord2 = (cities[i + 1]['x'], cities[i + 1]['y'])
            distance = calculate_euclidean_distance(coord1, coord2)
            total_distance += distance
        
        return jsonify({"total_distance": round(total_distance, 4)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para verificar que el servicio está activo"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
