from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Time:
	"""Time commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def get_post(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:TIME:POST \n
		Snippet: value: float = driver.scenario.localized.marker.time.get_post() \n
		Specifies post marker time. \n
			:return: post: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:TIME:POST?')
		return Conversions.str_to_float(response)

	def set_post(self, post: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:TIME:POST \n
		Snippet: driver.scenario.localized.marker.time.set_post(post = 1.0) \n
		Specifies post marker time. \n
			:param post: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(post)
		self._core.io.write(f'SCENario:LOCalized:MARKer:TIME:POST {param}')

	def get_pre(self) -> float:
		"""SCPI: SCENario:LOCalized:MARKer:TIME:PRE \n
		Snippet: value: float = driver.scenario.localized.marker.time.get_pre() \n
		Specifies pre marker time. \n
			:return: pre: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('SCENario:LOCalized:MARKer:TIME:PRE?')
		return Conversions.str_to_float(response)

	def set_pre(self, pre: float) -> None:
		"""SCPI: SCENario:LOCalized:MARKer:TIME:PRE \n
		Snippet: driver.scenario.localized.marker.time.set_pre(pre = 1.0) \n
		Specifies pre marker time. \n
			:param pre: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(pre)
		self._core.io.write(f'SCENario:LOCalized:MARKer:TIME:PRE {param}')
