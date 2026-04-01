import mysql.connector
import configparser
import csv
import os
from datetime import datetime

def load_config():
    config = configparser.ConfigParser()
    # Localización dinámica del archivo de configuración
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Archivo de configuracion no encontrado en: {config_path}")
    config.read(config_path)
    return config['mysql']

def connect(cfg):
    try:
        conn = mysql.connector.connect(
            host=cfg.get('host'),
            user=cfg.get('user'),
            password=cfg.get('password'),
            database=cfg.get('database')
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexion a MySQL: {err}")
        exit(1)

def fetch_data(conn, query):
    """Ejecuta consultas y retorna resultados en formato de diccionario."""
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    return result

def generate_report(mismatches):
    # Creación automática de carpeta para reportes
    os.makedirs('reports', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reports/reporte_mismatches_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SKU', 'NOMBRE', 'CANTIDAD_REGISTRADA', 'CANTIDAD_FISICA', 'DIFERENCIA'])
            for m in mismatches:
                writer.writerow([
                    m['sku'], 
                    m.get('nombre', 'N/A'), 
                    m['cantidad_registrada'], 
                    m['cantidad_fisica'], 
                    m['diferencia']
                ])
        print(f"Reporte generado en: {filename}")
    except IOError as e:
        print(f"Error al escribir archivo CSV: {e}")

def main():
    conn = None
    try:
        cfg = load_config()
        conn = connect(cfg)
        
        # Obtención de datos mediante consultas SQL
        products = fetch_data(conn, 'SELECT sku, nombre, cantidad_registrada FROM productos')
        inv_fisico = fetch_data(conn, 'SELECT sku, cantidad_fisica FROM inventario_fisico')
        
        # Mapeo de inventario físico para búsqueda eficiente O(1)
        inv_map = {i['sku']: i['cantidad_fisica'] for i in inv_fisico}
        mismatches = []

        for p in products:
            sku = p['sku']
            q_reg = p['cantidad_registrada']
            q_fis = inv_map.get(sku, 0)
            
            if q_reg != q_fis:
                mismatches.append({
                    'sku': sku, 
                    'nombre': p['nombre'], 
                    'cantidad_registrada': q_reg, 
                    'cantidad_fisica': q_fis, 
                    'diferencia': q_fis - q_reg
                })

        if mismatches:
            print(f"Se detectaron {len(mismatches)} inconsistencias.")
            generate_report(mismatches)
        else:
            print("Inventario validado: No se encontraron diferencias.")

    except Exception as e:
        print(f"Error en la ejecucion: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Conexion a base de datos cerrada.")

if __name__ == '__main__':
    main()
