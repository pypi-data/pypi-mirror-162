from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Scan:
	"""Scan commands group definition. 89 total commands, 10 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scan", core, parent)

	@property
	def circular(self):
		"""circular commands group. 0 Sub-classes, 10 commands."""
		if not hasattr(self, '_circular'):
			from .Circular import Circular
			self._circular = Circular(self._core, self._cmd_group)
		return self._circular

	@property
	def conical(self):
		"""conical commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_conical'):
			from .Conical import Conical
			self._conical = Conical(self._core, self._cmd_group)
		return self._conical

	@property
	def custom(self):
		"""custom commands group. 2 Sub-classes, 0 commands."""
		if not hasattr(self, '_custom'):
			from .Custom import Custom
			self._custom = Custom(self._core, self._cmd_group)
		return self._custom

	@property
	def helical(self):
		"""helical commands group. 1 Sub-classes, 4 commands."""
		if not hasattr(self, '_helical'):
			from .Helical import Helical
			self._helical = Helical(self._core, self._cmd_group)
		return self._helical

	@property
	def lissajous(self):
		"""lissajous commands group. 0 Sub-classes, 7 commands."""
		if not hasattr(self, '_lissajous'):
			from .Lissajous import Lissajous
			self._lissajous = Lissajous(self._core, self._cmd_group)
		return self._lissajous

	@property
	def lsw(self):
		"""lsw commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_lsw'):
			from .Lsw import Lsw
			self._lsw = Lsw(self._core, self._cmd_group)
		return self._lsw

	@property
	def raster(self):
		"""raster commands group. 0 Sub-classes, 13 commands."""
		if not hasattr(self, '_raster'):
			from .Raster import Raster
			self._raster = Raster(self._core, self._cmd_group)
		return self._raster

	@property
	def sector(self):
		"""sector commands group. 0 Sub-classes, 10 commands."""
		if not hasattr(self, '_sector'):
			from .Sector import Sector
			self._sector = Sector(self._core, self._cmd_group)
		return self._sector

	@property
	def sin(self):
		"""sin commands group. 0 Sub-classes, 6 commands."""
		if not hasattr(self, '_sin'):
			from .Sin import Sin
			self._sin = Sin(self._core, self._cmd_group)
		return self._sin

	@property
	def spiral(self):
		"""spiral commands group. 0 Sub-classes, 9 commands."""
		if not hasattr(self, '_spiral'):
			from .Spiral import Spiral
			self._spiral = Spiral(self._core, self._cmd_group)
		return self._spiral

	def get_catalog(self) -> str:
		"""SCPI: SCAN:CATalog \n
		Snippet: value: str = driver.scan.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('SCAN:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: SCAN:COMMent \n
		Snippet: value: str = driver.scan.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('SCAN:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: SCAN:COMMent \n
		Snippet: driver.scan.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'SCAN:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: SCAN:CREate \n
		Snippet: driver.scan.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'SCAN:CREate {param}')

	def get_name(self) -> str:
		"""SCPI: SCAN:NAME \n
		Snippet: value: str = driver.scan.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('SCAN:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: SCAN:NAME \n
		Snippet: driver.scan.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'SCAN:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: SCAN:REMove \n
		Snippet: driver.scan.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'SCAN:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: SCAN:SELect \n
		Snippet: value: str = driver.scan.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('SCAN:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: SCAN:SELect \n
		Snippet: driver.scan.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'SCAN:SELect {param}')

	def get_steering(self) -> bool:
		"""SCPI: SCAN:STEering \n
		Snippet: value: bool = driver.scan.get_steering() \n
		Defines whether electronic steering is used. Electronic steering is only available for scan types that use phased array
		antennas. \n
			:return: steering: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCAN:STEering?')
		return Conversions.str_to_bool(response)

	def set_steering(self, steering: bool) -> None:
		"""SCPI: SCAN:STEering \n
		Snippet: driver.scan.set_steering(steering = False) \n
		Defines whether electronic steering is used. Electronic steering is only available for scan types that use phased array
		antennas. \n
			:param steering: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(steering)
		self._core.io.write(f'SCAN:STEering {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.ScanType:
		"""SCPI: SCAN:TYPE \n
		Snippet: value: enums.ScanType = driver.scan.get_type_py() \n
		Sets the scan type. \n
			:return: type_py: CIRCular| SECTor| RASTer| CONical| HELical| SPIRal| LSW| SIN| CUSTom| LISSajous
		"""
		response = self._core.io.query_str('SCAN:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ScanType)

	def set_type_py(self, type_py: enums.ScanType) -> None:
		"""SCPI: SCAN:TYPE \n
		Snippet: driver.scan.set_type_py(type_py = enums.ScanType.CIRCular) \n
		Sets the scan type. \n
			:param type_py: CIRCular| SECTor| RASTer| CONical| HELical| SPIRal| LSW| SIN| CUSTom| LISSajous
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.ScanType)
		self._core.io.write(f'SCAN:TYPE {param}')

	def clone(self) -> 'Scan':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Scan(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
