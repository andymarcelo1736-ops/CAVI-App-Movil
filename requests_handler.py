import requests
import json

URL_BASE = "http://10.0.0.36:5000" 

class RequestsHandler:
    
    @staticmethod
    def get_productos():
        """Obtiene la lista de productos finales para el POS."""
        try:
            response = requests.get(f"{URL_BASE}/productos")
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener productos: {e}")
            return []

    @staticmethod
    def post_venta(items_vendidos):
        """Envía el pedido al servidor Flask para registrar la venta y descontar stock."""
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{URL_BASE}/vender", json={'items': items_vendidos}, headers=headers)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f"Error de conexión al servidor: {e}"}
