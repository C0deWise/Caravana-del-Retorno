"""
Este módulo contiene la lógica de negocio para la gestión de usuarios.
Se encarga de orquestar las operaciones, validaciones y transformaciones
de datos requeridas antes de interactuar con la capa de repositorio.
"""

from passlib.context import CryptContext
from sqlalchemy import select

from app.usuarios.models.parentesco import EstadoSolicitudParentesco
from app.usuarios.models.usuario import Usuario
from app.usuarios.repository.parentesco_repositorio import ParentescoRepositorio
from app.usuarios.repository.usuario_repositorio import UsuarioRepositorio
from app.usuarios.schemas.usuario_esquemas import UsuarioConsultaColonia, UsuarioCrear, UsuarioResumen
from app.usuarios.schemas.parentesco_esquemas import ParentescoCrear, ParentescoRespuesta, ParentescoRespuestaDetallada

# Contexto para el cifrado y verificación de contraseñas utilizando el algoritmo bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def mapear_usuario_a_resumen(usuario: Usuario) -> UsuarioResumen:
    """Función auxiliar para mapear un objeto Usuario a UsuarioResumen."""
    return UsuarioResumen(
        codigo=usuario.us_codigo,
        nombre=usuario.us_nombre,
        apellido=usuario.us_apellido
    )

def mapear_parentesco_a_respuesta_detallada(parentesco, solicitante: Usuario, destinatario: Usuario) -> ParentescoRespuestaDetallada:
    """Función auxiliar para mapear un objeto Parentesco a ParentescoRespuestaDetallada."""
    return ParentescoRespuestaDetallada(
        codigo=parentesco.codigo,
        tipo_parentesco=parentesco.tipo_parentesco,
        estado=parentesco.estado,
        solicitante= mapear_usuario_a_resumen(solicitante),
        destinatario= mapear_usuario_a_resumen(destinatario)
    )
class UsuarioServicio:
    """
    Servicio para gestionar la lógica de negocio de los usuarios.
    """

    def __init__(self, repositorio: UsuarioRepositorio, repositorio_parentesco: ParentescoRepositorio | None = None) -> None:
        """
        Inicializa el servicio con un repositorio de usuarios.

        Args:
            repositorio (UsuarioRepositorio): El repositorio para el acceso a datos.
            repositorio_parentesco (ParentescoRepositorio, opcional): El repositorio de parentesco.
        """
        self.repositorio = repositorio
        self.repositorio_parentesco = repositorio_parentesco

    async def registrar(self, schema: UsuarioCrear) -> Usuario:
        """
        Registra un nuevo usuario en el sistema.

        Este método realiza validaciones de negocio, como la verificación de campos únicos,
        cifra la contraseña y luego delega la creación del usuario al repositorio.

        Args:
            schema (UsuarioCrear): Los datos del usuario a registrar.

        Returns:
            Usuario: El objeto del usuario recién creado.

        Raises:
            ValueError: Si se detectan violaciones de campos únicos (documento, correo, celular).
        """
        errores = []

        # Se realizan verificaciones de unicidad para evitar errores de integridad en la BD.
        # Esto permite devolver un mensaje de error claro y específico al cliente.
        if await self.repositorio.existe_usuario("us_documento", schema.documento):
            errores.append("El documento ya se encuentra registrado.")
        if await self.repositorio.existe_usuario("us_correo", schema.correo):
            errores.append("El correo ya se encuentra registrado.")
        if await self.repositorio.existe_usuario("us_celular", schema.celular):
            errores.append("El celular ya se encuentra registrado.")

        # Verificar que el rol asignado exista para evitar errores de llave foránea
        from app.usuarios.models.usuario import Rol
        rol_query = await self.repositorio.db.execute(
            select(Rol).where(Rol.ro_codigo == schema.codigo_rol)
        )
        if not rol_query.scalar_one_or_none():
            errores.append(f"El rol con código {schema.codigo_rol} no existe en el sistema.")

        # Si se encontraron errores, se lanzan en una sola excepción.
        if errores:
            raise ValueError(". ".join(errores))

        # Cifrado de la contraseña antes de almacenarla en la base de datos.
        schema.contrasenia = pwd_context.hash(schema.contrasenia)

        return await self.repositorio.registrar(schema)

    async def obtener_todos(self) -> list[Usuario]:
        """
        Recupera todos los usuarios registrados en el sistema.

        Returns:
            list[Usuario]: Una lista de todos los usuarios.
        """
        return await self.repositorio.obtener_todos()

    async def buscar_por_nombre(self, nombre: str) -> list[Usuario]:
        """
        Busca usuarios por su nombre.

        Args:
            nombre (str): El término de búsqueda para el nombre.

        Returns:
            list[Usuario]: Una lista de usuarios que coinciden con el nombre.
        """
        return await self.repositorio.buscar_por_nombre(nombre)

    async def buscar_por_documento(self, documento: str) -> Usuario | None:
        """
        Busca un usuario específico por su número de documento.

        Args:
            documento (str): El número de documento a buscar.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        return await self.repositorio.buscar_por_documento(documento)

    async def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        """
        Obtiene un usuario por su ID.

        Args:
            usuario_id (int): El ID del usuario a buscar.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        usuario = await self.repositorio.obtener_usuario_por_id(usuario_id)
        if not usuario:
            raise ValueError(f"No se encontró un usuario con ID {usuario_id}.")
        return usuario
    
    async def existe_usuario(self, campo: str, valor: str) -> bool:
        """
        Verifica si un usuario ya existe basado en un campo y valor específicos.
        Delega la llamada directamente al repositorio.

        Args:
            campo (str): El nombre del campo a verificar (ej. 'us_documento').
            valor (str): El valor a buscar en ese campo.

        Returns:
            bool: True si el usuario existe, False de lo contrario.
        """
        return await self.repositorio.existe_usuario(campo, valor)
    
    async def existe_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una relación de parentesco entre dos usuarios."""
        if not self.repositorio_parentesco:
            raise RuntimeError("Repositorio de parentesco no inicializado.")
        return await self.repositorio_parentesco.existe_parentesco(codigo_solicitante, codigo_destinatario)

    async def aceptar_solicitud_parentesco(self, codigo_solicitud:int):
        """Acepta una solicitud de parentesco pendiente."""
        solicitud = await self.repositorio_parentesco.obtener_parentesco_por_id(codigo_solicitud)
        if not solicitud:
            raise ValueError("La solicitud de parentesco no existe.")
        if solicitud.estado != EstadoSolicitudParentesco.pendiente:
            raise ValueError("Solo se pueden aceptar solicitudes que estén en estado pendiente.")
        parentesco = await self.repositorio_parentesco.actualizar_estado_parentesco(codigo_solicitud, EstadoSolicitudParentesco.aceptada)
        return ParentescoRespuesta(
            codigo=parentesco.codigo,
            codigo_solicitante=parentesco.codigo_solicitante,
            codigo_destinatario=parentesco.codigo_destinatario,
            tipo_parentesco=parentesco.tipo_parentesco,
            estado=parentesco.estado
        )


    async def rechazar_solicitud_parentesco(self, codigo_solicitud:int):
        """Rechaza una solicitud de parentesco pendiente."""
        solicitud = await self.repositorio_parentesco.obtener_parentesco_por_id(codigo_solicitud)
        if not solicitud:
            raise ValueError("La solicitud de parentesco no existe.")
        if solicitud.estado != EstadoSolicitudParentesco.pendiente:
            raise ValueError("Solo se pueden rechazar solicitudes que estén en estado pendiente.")
        parentesco = await self.repositorio_parentesco.actualizar_estado_parentesco(codigo_solicitud, EstadoSolicitudParentesco.rechazada)
        return ParentescoRespuesta(
            codigo=parentesco.codigo,
            codigo_solicitante=parentesco.codigo_solicitante,
            codigo_destinatario=parentesco.codigo_destinatario,
            tipo_parentesco=parentesco.tipo_parentesco,
            estado=parentesco.estado
        )

    async def obtener_parentesco_por_id(self, id_parentesco: int):
        """Obtiene un parentesco por su ID."""
        return await self.repositorio_parentesco.obtener_parentesco_por_id_detallado(id_parentesco)
    
    async def existe_solicitud_parentesco(self, codigo_solicitante: int, codigo_destinatario: int) -> bool:
        """Verifica si ya existe una solicitud de parentesco entre dos usuarios."""
        if not self.repositorio_parentesco:
            raise RuntimeError("Repositorio de parentesco no inicializado.")
        return await self.repositorio_parentesco.existe_solicitud_parentesco(codigo_solicitante, codigo_destinatario)
    
    async def solicitar_parentesco(self, parentesco_crear: ParentescoCrear):
        """Solicita un parentesco entre dos usuarios."""
        if not self.repositorio_parentesco:
            raise RuntimeError("Repositorio de parentesco no inicializado.")
        if parentesco_crear.codigo_solicitante == parentesco_crear.codigo_destinatario:
            raise ValueError("El solicitante y el destinatario no pueden ser el mismo usuario.")
        # Verificar que ambos usuarios existan
        if not await self.existe_usuario("us_codigo", parentesco_crear.codigo_solicitante):
            raise ValueError("El usuario solicitante no existe.")
        if not await self.existe_usuario("us_codigo", parentesco_crear.codigo_destinatario):
            raise ValueError("El usuario destinatario no existe.")
        
        if await self.existe_parentesco(parentesco_crear.codigo_solicitante, parentesco_crear.codigo_destinatario):
            raise ValueError("Ya existe una relación de parentesco entre estos usuarios.")
        if await self.existe_solicitud_parentesco(parentesco_crear.codigo_solicitante, parentesco_crear.codigo_destinatario):
            raise ValueError("Ya existe una solicitud de parentesco pendiente entre estos usuarios.")

        solicitud_parentesco =  await self.repositorio_parentesco.solicitar_parentesco(parentesco_crear)
        return ParentescoRespuesta(
            codigo=solicitud_parentesco.codigo,
            codigo_solicitante=solicitud_parentesco.codigo_solicitante,
            codigo_destinatario=solicitud_parentesco.codigo_destinatario,
            tipo_parentesco=solicitud_parentesco.tipo_parentesco,
            estado=solicitud_parentesco.estado
        )
    async def obtener_usuario_por_id(self, us_id: int) -> Usuario | None:
        """
        Obtiene un usuario por su ID.

        Args:
            us_id (int): El ID del usuario a buscar.

        Returns:
            Usuario | None: El usuario encontrado o None si no existe.
        """
        return await self.repositorio.obtener_usuario_por_id(us_id)
    
    async def listar_parentescos_usuario(self, codigo_usuario: int):
        """Lista todas las relaciones de parentesco de un usuario."""

        parentescos = await self.repositorio_parentesco.listar_parentescos_usuario(codigo_usuario)
        return [mapear_parentesco_a_respuesta_detallada(p, p.solicitante, p.destinatario) for p in parentescos]
    
    async def obtener_parentesco_por_id(self, codigo_parentesco: int):
        """Obtiene un parentesco específico por su ID."""
        parentesco = await self.repositorio_parentesco.obtener_parentesco_por_id_detallado(codigo_parentesco)
        if not parentesco:
            raise ValueError("La solicitud de parentesco no existe.")
        return mapear_parentesco_a_respuesta_detallada(parentesco, parentesco.solicitante, parentesco.destinatario)
    
    async def buscar_por_colonia(self, colonia: int) -> list[Usuario]:
        """Busca usuarios miembros por colonia."""
        usuarios: list[Usuario] = await self.repositorio.buscar_por_colonia(colonia)
        usuarios_consulta: list[UsuarioConsultaColonia] = []
        for u in usuarios:
            usuario_consulta = UsuarioConsultaColonia(
                id = u.us_codigo,
                nombre=u.us_nombre,
                apellido=u.us_apellido,
                codigo_colonia=u.co_codigo,
                documento = u.us_documento,
                genero = u.us_genero,
                fecha_nacimiento = u.us_fecha_nacimiento,
                correo=u.us_correo,
                tipo_doc = u.us_tipo_doc,
                celular=u.us_celular,
                role = u.ro_codigo
            )
            usuarios_consulta.append(usuario_consulta)
        return usuarios_consulta

