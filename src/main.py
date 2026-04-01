# main.py - inventario-validator
import mysql.connector
import configparser
import csv
from datetime import datetime

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['mysql']

def connect(cfg):
    return mysql.connector.connect(
        host=cfg.get('host'),
        user=cfg.get('user'),
        password=cfg.get('password'),
        database=cfg.get('database')
    )

def fetch_products(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT sku, nombre, cantidad_registrada FROM productos')
    return cur.fetchall()

def fetch_inventario_fisico(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT sku, cantidad_fisica FROM inventario_fisico')
    return cur.fetchall()

def generate_report(mismatches):
    filename = f"reporte_mismatches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sku','nombre','cantidad_registrada','cantidad_fisica','diferencia'])
        for m in mismatches:
            writer.writerow([m['sku'], m.get('nombre',''), m['cantidad_registrada'], m['cantidad_fisica'], m['diferencia']])
    print('Reporte generado:', filename)

def main():
    cfg = load_config()
    conn = connect(cfg)
    products = fetch_products(conn)
    inv = fetch_inventario_fisico(conn)
    inv_map = {i['sku']: i['cantidad_fisica'] for i in inv}
    mismatches = []
    for p in products:
        sku = p['sku']
        q_reg = p['cantidad_registrada']
        q_fis = inv_map.get(sku, 0)
        if q_reg != q_fis:
            mismatches.append({'sku': sku, 'nombre': p['nombre'], 'cantidad_registrada': q_reg, 'cantidad_fisica': q_fis, 'diferencia': q_fis - q_reg})
    if mismatches:
        generate_report(mismatches)
    else:
        print('No se encontraron inconsistencias.')
    conn.close()

if __name__=='__main__':
    main()
