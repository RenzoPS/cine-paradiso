from cine_paradiso_api.repositories import ejecutar_consulta, ejecutar_mutacion


def obtener_usuario_por_email(email):
    filas = ejecutar_consulta(
        'SELECT id_usuario, nombre, apellido, email, contrasena_hash, rol, fecha_creacion '
        'FROM usuarios WHERE email = :email',
        {'email': email}
    )
    return filas[0] if filas else None


def obtener_usuario_por_id(id_usuario):
    filas = ejecutar_consulta(
        'SELECT id_usuario, nombre, apellido, email, rol, fecha_creacion '
        'FROM usuarios WHERE id_usuario = :id_usuario',
        {'id_usuario': id_usuario}
    )
    return filas[0] if filas else None


def obtener_usuarios():
    return ejecutar_consulta(
        'SELECT id_usuario, nombre, apellido, email, rol, fecha_creacion '
        'FROM usuarios ORDER BY id_usuario',
        {}
    )


def insertar_usuario(nombre, apellido, email, contrasena_hash, rol, fecha_creacion):
    return ejecutar_mutacion(
        'INSERT INTO usuarios (nombre, apellido, email, contrasena_hash, rol, fecha_creacion) '
        'VALUES (:nombre, :apellido, :email, :contrasena_hash, :rol, :fecha_creacion)',
        {
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'contrasena_hash': contrasena_hash,
            'rol': rol,
            'fecha_creacion': fecha_creacion,
        }
    )
