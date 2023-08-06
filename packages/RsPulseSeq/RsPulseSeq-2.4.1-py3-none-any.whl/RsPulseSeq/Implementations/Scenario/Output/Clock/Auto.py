from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Auto:
	"""Auto commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("auto", core, parent)

	def get_border(self) -> float:
		"""SCPI: SCENario:OUTPut:CLOCk:AUTO:BORDer \n
		Snippet: value: float = driver.scenario.output.clock.auto.get_border() \n
		Sets the minimum clock rate. \n
			:return: border: float Range: 1000 to 1e+08
		"""
		response = self._core.io.query_str('SCENario:OUTPut:CLOCk:AUTO:BORDer?')
		return Conversions.str_to_float(response)

	def set_border(self, border: float) -> None:
		"""SCPI: SCENario:OUTPut:CLOCk:AUTO:BORDer \n
		Snippet: driver.scenario.output.clock.auto.set_border(border = 1.0) \n
		Sets the minimum clock rate. \n
			:param border: float Range: 1000 to 1e+08
		"""
		param = Conversions.decimal_value_to_str(border)
		self._core.io.write(f'SCENario:OUTPut:CLOCk:AUTO:BORDer {param}')

	def get_oversampling(self) -> float:
		"""SCPI: SCENario:OUTPut:CLOCk:AUTO:OVERsampling \n
		Snippet: value: float = driver.scenario.output.clock.auto.get_oversampling() \n
		Sets the minimum oversampling factor. \n
			:return: oversampling: float Range: 1 to 1000
		"""
		response = self._core.io.query_str('SCENario:OUTPut:CLOCk:AUTO:OVERsampling?')
		return Conversions.str_to_float(response)

	def set_oversampling(self, oversampling: float) -> None:
		"""SCPI: SCENario:OUTPut:CLOCk:AUTO:OVERsampling \n
		Snippet: driver.scenario.output.clock.auto.set_oversampling(oversampling = 1.0) \n
		Sets the minimum oversampling factor. \n
			:param oversampling: float Range: 1 to 1000
		"""
		param = Conversions.decimal_value_to_str(oversampling)
		self._core.io.write(f'SCENario:OUTPut:CLOCk:AUTO:OVERsampling {param}')
