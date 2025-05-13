# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.node_parser import SentenceSplitter, CodeSplitter
from typing import Any, List, Sequence
from llama_index.core.node_parser.node_utils import (
    build_nodes_from_splits,
    default_id_func,
)
from llama_index.core.schema import (
    BaseNode,
    TextNode,
)
from llama_index.core.utils import get_tqdm_iterable

class CodeTransformer(NodeParser):

    def split_node(self, node: BaseNode) -> List[str]:
        node_metadata = node.metadata
        split_type = node_metadata.get("split_type", "default")
        if split_type == "code":
            langauge = node_metadata.get("language", "")
            if not langauge:
                raise ValueError("Language not specified in node metadata.")
            splitter = CodeSplitter.from_defaults(
                language=langauge,
            )
            return splitter.split_text(node.text)
        else:
            # Default to sentence splitting
            splitter = SentenceSplitter()
            return splitter.split_text(node.text)

    def _parse_nodes(
        self, nodes: Sequence[BaseNode], show_progress: bool = False, **kwargs: Any
    ) -> List[BaseNode]:
        all_nodes: List[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")
        for node in nodes_with_progress:
            splits = self.split_node(node)

            all_nodes.extend(
                build_nodes_from_splits(splits, node, id_func=self.id_func)
            )

        return all_nodes