"""
mapper.py
=========
Propósito: Mapper para convertir datos de asistentes a modelos de reportes detallados.
          Transforma información de registros de grupos y asistentes (usuarios y personas)
          en objetos RegistroRetornoGrupoDetallado y RegistroRetornoUsuarioDetallado.
          Este mapper es puro: solo transforma datos sin lógica de acceso a base de datos.
"""

from typing import Union

from app.reportes.models.registro_retorno_grupo_detallado_modelo import RegistroRetornoGrupoDetallado
from app.reportes.models.registro_retorno_usuario_detallado_modelo import RegistroRetornoUsuarioDetallado
from app.retornos.modelos.registro_retorno_grupo_modelo import RegistroRetornoGrupo
from app.retornos.modelos.registro_retorno_modelo import RegistroRetorno
from app.usuarios.models.usuario import Usuario
from app.retornos.modelos.persona_modelo import Persona


class RegistroRetornoGrupoDetalladoMapper:
    """
    Mapper puro que convierte datos de asistentes de grupos a RegistroRetornoGrupoDetallado.
    No realiza acceso a datos, solo transforma la información recibida.
    """

    @staticmethod
    def mapear_grupos_con_asistentes(
        registros_grupos: list[RegistroRetornoGrupo],
        asistentes_usuarios: list[tuple[int, Usuario]],
        asistentes_personas: list[tuple[int, Persona]],
    ) -> list[RegistroRetornoGrupoDetallado]:
        """
        Convierte RegistroRetornoGrupo a RegistroRetornoGrupoDetallado,
        asociando usuarios y personas a sus grupos correspondientes.

        Args:
            registros_grupos: Lista de RegistroRetornoGrupo (deben tener grupo_retorno_rel cargado)
            asistentes_usuarios: Lista de tuplas (gr_codigo, Usuario)
            asistentes_personas: Lista de tuplas (gr_codigo, Persona)

        Returns:
            Lista de RegistroRetornoGrupoDetallado con la información transformada
        """
        resultados: list[RegistroRetornoGrupoDetallado] = []

        # Crear diccionarios agrupados por grupo
        usuarios_por_grupo: dict[int, list[Usuario]] = {}
        personas_por_grupo: dict[int, list[Persona]] = {}

        for gr_codigo, usuario in asistentes_usuarios:
            if gr_codigo not in usuarios_por_grupo:
                usuarios_por_grupo[gr_codigo] = []
            usuarios_por_grupo[gr_codigo].append(usuario)

        for gr_codigo, persona in asistentes_personas:
            if gr_codigo not in personas_por_grupo:
                personas_por_grupo[gr_codigo] = []
            personas_por_grupo[gr_codigo].append(persona)

        # Mapear cada registro de grupo
        for registro_grupo in registros_grupos:
            try:
                registro_detallado = RegistroRetornoGrupoDetalladoMapper.mapear_grupo_con_asistentes(
                    registro_grupo,
                    usuarios_por_grupo.get(registro_grupo.cod_grupo, []),
                    personas_por_grupo.get(registro_grupo.cod_grupo, []),
                )
                resultados.append(registro_detallado)
            except (AttributeError, ValueError) as e:
                # Si falta información crítica, saltamos este grupo
                print(f"Error al mapear grupo {registro_grupo.cod_grupo}: {str(e)}")
                continue

        return resultados

    @staticmethod
    def mapear_grupo_con_asistentes(
        registro_grupo: RegistroRetornoGrupo,
        usuarios_del_grupo: list[Usuario],
        personas_del_grupo: list[Persona],
    ) -> RegistroRetornoGrupoDetallado:
        """
        Convierte un único RegistroRetornoGrupo a RegistroRetornoGrupoDetallado.

        Args:
            registro_grupo: Registro del grupo de retorno (debe tener grupo_retorno_rel cargado)
            usuarios_del_grupo: Lista de Usuario del grupo
            personas_del_grupo: Lista de Persona del grupo

        Returns:
            RegistroRetornoGrupoDetallado con la información transformada

        Raises:
            AttributeError: Si falta información crítica en el registro o grupo
        """
        # Obtener información del grupo y líder
        grupo_retorno = registro_grupo.grupo_retorno_rel
        lider = grupo_retorno.lider

        # Combinar nombres, omitiendo al líder
        nombres_asistentes = [
            f"{usuario.us_nombre} {usuario.us_apellido}"
            for usuario in usuarios_del_grupo
            if usuario.us_codigo != lider.us_codigo
        ] + [
            f"{persona.pe_nombre} {persona.pe_apellido}"
            for persona in personas_del_grupo
        ]

        # Crear y retornar RegistroRetornoGrupoDetallado
        return RegistroRetornoGrupoDetallado(
            cod_grupo=registro_grupo.cod_grupo,
            lider_nombre=f"{lider.us_nombre} {lider.us_apellido}",
            lider_celular=lider.us_celular,
            nombre_usuarios=nombres_asistentes,
            notas=registro_grupo.anotacion,
            num_hospedaje=registro_grupo.num_hospedaje,
            num_transporte=registro_grupo.num_transporte,
            num_parqueadero_motos=registro_grupo.num_parqueadero_moto,
            num_parqueadero_carros=registro_grupo.num_parqueadero_carro,
        )

class RegistroRetornoIndividualDetalladoMapper:
    
    @staticmethod
    def mapear_usuarios_asistentes(usuarios_asistentes: list[Usuario, RegistroRetorno]) -> list[RegistroRetornoUsuarioDetallado]:
        usuarios_mapeados: list[RegistroRetornoUsuarioDetallado] = []
        for us, reg in usuarios_asistentes:
            usuarios_mapeados.append(RegistroRetornoUsuarioDetallado(
                celular = us.us_celular,
                nombre = f"{us.us_nombre} {us.us_apellido}",
                notas = reg.anotacion,
                num_hospedaje = reg.num_hospedaje,
                num_transporte = reg.num_transporte,
                num_parqueadero_motos = reg.num_parqueadero_moto,
                num_parqueadero_carros = reg.num_parqueadero_carro
            ))
        return usuarios_mapeados

