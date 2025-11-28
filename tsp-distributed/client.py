import requests
import itertools
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Definir las ciudades con sus coordenadas
CITIES = [
    {"name": "A", "x": 0, "y": 0},
    {"name": "B", "x": 10, "y": 5},
    {"name": "C", "x": 15, "y": 15},
    {"name": "D", "x": 5, "y": 20},
    {"name": "E", "x": 20, "y": 10}
]

API_URL = "http://localhost:5000/calculate_distance"

def calculate_route_distance(route):
    """
    Envía una ruta al servidor y obtiene su distancia total
    """
    try:
        response = requests.post(API_URL, json={"cities": route}, timeout=5)
        if response.status_code == 200:
            return response.json()['total_distance']
        else:
            print(f"Error en respuesta: {response.status_code}")
            return float('inf')
    except Exception as e:
        print(f"Error en la petición: {e}")
        return float('inf')

def brute_force_sequential():
    """
    Método secuencial: prueba todas las permutaciones una por una
    """
    print("=== BÚSQUEDA SECUENCIAL ===")
    start_time = time.time()
    
    best_distance = float('inf')
    best_route = None
    total_permutations = 0
    
    # Generar todas las permutaciones posibles
    for perm in itertools.permutations(CITIES):
        route = list(perm)
        distance = calculate_route_distance(route)
        total_permutations += 1
        
        if distance < best_distance:
            best_distance = distance
            best_route = route
        
        # Mostrar progreso cada 10 permutaciones
        if total_permutations % 10 == 0:
            print(f"Procesadas {total_permutations} rutas...")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n--- RESULTADOS SECUENCIALES ---")
    print(f"Total de permutaciones evaluadas: {total_permutations}")
    print(f"Tiempo total: {elapsed_time:.2f} segundos")
    print(f"Mejor distancia: {best_distance:.4f}")
    print(f"Mejor ruta: {' -> '.join([city['name'] for city in best_route])}")
    print(f"Velocidad: {total_permutations/elapsed_time:.2f} rutas/segundo\n")
    
    return best_route, best_distance, elapsed_time

def brute_force_parallel(max_workers=10):
    """
    Método paralelo: envía múltiples peticiones simultáneamente
    """
    print(f"=== BÚSQUEDA PARALELA (con {max_workers} workers) ===")
    start_time = time.time()
    
    best_distance = float('inf')
    best_route = None
    total_permutations = 0
    
    # Generar todas las permutaciones
    all_permutations = list(itertools.permutations(CITIES))
    
    # Usar ThreadPoolExecutor para paralelizar las peticiones
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear un diccionario de futures
        future_to_route = {
            executor.submit(calculate_route_distance, list(perm)): list(perm)
            for perm in all_permutations
        }
        
        # Procesar los resultados conforme se completan
        for future in as_completed(future_to_route):
            route = future_to_route[future]
            try:
                distance = future.result()
                total_permutations += 1
                
                if distance < best_distance:
                    best_distance = distance
                    best_route = route
                
                # Mostrar progreso cada 10 permutaciones
                if total_permutations % 10 == 0:
                    print(f"Procesadas {total_permutations} rutas...")
                    
            except Exception as e:
                print(f"Error procesando ruta: {e}")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n--- RESULTADOS PARALELOS ---")
    print(f"Total de permutaciones evaluadas: {total_permutations}")
    print(f"Tiempo total: {elapsed_time:.2f} segundos")
    print(f"Mejor distancia: {best_distance:.4f}")
    print(f"Mejor ruta: {' -> '.join([city['name'] for city in best_route])}")
    print(f"Velocidad: {total_permutations/elapsed_time:.2f} rutas/segundo\n")
    
    return best_route, best_distance, elapsed_time

def main():
    print("=" * 60)
    print("PROBLEMA DEL VIAJANTE - CLIENTE DE FUERZA BRUTA")
    print("=" * 60)
    print(f"\nCiudades a visitar: {len(CITIES)}")
    print(f"Total de permutaciones posibles: {len(list(itertools.permutations(CITIES)))}")
    print(f"URL del servicio: {API_URL}\n")
    
    # Verificar que el servicio está disponible
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            print("✓ Servicio disponible\n")
        else:
            print("✗ Servicio no responde correctamente")
            return
    except Exception as e:
        print(f"✗ No se puede conectar al servicio: {e}")
        print("Asegúrate de que el swarm esté corriendo en localhost:5000")
        return
    
    # Ejecutar búsqueda secuencial
    route_seq, dist_seq, time_seq = brute_force_sequential()
    
    # Ejecutar búsqueda paralela
    route_par, dist_par, time_par = brute_force_parallel(max_workers=10)
    
    # Comparación de rendimiento
    print("=" * 60)
    print("COMPARACIÓN DE RENDIMIENTO")
    print("=" * 60)
    speedup = time_seq / time_par
    print(f"Speedup: {speedup:.2f}x")
    print(f"Mejora de eficiencia: {((time_seq - time_par) / time_seq * 100):.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
