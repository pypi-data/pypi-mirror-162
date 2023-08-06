from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup
from ..Internal import Conversions
from .. import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Generator:
	"""Generator commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("generator", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.GeneratorType:
		"""SCPI: GENerator:TYPE \n
		Snippet: value: enums.GeneratorType = driver.generator.get_type_py() \n
		Sets the instrument's type. \n
			:return: type_py: SMU| SMM| SMBB| SW| SGT| SMBV| SMJ| SMW SMBB designates R&S SMBV100B.
		"""
		response = self._core.io.query_str('GENerator:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.GeneratorType)

	def set_type_py(self, type_py: enums.GeneratorType) -> None:
		"""SCPI: GENerator:TYPE \n
		Snippet: driver.generator.set_type_py(type_py = enums.GeneratorType.SGT) \n
		Sets the instrument's type. \n
			:param type_py: SMU| SMM| SMBB| SW| SGT| SMBV| SMJ| SMW SMBB designates R&S SMBV100B.
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.GeneratorType)
		self._core.io.write(f'GENerator:TYPE {param}')
