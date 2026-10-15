# CONTROLADOR: reglas de negocio y operaciones; no contiene input ni print.
from datetime import date
from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

GESTOR_ESTUDIANTES = GestorJSON('data/estudiantes.json')
GESTOR_MATERIAS = GestorJSON('data/materias.json')
GESTOR_MATRICULAS = GestorJSON('data/matriculas.json')

# TUPLAS: los campos de búsqueda no cambian durante la ejecución.
CAMPOS_ESTUDIANTE = ('nombre', 'apellido', 'email', 'carnet', 'carrera')
CAMPOS_MATERIA = ('nombre', 'codigo')


# Funciones generales iguales para los tres tipos de registro.
def leer_objetos(gestor, clase):
    objetos = []
    for datos in gestor.leer():
        objetos.append(clase.desde_diccionario(datos))
    return objetos


def obtener_por_id(gestor, clase, id_registro):
    for objeto in leer_objetos(gestor, clase):
        if objeto.id == id_registro:
            return objeto
    return None


def buscar(gestor, clase, texto, campos):
    resultado = []
    texto = texto.strip().lower()
    if texto == '':
        return resultado
    for objeto in leer_objetos(gestor, clase):
        for campo in campos:
            if texto in str(getattr(objeto, campo)).lower():
                resultado.append(objeto)
                break
    return resultado


def siguiente_id(gestor):
    mayor = 0
    for registro in gestor.leer():
        if registro['id'] > mayor:
            mayor = registro['id']
    return mayor + 1


def guardar_nuevo(gestor, objeto):
    datos = gestor.leer()
    datos.append(objeto.a_diccionario())
    return gestor.guardar(datos)


def reemplazar(gestor, objeto):
    datos = gestor.leer()
    for posicion, registro in enumerate(datos):
        if registro['id'] == objeto.id:
            datos[posicion] = objeto.a_diccionario()
            return gestor.guardar(datos)
    return False


def eliminar(gestor, id_registro):
    datos = gestor.leer()
    nuevos = []
    for registro in datos:
        if registro['id'] != id_registro:
            nuevos.append(registro)
    if len(nuevos) == len(datos):
        return False
    return gestor.guardar(nuevos)


def ids_registrados(gestor):
    # CONJUNTO: permite comprobar rápidamente si un id está registrado.
    ids = set()
    for registro in gestor.leer():
        ids.add(registro['id'])
    return ids


def indice_por_id(gestor, clase):
    # DICCIONARIO ÍNDICE: relaciona cada id con su objeto para consultar certificados.
    indice = {}
    for objeto in leer_objetos(gestor, clase):
        indice[objeto.id] = objeto
    return indice


# ESTUDIANTES
def carnets_registrados(excepto_id=None):
    # CONJUNTO: no admite carnets repetidos.
    carnets = set()
    for r in GESTOR_ESTUDIANTES.leer():
        if r['id'] != excepto_id:
            carnets.add(r['carnet'].strip().upper())
    return carnets


def emails_registrados(excepto_id=None):
    emails = set()
    for r in GESTOR_ESTUDIANTES.leer():
        if r['id'] != excepto_id:
            emails.add(r['email'].strip().lower())
    return emails


def validar_estudiante(datos, id_actual=None):
    for campo in ('nombre', 'apellido', 'email', 'carnet'):
        if id_actual is None or campo in datos:
            if not str(datos.get(campo, '')).strip():
                return f'{campo.capitalize()} es obligatorio'
    if 'email' in datos:
        email = str(datos['email']).strip().lower()
        if not es_email_valido(email):
            return 'Email inválido'
        if email in emails_registrados(id_actual):
            return 'El email ya está registrado'
    if 'carnet' in datos and str(datos['carnet']).strip().upper() in carnets_registrados(id_actual):
        return 'El carnet ya está registrado'
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error
    e = Estudiante(siguiente_id(GESTOR_ESTUDIANTES), str(datos['nombre']).strip().title(),
                   str(datos['apellido']).strip().title(), str(datos['email']).strip().lower(),
                   str(datos['carnet']).strip().upper(), str(datos.get('carrera', '')).strip().title())
    if not guardar_nuevo(GESTOR_ESTUDIANTES, e):
        return False, 'No fue posible guardar el estudiante'
    return True, 'Estudiante creado'


def obtener_estudiantes():
    return leer_objetos(GESTOR_ESTUDIANTES, Estudiante)


def obtener_estudiante(id_registro):
    return obtener_por_id(GESTOR_ESTUDIANTES, Estudiante, id_registro)


def buscar_estudiantes(termino):
    return buscar(GESTOR_ESTUDIANTES, Estudiante, termino, CAMPOS_ESTUDIANTE)


def actualizar_estudiante(id_registro, cambios):
    e = obtener_estudiante(id_registro)
    if e is None:
        return False, 'Estudiante no encontrado'
    if not cambios:
        return False, 'No se indicó ningún cambio'
    for campo in cambios:
        if campo not in CAMPOS_ESTUDIANTE:
            return False, 'Campo no permitido'
    error = validar_estudiante(cambios, id_registro)
    if error:
        return False, error
    for campo, valor in cambios.items():
        valor = str(valor).strip()
        if campo in ('nombre', 'apellido', 'carrera'):
            valor = valor.title()
        if campo == 'email':
            valor = valor.lower()
        if campo == 'carnet':
            valor = valor.upper()
        setattr(e, campo, valor)
    if not reemplazar(GESTOR_ESTUDIANTES, e):
        return False, 'No se pudo guardar'
    return True, 'Estudiante actualizado'


def eliminar_estudiante(id_registro):
    if obtener_estudiante(id_registro) is None:
        return False, 'Estudiante no encontrado'
    for m in obtener_matriculas():
        if m.estudiante_id == id_registro:
            return False, 'No se puede eliminar: tiene matrículas registradas'
    if not eliminar(GESTOR_ESTUDIANTES, id_registro):
        return False, 'No se pudo eliminar'
    return True, 'Estudiante eliminado'


# MATERIAS
def codigos_registrados(excepto_id=None):
    # CONJUNTO: garantiza que cada código de materia sea único.
    codigos = set()
    for r in GESTOR_MATERIAS.leer():
        if r['id'] != excepto_id:
            codigos.add(r['codigo'].strip().upper())
    return codigos


def validar_materia(datos, id_actual=None):
    for campo in ('nombre', 'codigo', 'creditos', 'cupos'):
        if id_actual is None or campo in datos:
            if not str(datos.get(campo, '')).strip():
                # Se acepta 0 en cupos porque se convierte previamente a texto '0'.
                return f'{campo.capitalize()} es obligatorio'
    if 'codigo' in datos and str(datos['codigo']).strip().upper() in codigos_registrados(id_actual):
        return 'El código ya existe'
    if 'creditos' in datos:
        try:
            creditos = int(datos['creditos'])
            if str(creditos) != str(datos['creditos']).strip() or not 1 <= creditos <= 10:
                return 'Los créditos deben ser enteros entre 1 y 10'
        except (TypeError, ValueError):
            return 'Los créditos deben ser enteros entre 1 y 10'
    if 'cupos' in datos:
        try:
            cupos = int(datos['cupos'])
            if str(cupos) != str(datos['cupos']).strip() or not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
                return 'Los cupos deben ser enteros entre 0 y 30'
        except (TypeError, ValueError):
            return 'Los cupos deben ser enteros entre 0 y 30'
    return None


def crear_materia(datos):
    error = validar_materia(datos)
    if error:
        return False, error
    materia = Materia(siguiente_id(GESTOR_MATERIAS), str(datos['nombre']).strip().title(),
                     str(datos['codigo']).strip().upper(), datos['creditos'], datos['cupos'])
    if not guardar_nuevo(GESTOR_MATERIAS, materia):
        return False, 'No se pudo guardar'
    return True, 'Materia creada'


def obtener_materias():
    return leer_objetos(GESTOR_MATERIAS, Materia)


def obtener_materia(id_registro):
    return obtener_por_id(GESTOR_MATERIAS, Materia, id_registro)


def buscar_materias(termino):
    return buscar(GESTOR_MATERIAS, Materia, termino, CAMPOS_MATERIA)


def actualizar_materia(id_registro, cambios):
    materia = obtener_materia(id_registro)
    if materia is None:
        return False, 'Materia no encontrada'
    if not cambios:
        return False, 'No se indicó ningún cambio'
    for campo in cambios:
        if campo not in ('nombre', 'codigo', 'creditos', 'cupos'):
            return False, 'Campo no permitido'
    error = validar_materia(cambios, id_registro)
    if error:
        return False, error
    # No se permite reducir cupos disponibles por debajo de cero.
    for campo, valor in cambios.items():
        if campo in ('creditos', 'cupos'):
            valor = int(valor)
        elif campo == 'codigo':
            valor = str(valor).strip().upper()
        else:
            valor = str(valor).strip().title()
        setattr(materia, campo, valor)
    if not reemplazar(GESTOR_MATERIAS, materia):
        return False, 'No se pudo guardar'
    return True, 'Materia actualizada'


def eliminar_materia(id_registro):
    if obtener_materia(id_registro) is None:
        return False, 'Materia no encontrada'
    for m in obtener_matriculas():
        if m.materia_id == id_registro:
            return False, 'No se puede eliminar: tiene matrículas registradas'
    if not eliminar(GESTOR_MATERIAS, id_registro):
        return False, 'No se pudo eliminar'
    return True, 'Materia eliminada'


def materias_sin_cupo():
    resultado = []
    for m in obtener_materias():
        if not m.hay_cupo():
            resultado.append(m)
    return resultado


# MATRÍCULAS
def crear_matricula(datos):
    try:
        estudiante_id = int(datos.get('estudiante_id'))
        materia_id = int(datos.get('materia_id'))
    except (TypeError, ValueError):
        return False, 'Los id deben ser números enteros'
    if estudiante_id not in ids_registrados(GESTOR_ESTUDIANTES):
        return False, 'El estudiante no existe'
    if materia_id not in ids_registrados(GESTOR_MATERIAS):
        return False, 'La materia no existe'
    materia = obtener_materia(materia_id)
    if not materia.hay_cupo():
        return False, 'La materia no tiene cupos'
    periodo = str(datos.get('periodo', '')).strip()
    if not periodo:
        return False, 'El periodo es obligatorio'
    nota = datos.get('nota', 0)
    if not Materia.es_nota_valida(nota):
        return False, 'La nota debe estar entre 0 y 20'
    for m in obtener_matriculas():
        if m.estudiante_id == estudiante_id and m.materia_id == materia_id and m.periodo == periodo:
            return False, 'El estudiante ya está matriculado en esa materia y periodo'
    fecha = str(datos.get('fecha', '')).strip()
    if not fecha:
        fecha = str(date.today())
    matricula = Matricula(siguiente_id(GESTOR_MATRICULAS), estudiante_id, materia_id,
                          periodo, nota, fecha)
    if not guardar_nuevo(GESTOR_MATRICULAS, matricula):
        return False, 'No se pudo guardar la matrícula'
    materia.ocupar_cupo()
    if not reemplazar(GESTOR_MATERIAS, materia):
        eliminar(GESTOR_MATRICULAS, matricula.id)
        return False, 'No se pudo actualizar el cupo'
    return True, 'Matrícula registrada y cupo descontado'


def obtener_matriculas():
    return leer_objetos(GESTOR_MATRICULAS, Matricula)


def obtener_matricula(id_registro):
    return obtener_por_id(GESTOR_MATRICULAS, Matricula, id_registro)


def registrar_nota(id_registro, nota):
    matricula = obtener_matricula(id_registro)
    if matricula is None:
        return False, 'Matrícula no encontrada'
    if not Materia.es_nota_valida(nota):
        return False, 'La nota debe estar entre 0 y 20'
    matricula.nota = float(nota)
    if not reemplazar(GESTOR_MATRICULAS, matricula):
        return False, 'No se pudo guardar'
    return True, f'Nota registrada. Estado: {matricula.estado()}'


def retirar_matricula(id_registro):
    matricula = obtener_matricula(id_registro)
    if matricula is None:
        return False, 'Matrícula no encontrada'
    materia = obtener_materia(matricula.materia_id)
    if materia is None:
        return False, 'La materia asociada no existe'
    if not materia.liberar_cupo():
        return False, 'No se puede devolver el cupo: límite alcanzado'
    if not eliminar(GESTOR_MATRICULAS, id_registro):
        return False, 'No se pudo retirar la matrícula'
    if not reemplazar(GESTOR_MATERIAS, materia):
        guardar_nuevo(GESTOR_MATRICULAS, matricula)
        return False, 'No se pudo devolver el cupo'
    return True, 'Matrícula retirada y cupo devuelto'


def certificado(id_registro):
    matricula = obtener_matricula(id_registro)
    if matricula is None:
        return None
    # DICCIONARIOS ÍNDICE: evitamos buscar varias veces por toda la lista.
    estudiantes = indice_por_id(GESTOR_ESTUDIANTES, Estudiante)
    materias = indice_por_id(GESTOR_MATERIAS, Materia)
    estudiante = estudiantes.get(matricula.estudiante_id)
    materia = materias.get(matricula.materia_id)
    if estudiante is None or materia is None:
        return None
    return (f'CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n'
            f'Estudiante: {estudiante.nombre_completo()}   ({estudiante.carnet})\n'
            f'Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n'
            f'------------------------------------------\n'
            f'Nota      : {matricula.nota}\n'
            f'Estado    : {matricula.estado()}')


def matriculas_por_estudiante():
    # DICCIONARIO DE LISTAS: un estudiante puede tener varias matrículas.
    grupos = {}
    for matricula in obtener_matriculas():
        grupos.setdefault(matricula.estudiante_id, []).append(matricula)
    return grupos


def promedio_de_estudiante(id_registro):
    if obtener_estudiante(id_registro) is None:
        return None
    grupos = matriculas_por_estudiante()
    matriculas = grupos.get(id_registro, [])
    if not matriculas:
        return None
    suma = 0
    for matricula in matriculas:
        suma += matricula.nota
    return round(suma / len(matriculas), 2)


def resumen():
    # CONJUNTO: carreras distintas sin valores repetidos.
    carreras = set()
    for estudiante in obtener_estudiantes():
        if estudiante.carrera:
            carreras.add(estudiante.carrera)
    aprobadas = 0
    for matricula in obtener_matriculas():
        if matricula.esta_aprobada():
            aprobadas += 1
    return len(obtener_estudiantes()), sorted(carreras), materias_sin_cupo(), aprobadas
