from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum
from sqlalchemy import Enum

db = SQLAlchemy()

class Usuarios(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(13), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)

    
    administradores = db.relationship('Administradores', back_populates='usuario', lazy=True)
    solicitudes = db.relationship('SolicitudesServicios', back_populates='usuario', lazy=True)
    pagos = db.relationship('Pagos', back_populates='usuario', lazy=True)
    mensajes = db.relationship('Mensajes', back_populates='usuario', lazy=True)
    direcciones = db.relationship('Direcciones', back_populates='usuario', lazy=True)
    notificaciones = db.relationship('Notificaciones', back_populates='usuario', lazy=True)
    resenas = db.relationship('Resenas', back_populates='usuario', lazy=True)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "correo": self.correo,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "contrasena": self.contrasena
        }


class Trabajadores(db.Model):
    __tablename__ = 'trabajadores'

    id_trabajador = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion_trabajo = db.Column(db.String(255), nullable=False)
    correo_trabajador = db.Column(db.String(255), nullable=False)
    telefono_trabajador = db.Column(db.String(13), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    foto_trabajador = db.Column(db.String(255), nullable=False)

    servicios = db.relationship('Servicios', back_populates='trabajador', lazy=True)
    disponibilidades = db.relationship('Disponibilidad', back_populates='trabajador', lazy=True)
    resenas = db.relationship('Resenas', back_populates='trabajador', lazy=True)
    mensajes = db.relationship('Mensajes', back_populates='trabajador', lazy=True)
    notificaciones = db.relationship('Notificaciones', back_populates='trabajador', lazy=True)

    def to_dict(self):
        return {
            "id_trabajador": self.id_trabajador,
            "nombre": self.nombre,
            "descripcion_trabajo": self.descripcion_trabajo,
            "correo_trabajador": self.correo_trabajador,
            "telefono_trabajador": self.telefono_trabajador,
            "contrasena": self.contrasena,
            "foto_trabajador": self.foto_trabajador
        }


class Administradores(db.Model):
    __tablename__ = 'administradores'

    id_administrador = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo_admin = db.Column(db.String(255), nullable=False)
    nivel_acceso = db.Column(db.Integer, nullable=False)

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)

    usuario = db.relationship('Usuarios', back_populates='administradores')

    def to_dict(self):
        return {
            "id_administrador": self.id_administrador,
            "correo_admin": self.correo_admin,
            "nivel_acceso": self.nivel_acceso
        }

class Servicios(db.Model):
    __tablename__ = 'servicios'

    id_servicio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_servicio = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    tarifa = db.Column(db.Integer, nullable=False)
    tipo_tarifa = db.Column(db.String(100), nullable=True)

    id_trabajador = db.Column(db.Integer, db.ForeignKey("trabajadores.id_trabajador"), nullable=False)

    trabajador = db.relationship('Trabajadores', back_populates='servicios')
    solicitudes = db.relationship('SolicitudesServicios', back_populates='servicio', lazy=True)

    def to_dict(self):
        return {
            "id_servicio": self.id_servicio,
            "tipo_servicio": self.tipo_servicio,
            "descripcion": self.descripcion,
            "tarifa": self.tarifa,
            "tipo_tarifa": self.tipo_tarifa
        }

class Estado(PyEnum):
    DISPONIBLE = 'disponible'
    OCUPADO = 'ocupado'
    INACTIVO = 'inactivo'

class Disponibilidad(db.Model):
    __tablename__ = 'disponibilidad_trabajadores'

    id_disponibilidad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    estado = db.Column(Enum(Estado), default=Estado.DISPONIBLE)

    id_trabajador = db.Column(db.Integer, db.ForeignKey("trabajadores.id_trabajador"), nullable=False)

    trabajador = db.relationship('Trabajadores', back_populates='disponibilidades')

    def to_dict(self):
        return {
            "id_disponibilidad": self.id_disponibilidad,
            "fecha": self.fecha,
            "hora_inicio": self.hora_inicio,
            "hora_fin": self.hora_fin,
            "estado": self.estado.value
        }

class SolicitudesServicios(db.Model):
    __tablename__ = 'solicitudes_servicios'

    id_solicitud = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_solicitud = db.Column(db.DateTime, nullable=False)
    direccion_servicio = db.Column(db.String(255), nullable=False)
    descripcion_servicio = db.Column(db.String(255), nullable=False)

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    id_servicio = db.Column(db.Integer, db.ForeignKey("servicios.id_servicio"), nullable=False)

    usuario = db.relationship('Usuarios', back_populates='solicitudes')
    servicio = db.relationship('Servicios', back_populates='solicitudes')
    pagos = db.relationship('Pagos', back_populates='solicitud', lazy=True)
    resenas = db.relationship('Resenas', back_populates='solicitud', lazy=True)
    mensajes = db.relationship('Mensajes', back_populates='solicitud', lazy=True)

    def to_dict(self):
        return {
            "id_solicitud": self.id_solicitud,
            "fecha_solicitud": self.fecha_solicitud,
            "direccion_servicio": self.direccion_servicio,
            "descripcion_servicio": self.descripcion_servicio
        }

class Pagos(db.Model):
    __tablename__ = "pagos"

    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total = db.Column(db.Integer, nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False)

    id_solicitud = db.Column(db.Integer, db.ForeignKey("solicitudes_servicios.id_solicitud"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)

    solicitud = db.relationship('SolicitudesServicios', back_populates='pagos')
    usuario = db.relationship('Usuarios', back_populates='pagos')

    def to_dict(self):
        return {
            "id_pago": self.id_pago,
            "total": self.total,
            "fecha_pago": self.fecha_pago
        }

class Resenas(db.Model):
    __tablename__ = "resenas"

    id_resena = db.Column(db.Integer, primary_key=True, autoincrement=True)
    calificacion = db.Column(db.Integer, nullable=False)
    comentarios = db.Column(db.String(500), nullable=False)
    fecha_resena = db.Column(db.DateTime, nullable=False)

    id_solicitud = db.Column(db.Integer, db.ForeignKey("solicitudes_servicios.id_solicitud"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    id_trabajador = db.Column(db.Integer, db.ForeignKey("trabajadores.id_trabajador"), nullable=False)

    solicitud = db.relationship('SolicitudesServicios', back_populates='resenas')
    usuario = db.relationship('Usuarios', back_populates='resenas')
    trabajador = db.relationship('Trabajadores', back_populates='resenas')

    def to_dict(self):
        return {
            "id_resena": self.id_resena,
            "calificacion": self.calificacion,
            "comentarios": self.comentarios,
            "fecha_resena": self.fecha_resena
        }

class Mensajes(db.Model):
    __tablename__ = 'mensajes'

    id_mensaje = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contenido = db.Column(db.String(500), nullable=True)
    fecha_envio = db.Column(db.DateTime)

    id_solicitud = db.Column(db.Integer, db.ForeignKey("solicitudes_servicios.id_solicitud"), nullable=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True)
    id_trabajador = db.Column(db.Integer, db.ForeignKey("trabajadores.id_trabajador"), nullable=True)

    solicitud = db.relationship('SolicitudesServicios', back_populates='mensajes')
    usuario = db.relationship('Usuarios', back_populates='mensajes')
    trabajador = db.relationship('Trabajadores', back_populates='mensajes')

    def to_dict(self):
        return {
            "id_mensaje": self.id_mensaje,
            "contenido": self.contenido,
            "fecha_envio": self.fecha_envio
        }

class Direcciones(db.Model):
    __tablename__ = 'direcciones'

    id_direccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    direccion_completa = db.Column(db.String(255))

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)

    usuario = db.relationship('Usuarios', back_populates='direcciones')

    def to_dict(self):
        return {
            "id_direccion": self.id_direccion,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "direccion_completa": self.direccion_completa
        }

class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'

    id_notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_notificacion = db.Column(db.String(255))
    mensaje = db.Column(db.Text())
    fecha_creacion = db.Column(db.DateTime)
    leido = db.Column(db.Boolean, default=False)

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True)
    id_trabajador = db.Column(db.Integer, db.ForeignKey("trabajadores.id_trabajador"), nullable=True)

    usuario = db.relationship('Usuarios', back_populates='notificaciones')
    trabajador = db.relationship('Trabajadores', back_populates='notificaciones')

    def to_dict(self):
        return {
            "id_notificacion": self.id_notificacion,
            "tipo_notificacion": self.tipo_notificacion,
            "mensaje": self.mensaje,
            "fecha_creacion": self.fecha_creacion,
            "leido": self.leido
        }
