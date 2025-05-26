# app/service/DatabaseManagerSA.py

import json
from sqlalchemy.exc import IntegrityError
from app.model.Usuario import Session, Usuario, Partida

class AdministradorBaseDatosSA:
    def __init__(self):
        self.sesion = Session()

    def verificar_usuario(self, nombre: str, clave: str) -> int | None:
        usuario = (
            self.sesion
                .query(Usuario)
                .filter_by(nombre=nombre, clave=clave)
                .first()
        )
        return usuario.id if usuario else None

    def crear_usuario(self, username: str, password: str) -> int:
        nuevo = Usuario(username=username, password=password)
        self.sesion.add(nuevo)
        try:
            self.sesion.commit()
        except IntegrityError:
            self.sesion.rollback()
            raise
        return nuevo.id

    def listar_partidas_guardadas(self, usuario_id: int) -> list[tuple[int,str,str]]:
        partidas = (
            self.sesion
                .query(Partida)
                .filter_by(usuario_id=usuario_id)
                .all()
        )
        return [
            (p.id, p.nombre_personaje, p.fecha_guardado.strftime("%Y-%m-%d %H:%M:%S"))
            for p in partidas
        ]

    def cargar_partida(self, partida_id: int) -> dict:
        partida = self.sesion.get(Partida, partida_id)
        if not partida:
            return {}

        datos_personaje = json.loads(partida.datos_personaje)
        return {
            "personaje": datos_personaje,
            "historia": partida.historia
        }

    def guardar_partida(self, usuario_id: int, nombre_personaje: str, datos_personaje: dict, historia: str = None):
        # Buscamos si ya hay una partida guardada con ese nombre
        partida = (
            self.sesion
                .query(Partida)
                .filter_by(usuario_id=usuario_id, nombre_personaje=nombre_personaje)
                .first()
        )
        datos_json = json.dumps(datos_personaje)
        if partida:
            partida.datos_personaje = datos_json
            partida.historia = json.dumps(historia) if historia else partida.historia
            from datetime import datetime
            partida.guardado_en = datetime.utcnow()
        else:
            # Creamos nueva partida
            partida = Partida(
                usuario_id=usuario_id,
                nombre_personaje=nombre_personaje,
                datos_personaje=datos_json
            )
            self.sesion.add(partida)

        self.sesion.commit()
