import re
import typing as T

import pandas as pd

from pycollimator.error import NotFoundError
from pycollimator.i18n import N
from pycollimator.log import Log
from pycollimator.utils import is_uuid


# Current structure of SimulationModel:
# "diagram" : { ModelDiagram }
# "submodels": {
#   "references": {
#      "<uuid>": { "diagram_uuid": "<uuid>" },
#       ...
#   },
#   "diagrams": {
#     "<uuid>": { ModelDiagram }
#   }
# }


# FIXME FIXME FIXME
# We don't have a strong representation of the model, and we create
# Block objects on the fly. Modifying them means we need to backtrack
# to the model and update it somehow. Right now this scenario is limited
# to DataSourceBlock input data. We don't really want to allow modifying
# the model, so it's kinda okay. At least for now.


class Block:
    """
    Representation of a block in a model.

    Can be returned to the API user.
    """

    @classmethod
    def from_data(cls, data, model):
        if data.get("type") == "core.DataSource":
            return DataSourceBlock(data, model)
        return cls(data, model)

    def __init__(self, block_json, model):
        self.model = model
        self._json = block_json

    def __getitem__(self, key):
        return self._json[key]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if Log.is_level_above("DEBUG"):
            return f"<{self.__class__.__name__} name='{self.name}' type='{self.type}' uuid='{self.uuid}'>"
        return f"<{self.__class__.__name__} name='{self.name}' type='{self.type}'>"

    @property
    def name(self):
        return self._json["name"]

    @property
    def uuid(self):
        return self._json["uuid"]

    @property
    def type(self):
        return self._json["type"]

    @property
    def path(self):
        return self.model.get_block_path(self.uuid)

    # @property
    # def parameters(self):
    #     return self._json["parameters"]

    def get_parameter(self, name: str, no_eval=False):
        param = self._json["parameters"].get(name)
        Log.trace(f"get_parameter: {name}={param}")
        if param is None:
            raise NotFoundError(N(f"Block '{self}' of type '{self.type}' does not have parameter '{name}'"))
        if param.get("is_string", False) is True:
            return str(param["value"])
        if no_eval is True:
            return param["value"]
        expr = param.get("expression") or param["value"]
        evaluated = eval(expr)
        return evaluated


class DataSourceBlock(Block):
    def __init__(self, block_json, model):
        if block_json.get("type") != "core.DataSource":
            raise TypeError(N("DataSourceBlock must be created from a DataSource block"))
        super().__init__(block_json, model)
        self.data = None

    def set_data(self, data: pd.DataFrame):
        # FIXME make sure the shape is correct and all that
        if not isinstance(data, pd.DataFrame):
            raise TypeError(N("Input data must be a pandas DataFrame"))
        # set data of a DataSource block
        Log.trace("set_data, shape:", data.shape, "block:", self.__repr__())
        self.data = data.copy()
        self.data.index.name = "time"
        self.model._set_datasource_data(self, self.data)


class ModelDiagram:
    """
    Contents of a fully loaded model diagram (single plane).

    For use by internal APIs.
    """

    def __init__(self, data, model):
        self.model = model
        self.diagram = data

    def __str__(self) -> str:
        if self.diagram.get("name") is not None:
            return self.diagram["name"]
        return self.diagram["uuid"]

    def __repr__(self) -> str:
        if Log.is_level_above("DEBUG"):
            return f"<{self.__class__.__name__} model='{self.model}' uuid='{self.uuid}'>"
        return f"<{self.__class__.__name__} model='{self.model}'>"

    @property
    def nodes(self):
        return self.diagram.get("nodes", [])

    @property
    def links(self):
        return self.diagram.get("links", [])

    def find_block(
        self, pattern: str = None, name: str = None, uuid: str = None, type: str = None, ignorecase=True
    ) -> T.Optional[Block]:
        blocks = self.find_blocks(pattern=pattern, name=name, uuid=uuid, type=type, case=ignorecase)
        if len(blocks) == 0:
            return None
        if len(blocks) > 1:
            raise NotFoundError(N(f"Multiple blocks found for '{name}' in model '{self}'"))
        return blocks[0]

    def find_blocks(
        self, pattern: str = None, name: str = None, uuid: str = None, type: str = None, case=True
    ) -> list[Block]:
        found = None

        if uuid is None and name is None and pattern is None and type is None:
            pattern = ""

        if uuid is not None:
            found = [
                Block.from_data(node, self.model) for node in self.nodes if node.get("uuid").lower() == uuid.lower()
            ]
        if pattern is not None:
            rgx = re.compile(pattern, re.IGNORECASE if not case else 0)
            found = [Block.from_data(node, self.model) for node in self.nodes if rgx.match(node.get("name"))]
        if name is not None:
            if not case:
                found = [
                    Block.from_data(node, self.model)
                    for node in self.nodes
                    if node.get("name", "").lower() == name.lower()
                ]
            else:
                found = [Block.from_data(node, self.model) for node in self.nodes if node.get("name") == name]

        # If type is set: filter by type, or return all blocks of the given type if no other search criteria was set
        if type is not None:
            if not type.startswith("core."):
                type = "core." + type
            type = type.lower()
            if uuid is None and name is None and pattern is None:
                found = [Block.from_data(node, self.model) for node in self.nodes if node.get("type").lower() == type]
            else:
                found = [blk for blk in found if blk.type.lower() == type]

        return found


class ModelGraph:
    """
    Contents of a fully loaded model graph (all loadable planes).

    For use by internal APIs.
    """

    def __init__(self, data, model):
        self._data = data
        self._model = model
        self.uuid = data.get("uuid")
        self.name = data.get("name")
        self.root_diagram = ModelDiagram(data["diagram"], model=self._model)
        self.diagrams_by_submodel_uuid = {}  # type: T.Dict[str, ModelDiagram]

        submodel_references = data.get("submodels", {}).get("references", {})
        submodel_diagrams = data.get("submodels", {}).get("diagrams", {})
        for submodel_uuid in submodel_references:
            ref = submodel_references[submodel_uuid]
            diagram_uuid = ref["diagram_uuid"]
            diagram = submodel_diagrams[diagram_uuid]
            self.diagrams_by_submodel_uuid[submodel_uuid] = ModelDiagram(diagram, model)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if Log.is_level_above("DEBUG"):
            return f"<{self.__class__.__name__} model='{self._model}' uuid='{self.uuid}'>"
        return f"<{self.__class__.__name__} model='{self._model}'>"

    # def get_diagram(self, diagram_uuid: str = None):
    #     if diagram_uuid is None:
    #         return self.root_diagram
    #     return ModelDiagram(self._data["diagrams"][diagram_uuid], model=self._model)

    # def get_submodel_diagram(self, submodel_uuid):
    #     return ModelDiagram(
    #         self.get_diagram(self._data["submodels"]["references"][submodel_uuid]["diagram_uuid"]), model=self._model
    #     )

    # FIXME walk and construct blocks paths
    def find_blocks(
        self, pattern: str = None, name: str = None, uuid: str = None, type: str = None, case=True
    ) -> list[Block]:
        found = []

        # find in root diagram
        nodes = self.root_diagram.find_blocks(pattern=pattern, name=name, uuid=uuid, type=type, case=case)
        for node in nodes:
            found.append(node)

        # walk through submodel
        # FIXME: this walks submodels in random order and doesn't know blocks paths
        for submodel_uuid in self.diagrams_by_submodel_uuid:
            submodel_diagram = self.diagrams_by_submodel_uuid[submodel_uuid]
            nodes = submodel_diagram.find_blocks(pattern=pattern, name=name, uuid=uuid, type=type, case=case)
            for node in nodes:
                found.append(node)

        return found

    def _get_block_path(self, diagram: ModelDiagram, block_uuid: str, pfx: str) -> str:
        for node in diagram.nodes:
            if node["uuid"] == block_uuid:
                return f"{pfx}{node['name']}"
            if node["type"] == "core.Submodel":
                submodel_diagram = self.diagrams_by_submodel_uuid[node["uuid"]]
                found = self._get_block_path(submodel_diagram, block_uuid, f"{pfx}{node['name']}.")
                if found:
                    return found
        return None

    def get_block_path(self, block):
        """
        Get the path of a block in the model.
        """
        if not isinstance(block, Block):
            if is_uuid(block):
                blocks = self.find_blocks(uuid=block)
            else:
                blocks = self.find_blocks(name=block)
            if len(blocks) == 0:
                blocks = self.find_blocks(pattern=block)
            if len(blocks) == 0:
                raise NotFoundError(N(f"No block found for '{block}'"))
            if len(blocks) > 1:
                raise NotFoundError(N(f"Multiple blocks found for '{block}'"))
        return self._get_block_path(self.root_diagram, block, "")
