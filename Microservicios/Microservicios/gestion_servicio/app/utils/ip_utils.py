import ipaddress
from app.models.ips_asignadas_pppoe_model import IPAsignadaPPPoE

def generar_ip_libre(rango_inicio, rango_fin, id_pool):
    try:
        inicio = ipaddress.IPv4Address(rango_inicio)
        fin = ipaddress.IPv4Address(rango_fin)

        usadas = set(row.ip for row in IPAsignadaPPPoE.query.filter_by(id_pool=id_pool, asignada=True).all())

        # Comenzar desde la siguiente IP después del inicio
        for ip in range(int(inicio) + 1, int(fin) + 1):
            ip_str = str(ipaddress.IPv4Address(ip))
            if ip_str not in usadas:
                return ip_str
        return None
    except Exception as e:
        print(f"Error generando IP libre: {e}")
        return None
