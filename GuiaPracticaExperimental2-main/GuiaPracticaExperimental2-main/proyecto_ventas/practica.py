"""PRÁCTICA DE LA GUÍA 2: ejercicios 1 al 10.
Ejecutar desde proyecto_ventas con: python practica.py
Los ejercicios 6, 8 y 10 también están integrados en el proyecto.
"""
from models import Cliente, Producto, Venta, Proveedor


def ejercicio_1():
    ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
    vistas = set()
    unicas = []
    for ciudad in ciudades:
        if ciudad not in vistas:
            vistas.add(ciudad)
            unicas.append(ciudad)
    print("Sin repetidos y en orden:", unicas)


def ejercicio_2():
    ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
    conteo = {}
    for ciudad in ciudades:
        if ciudad not in conteo:
            conteo[ciudad] = 0
        conteo[ciudad] += 1
    print("Cantidad por ciudad:", conteo)
    mayor = 0
    for ciudad, cantidad in conteo.items():
        if cantidad > mayor:
            mayor = cantidad
    print("Ciudades más repetidas:")
    for ciudad, cantidad in conteo.items():
        if cantidad == mayor:
            print(ciudad, cantidad)


def ejercicio_3():
    inscritos_matematica = {"Ana", "Luis", "Sol", "Marco"}
    inscritos_ingles = {"Luis", "Marco", "Ruth"}
    print("En las dos:", sorted(inscritos_matematica & inscritos_ingles))
    print("Solo Matemática:", sorted(inscritos_matematica - inscritos_ingles))
    print("Total de estudiantes distintos:", len(inscritos_matematica | inscritos_ingles))


def ejercicio_4():
    clientes = [{"id": 1, "nombre": "Ana"}, {"id": 2, "nombre": "Luis"}]
    indice = {}
    for cliente in clientes:
        indice[cliente["id"]] = cliente
    print("Índice por ID:", indice)
    print("Nombre del cliente 2:", indice[2]["nombre"])


def ejercicio_5():
    ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)]
    total = 0
    mejor_mes = ""
    mejor_monto = 0
    for mes, monto in ventas:  # desempaquetado de tuplas
        total += monto
        if monto > mejor_monto:
            mejor_monto = monto
            mejor_mes = mes
        print(mes, monto)
    print("Total:", total)
    print("Mayor venta:", mejor_mes, mejor_monto)


def ejercicio_6():
    from views import ClienteController
    # Archivo de ejemplo separado para no modificar los datos reales del sistema.
    controlador = ClienteController(archivo="data/practica_clientes.json")
    # Los objetos de prueba se mantienen en memoria y no se guardan.
    controlador.lista = [
        Cliente(1, "Ana", "Pérez", "ana@x.com", "", "Guayaquil"),
        Cliente(2, "Luis", "Mora", "luis@x.com", "", "Guayaquil"),
        Cliente(3, "Sol", "López", "sol@x.com", "", "Quito"),
    ]
    print("Clientes por ciudad:", controlador.clientes_por_ciudad())
    print("En main.py también está disponible como opción 8 del menú Clientes.")


def ejercicio_7():
    print("a) Total de venta: instancia; usa cantidad y precio de la venta.")
    print("b) Crear Producto desde diccionario: clase; usa cls para construir.")
    print("c) Validar precio: estático; no necesita un producto concreto.")
    print("d) Stock bajo: instancia; consulta el stock de ese producto.")
    print("e) Calcular IVA: estático; recibe cualquier monto.")


def ejercicio_8():
    datos = {"id": 1, "nombre": "Luis", "apellido": "Mora", "email": "luis@x.com",
             "ruc": "0912345678001", "empresa": "Importadora Sur"}
    proveedor = Proveedor.desde_diccionario(datos)
    print("Proveedor creado con herencia:", proveedor)
    print("Como diccionario:", proveedor.a_diccionario())


def describir(objeto):
    # Ejercicio 9: polimorfismo sin preguntar el tipo con if.
    return objeto.etiqueta()


def ejercicio_9():
    objetos = [Cliente(1, "Ana", "Pérez", "ana@x.com", "", "Quito"),
               Producto(1, "Cuaderno", 2, 20),
               Venta(1, 1, 1, 3, 2, "2026-10-12"),
               Proveedor(1, "Luis", "Mora", "luis@x.com", "123", "Sur")]
    for objeto in objetos:
        print(describir(objeto))


def ejercicio_10():
    print("Precio normal por unidad:", Producto.precio_mayorista(10, 5))
    print("Precio mayorista por unidad:", Producto.precio_mayorista(10, 12))
    print("Total de 12 unidades:", 12 * Producto.precio_mayorista(10, 12))
    print("En views.py el descuento se aplica al crear ventas de 12 o más unidades.")


def main():
    ejercicios = (ejercicio_1, ejercicio_2, ejercicio_3, ejercicio_4,
                  ejercicio_5, ejercicio_6, ejercicio_7, ejercicio_8,
                  ejercicio_9, ejercicio_10)
    while True:
        print("\n========== PRÁCTICA GUÍA 2 ==========")
        print("1 al 10: ejecutar el ejercicio indicado")
        print("11: ejecutar todos")
        print("0: salir")
        opcion = input("Elige una opción: ").strip()
        if opcion == "0":
            break
        elif opcion == "11":
            for numero in range(10):
                print("\n--- EJERCICIO", numero + 1, "---")
                ejercicios[numero]()
        elif opcion in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"):
            numero = int(opcion)
            print("\n--- EJERCICIO", numero, "---")
            ejercicios[numero - 1]()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
