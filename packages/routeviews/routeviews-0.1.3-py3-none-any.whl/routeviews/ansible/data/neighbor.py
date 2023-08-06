import dataclasses
import logging
from typing import Dict, List

from routeviews import parse, types, yaml

logger = logging.getLogger(__name__)


DEFAULT_ORDER = ['peer_address', 'peer_as', 'description', 'afi_safis', 'options']

@dataclasses.dataclass
class NeighborConfig:
    peer_as: int
    peer_address: types.IPAddr
    description: str = None
    afi_safis: List[str] = None
    options: Dict = None
    _order: List[str] = None

    @classmethod
    def from_data(cls, data: Dict):
        """Parse a NeighborConfig object from python native data structures.

        Args:
            neighbor_data (Dict): The data, e.g. parsed via PYyaml.

        Raises:
            KeyError: If the provided data structure does not contain expected key(s).

        Returns:
            NeighborConfig: A new neighbor config.
        """
        ipaddr = parse.IPAddr(data['peer_address'])
        return cls(
            peer_as=data['peer_as'],
            peer_address=ipaddr,
            description=data.get('description', None),
            afi_safis=data.get('afi_safis', None),
            options=data.get('options', None),
            _order=list(data.keys()),
        )

    def to_data(self):
        if self._order:
            return self._to_data_ordered(self._order)
        else:
            return self._to_data_ordered(DEFAULT_ORDER)

    def _to_data_ordered(self, order):
        data = {}
        for key in order:
            if hasattr(self, key) and getattr(self, key):
                if key == 'peer_address':
                    datum = str(getattr(self, key))
                else:
                    datum = getattr(self, key)
                data[key] = datum
        return data

    def diff(self, diff_marker='+'):
        as_yaml = yaml.dump(self.to_data())
        diff_lines = []
        for line in as_yaml.split('\n'):
            if line:
                new_line = f'{diff_marker} {line}'
                diff_lines.append(new_line)
        return '\n'.join(diff_lines)
