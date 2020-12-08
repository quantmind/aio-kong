from typing import List

from .components import CrudComponent, JsonType


class Snis(CrudComponent):
    """Kong SNI API component"""

    async def apply_json(self, data: JsonType, clear: bool = True) -> List:
        """Apply a JSON data objects for snis - never clear them"""
        if not isinstance(data, list):
            data = [data]
        result = []
        for entry in data:
            entry = entry.copy()
            name = entry.pop("name")
            if await self.has(name):
                sni = await self.update(name, **entry)
            else:
                sni = await self.create(name=name, **entry)
            result.append(sni.data)
        return result
