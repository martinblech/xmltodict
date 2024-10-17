from typing import Any, Callable, Union, IO, Iterator, List, Tuple, Optional, Dict

class ParsingInterrupted(Exception): ...

class _DictSAXHandler:
    path: List[Tuple[str, Dict[str, Any]]]
    stack: List[Tuple[Optional[Dict[str, Any]], List[str]]]
    data: List[str]
    item: Optional[Dict[str, Any]]
    item_depth: int
    xml_attribs: bool
    item_callback: Callable[..., Any]
    attr_prefix: str
    cdata_key: str
    force_cdata: bool
    cdata_separator: str
    postprocessor: Optional[Callable[..., Any]]
    dict_constructor: Callable[..., Any]
    strip_whitespace: bool
    namespace_separator: str
    namespaces: Optional[Dict[str, str]]
    force_list: Union[None, Tuple[str], Callable[..., Any]]
    comment_key: str
    def __init__(
        self,
        item_depth: int = ...,
        item_callback: Callable[..., Any] = ...,
        xml_attribs: bool = ...,
        attr_prefix: str = ...,
        cdata_key: str = ...,
        force_cdata: bool = ...,
        cdata_separator: str = ...,
        postprocessor: Any | None = ...,
        dict_constructor: Callable[..., Any] = ...,
        strip_whitespace: bool = ...,
        namespace_separator: str = ...,
        namespaces: Any | None = ...,
        force_list: Any | None = ...,
        comment_key: str = ...,
    ): ...
    def startNamespaceDecl(self, prefix: str, uri: str) -> None: ...
    def startElement(
        self, full_name: str, attrs: Union[Dict[str, Any], List[Any]]
    ) -> None: ...
    def endElement(self, full_name: str) -> None: ...
    def characters(self, data: str) -> None: ...
    def comments(self, data: str) -> None: ...
    def push_data(
        self, item: Optional[Dict[str, Any]], key: str, data: Any
    ) -> Optional[Dict[str, Any]]: ...

def parse(
    xml_input: Union[str, bytes, IO[str], Iterator[bytes]],
    encoding: Optional[str] = ...,
    expat: Any = ...,
    process_namespaces: bool = ...,
    namespace_separator: str = ...,
    disable_entities: bool = ...,
    process_comments: bool = ...,
    **kwargs: Any
) -> Dict[str, Any]: ...
def unparse(
    input_dict: Dict[str, Any],
    output: Any | None = ...,
    encoding: str = ...,
    full_document: bool = ...,
    short_empty_elements: bool = ...,
    **kwargs: Any
) -> Optional[str]: ...
