from app.infrastructure.database import execute_query

#Funcion que debuelve un inmueble por su codigo de tarjeta o como un diccionario o NONE si no existe
def get_inmueble_by_codigo(codigo):
    query = "SELECT * FROM inmuebles WHERE codigo_tarjeta = %s"
    inmuebles = execute_query(query, (codigo,), fetch=True)

    if inmuebles:
        return inmuebles[0]

    return None
#Buscar un inmueble por su codigo de tarjeta
def get_inmueble_id_by_codigo(codigo):
    query = "SELECT id FROM inmuebles WHERE codigo_tarjeta = %s"
    inmuebles = execute_query(query, (codigo,), fetch=True)

    if inmuebles:
        return inmuebles[0]["id"]

    return None
