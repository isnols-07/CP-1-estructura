# VISTA: aquí se pregunta y se muestra; todas las reglas están en views.py.
from shared.herramientas import imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
import views


def pausa():
    input('\nPresione Enter para continuar...')


def pedir_entero(mensaje):
    try:
        return int(input(mensaje))
    except ValueError:
        return None


def resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Sirve para clientes, productos y ventas: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return

    for objeto in objetos:
        print(f"  {objeto}")

    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


def menu_registros(tipo):
    if tipo == 'estudiantes':
        titulo = 'ESTUDIANTES'
        campos = ('nombre', 'apellido', 'email', 'carnet', 'carrera')
        crear = views.crear_estudiante
        listar = views.obtener_estudiantes
        buscar = views.buscar_estudiantes
        obtener = views.obtener_estudiante
        actualizar = views.actualizar_estudiante
        eliminar = views.eliminar_estudiante
    else:
        titulo = 'MATERIAS'
        campos = ('nombre', 'codigo', 'creditos', 'cupos')
        crear = views.crear_materia
        listar = views.obtener_materias
        buscar = views.buscar_materias
        obtener = views.obtener_materia
        actualizar = views.actualizar_materia
        eliminar = views.eliminar_materia

    while True:
        imprimir_titulo(titulo)
        print('1. Crear\n2. Ver todos\n3. Buscar\n4. Ver por id\n5. Actualizar\n6. Eliminar\n0. Volver')
        opcion = input('Opción: ').strip()
        if opcion == '0':
            return
        if opcion == '1':
            datos = {}
            for campo in campos:
                datos[campo] = input(f'{campo.capitalize()}: ')
            resultado(*crear(datos))
        elif opcion == '2':
            mostrar_lista(listar())
        elif opcion == '3':
            mostrar_lista(buscar(input('Texto a buscar: ')))
        elif opcion == '4':
            objeto = obtener(pedir_entero('Id: '))
            if objeto is None:
                imprimir_error('Registro no encontrado')
            else:
                mostrar_detalle(objeto)
        elif opcion == '5':
            id_registro = pedir_entero('Id: ')
            objeto = obtener(id_registro)
            if objeto is None:
                imprimir_error('Registro no encontrado')
            else:
                print('Deje en blanco los campos que no desea cambiar.')
                cambios = {}
                for campo in campos:
                    nuevo = input(f'{campo} [{getattr(objeto, campo)}]: ').strip()
                    if nuevo:
                        cambios[campo] = nuevo
                resultado(*actualizar(id_registro, cambios))
        elif opcion == '6':
            id_registro = pedir_entero('Id: ')
            objeto = obtener(id_registro)
            if objeto is None:
                imprimir_error('Registro no encontrado')
            elif confirmar(f'¿Eliminar {objeto.etiqueta()}?'):
                resultado(*eliminar(id_registro))
        else:
            imprimir_error('Opción incorrecta')
        pausa()


def menu_matriculas():
    while True:
        imprimir_titulo('MATRÍCULAS')
        print('1. Matricular\n2. Ver todas\n3. Registrar nota\n4. Ver certificado\n5. Retirar matrícula\n0. Volver')
        opcion = input('Opción: ').strip()
        if opcion == '0':
            return
        if opcion == '1':
            datos = {
                'estudiante_id': pedir_entero('Id del estudiante: '),
                'materia_id': pedir_entero('Id de la materia: '),
                'periodo': input('Periodo (ej. 2026-1): '),
                'nota': input('Nota inicial (0 a 20): '),
                'fecha': input('Fecha AAAA-MM-DD (vacío = hoy): ')
            }
            resultado(*views.crear_matricula(datos))
        elif opcion == '2':
            mostrar_lista(views.obtener_matriculas())
        elif opcion == '3':
            id_registro = pedir_entero('Id de matrícula: ')
            nota = input('Nueva nota: ')
            resultado(*views.registrar_nota(id_registro, nota))
        elif opcion == '4':
            certificado = views.certificado(pedir_entero('Id de matrícula: '))
            if certificado is None:
                imprimir_error('Certificado no disponible')
            else:
                print('\n' + certificado)
        elif opcion == '5':
            id_registro = pedir_entero('Id de matrícula: ')
            if confirmar('¿Retirar esta matrícula?'):
                resultado(*views.retirar_matricula(id_registro))
        else:
            imprimir_error('Opción incorrecta')
        pausa()


def mostrar_resumen():
    imprimir_titulo('RESUMEN ACADÉMICO')
    total, carreras, sin_cupo, aprobadas = views.resumen()
    print('Estudiantes:', total)
    print('Carreras distintas:', ', '.join(carreras) if carreras else 'Ninguna')
    print('Materias sin cupo:')
    mostrar_lista(sin_cupo)
    print('Matrículas aprobadas:', aprobadas)
    pausa()


def main():
    while True:
        imprimir_titulo('SISTEMA ACADÉMICO')
        print('1. Estudiantes\n2. Materias\n3. Matrículas\n4. Resumen\n0. Salir')
        opcion = input('Opción: ').strip()
        if opcion == '1':
            menu_registros('estudiantes')
        elif opcion == '2':
            menu_registros('materias')
        elif opcion == '3':
            menu_matriculas()
        elif opcion == '4':
            mostrar_resumen()
        elif opcion == '0':
            print('Hasta pronto')
            break
        else:
            imprimir_error('Opción incorrecta')


if __name__ == '__main__':
    main()
