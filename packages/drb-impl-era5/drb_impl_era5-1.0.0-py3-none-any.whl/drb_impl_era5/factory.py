from drb import DrbNode
from drb.factory import DrbFactory
from drb_impl_http import DrbHttpNode
from drb.exceptions import DrbFactoryException

from .era5_nodes import Era5ServiceNode


class Era5Factory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbHttpNode):
            node_era5_service = Era5ServiceNode(
                url=node.path.original_path,
                auth=node.auth)
        else:
            node_era5_service = Era5ServiceNode(node.path.name)
        try:
            node_era5_service.children
        except e:
            final_url = node.path.name.replace('+era5', '')
            raise DrbFactoryException(f'Unsupported Era5 service: {final_url}')
        return node_era5_service
