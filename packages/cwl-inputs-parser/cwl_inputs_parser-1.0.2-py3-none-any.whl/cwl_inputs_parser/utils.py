#!/usr/bin/env python3
# coding: utf-8
import io
import json
import logging
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Union, cast

import ruamel.yaml
from cwl_utils.parser import load_document_by_string
from cwl_utils.parser.cwl_v1_2 import (CommandInputArraySchema,
                                       CommandInputEnumSchema,
                                       CommandInputParameter,
                                       CommandInputRecordSchema,
                                       CommandLineTool, ExpressionTool,
                                       InputArraySchema, InputRecordSchema,
                                       Workflow)
from cwltool.main import RuntimeContext, arg_parser, argcomplete
from cwltool.main import fetch_document as cwltool_fetch_document
from cwltool.main import (generate_input_template, get_default_args, make_tool,
                          resolve_and_validate_document, resolve_tool_uri,
                          setup_loadingContext)
from requests import get
from ruamel.yaml.main import YAML

CWLUtilObj = Union[CommandLineTool, Workflow, ExpressionTool]
CWLUtilLoadResult = Union[List[CWLUtilObj], CWLUtilObj]


def download_file(remote_url: str) -> str:
    """Downloads a file from a URL and returns the content."""
    response = get(remote_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: {remote_url}")
    return response.text


def is_remote_url(location: str) -> bool:
    """Returns True if the path is a remote URL."""
    return location.startswith("http://") or location.startswith("https://")


def fetch_document(location: Union[str, Path]) -> str:
    """Fetches a CWL document from a file path or a remote URL."""
    if isinstance(location, str):
        if is_remote_url(location):
            return download_file(location)
        location = Path(location)
    if location.is_absolute():
        return location.read_text(encoding="utf-8")
    return Path().cwd().joinpath(location).read_text(encoding="utf-8")


def as_uri(location: Union[str, Path]) -> str:
    """Converts a location to a URI."""
    if isinstance(location, str):
        if is_remote_url(location):
            return location
        location = Path(location)
    if not location.is_absolute():
        location = Path().cwd().joinpath(location)
    return location.as_uri()


def extract_main_tool(cwl_obj: CWLUtilLoadResult) -> CWLUtilObj:
    """Extracts the main tool from a CWL object."""
    if isinstance(cwl_obj, list):
        for obj in cwl_obj:
            if obj.class_ == "Workflow" or str(obj.id).rsplit("#", maxsplit=1)[-1] == "main":  # noqa: E501
                return obj
    return cast(CWLUtilObj, cwl_obj)


class UnsupportedValueError(Exception):
    """Raised when an unsupported value is encountered."""


@dataclass
class SecondaryFile:
    """SecondaryFile"""
    pattern: Optional[str] = None
    required: Optional[bool] = True


@dataclass
class InputField:
    """
    InputField
    example:
    {
        "default": null,
        "doc": "doc example",
        "id": "id example",
        "label": "label example",
        "type": "File",
        "required": true,
        "secondaryFiles": [
            {
                "pattern": "pattern example",
                "required": true,
            }
        ],
    }
    """
    default: Optional[Any] = None
    doc: Optional[str] = None
    id: Optional[str] = None
    label: Optional[str] = None
    type: Optional[str] = None
    array: bool = False
    required: bool = True
    secondaryFiles: Optional[List[SecondaryFile]] = None


class Inputs:
    """Generates InputField from a cwl-utils object."""

    def __init__(self, cwl_obj: CWLUtilLoadResult) -> None:
        self.ori_cwl_obj = deepcopy(cwl_obj)
        self.cwl_obj = deepcopy(extract_main_tool(cwl_obj))
        self.fields: List[InputField] = []
        self._parse()

    def as_json(self) -> str:
        """Dump as json."""
        def encode_default(item: Any) -> Dict[str, Any]:
            if isinstance(item, object) and hasattr(item, '__dict__'):
                return item.__dict__
            else:
                raise TypeError

        return json.dumps(self.fields, default=encode_default, indent=2)

    def as_dict(self) -> Any:
        """Dump as dict."""
        str_json = self.as_json()
        return json.loads(str_json)

    def _parse(self) -> None:
        """Parses inputs field from the CWL object."""
        for inp_obj in self.cwl_obj.inputs:
            if isinstance(inp_obj.type, str):
                inp_field = self._typical_field(inp_obj)
            elif isinstance(inp_obj.type, list):
                if len(inp_obj.type) == 1:
                    tmp_obj = deepcopy(inp_obj)
                    tmp_obj.type = inp_obj.type[0]
                    if isinstance(tmp_obj.type, str):
                        inp_field = self._typical_field(tmp_obj)
                    elif isinstance(tmp_obj.type, CommandInputArraySchema):
                        inp_field = self._command__input_array_field(tmp_obj)  # noqa: E501
                    elif isinstance(tmp_obj.type, InputArraySchema):
                        inp_field = self._input_array_field(tmp_obj)
                    else:
                        raise UnsupportedValueError("The type field contains an unsupported format")  # noqa: E501
                elif len(inp_obj.type) == 2:
                    if 'null' in inp_obj.type:
                        tmp_obj = deepcopy(inp_obj)
                        for t in inp_obj.type:
                            if t != 'null':
                                tmp_obj.type = t
                        inp_field = self._typical_field(tmp_obj)
                        inp_field.required = False
                    else:
                        # [TODO] not support
                        raise UnsupportedValueError("The union field does not support by cwl-inputs-parser")  # noqa: E501
                else:
                    # [TODO] not support
                    raise UnsupportedValueError("The union field does not support by cwl-inputs-parser")  # noqa: E501
            elif isinstance(inp_obj.type, CommandInputArraySchema):
                if inp_obj.type.items not in ["boolean", "int", "string", "File", "Directory", "Any"]:  # noqa: E501
                    raise UnsupportedValueError("The type field contains an unsupported format")  # noqa: E501
                inp_field = self._command__input_array_field(inp_obj)
            elif isinstance(inp_obj.type, CommandInputEnumSchema):
                # [TODO] not support
                # inp_field = self._command_input_enum_field(inp_obj)
                raise UnsupportedValueError("The CommandInputEnumSchema field does not support by cwl-inputs-parser")  # noqa: E501
            elif isinstance(inp_obj.type, CommandInputRecordSchema):
                # [TODO] not support
                # inp_field = self._command_input_record_field(inp_obj)
                raise UnsupportedValueError("The CommandInputRecordSchema field does not support by cwl-inputs-parser")  # noqa: E501
            elif isinstance(inp_obj.type, InputArraySchema):
                if isinstance(inp_obj.type.items, InputRecordSchema):
                    # [TODO] not support
                    raise UnsupportedValueError("The InputRecordSchema field in the InputArraySchema field does not support by cwl-inputs-parser")  # noqa: E501
                if inp_obj.type.items not in ["boolean", "int", "string", "File", "Directory", "Any"]:  # noqa: E501
                    raise UnsupportedValueError("The type field contains an unsupported format")  # noqa: E501
                inp_field = self._input_array_field(inp_obj)
            elif isinstance(inp_obj.type, InputRecordSchema):
                # [TODO] not support
                raise UnsupportedValueError("The InputRecordSchema field does not support by cwl-inputs-parser")  # noqa: E501
            else:
                # [TODO] not support
                raise UnsupportedValueError("The type field contains an unsupported format")  # noqa: E501

            if inp_field.type == "File":
                if inp_obj.secondaryFiles:
                    inp_field.secondaryFiles = []
                    for secondary_file in inp_obj.secondaryFiles:
                        required = secondary_file.required
                        pattern = secondary_file.pattern
                        if pattern.endswith("?"):
                            required = False
                            pattern = pattern.rstrip("?")
                        if required is None:
                            required = True
                        inp_field.secondaryFiles.append(
                            SecondaryFile(
                                pattern=pattern,
                                required=required
                            )
                        )

            self.fields.append(inp_field)

    def _typical_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a typical fields
        like: boolean, int, string, File, stdin, Directory, Any
        """
        if inp_obj.type == "boolean":
            return self._boolean_field(inp_obj)
        elif inp_obj.type == "int":
            return self._int_field(inp_obj)
        elif inp_obj.type == "string":
            return self._string_field(inp_obj)
        elif inp_obj.type == "File":
            return self._file_field(inp_obj)
        elif inp_obj.type == "stdin":
            return self._stdin_field(inp_obj)
        elif inp_obj.type == "Directory":
            return self.directory_field(inp_obj)
        elif inp_obj.type == "Any":
            return self.any_field(inp_obj)
        else:
            # [TODO] not support
            raise UnsupportedValueError("The type field contains an unsupported format")  # noqa: E501

    @staticmethod
    def _clean_val(val: Optional[Any]) -> Optional[Any]:
        """Cleans a value field."""
        if isinstance(val, str):
            return deepcopy(val).replace("\n", " ").strip()
        return deepcopy(val)

    def _template_field(self, inp_obj: CommandInputParameter) -> InputField:
        """Generates a InputField template from a CWL InputParameter."""
        id_ = self._clean_val(inp_obj.id)
        if isinstance(id_, str):
            id_ = id_.split("#")[-1]
        return InputField(
            default=deepcopy(inp_obj.default),
            doc=self._clean_val(inp_obj.doc),
            id=id_,
            label=self._clean_val(inp_obj.label),
            type=self._clean_val(inp_obj.type),
        )

    def _boolean_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/revsort-packed.cwl'
        {
            'default': True,
            'doc': 'If true, reverse (decending) sort',
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#main/reverse_sort',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7feb232f7be0>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'boolean'
        }
        make-template result:
        reverse_sort: true  # default value of type "boolean".
        """
        return self._template_field(inp_obj)

    def _int_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/bwa-mem-tool.cwl'
        {
            'default': None,
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#minimum_seed_length',  # noqa: E501
            'inputBinding': <cwl_utils.parser.cwl_v1_2.CommandLineBinding object at 0x7f3c1af41220>, # noqa: E501
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f3c1cdec730>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'int'
        }
        make-template result:
        minimum_seed_length: 0  # type "int"
        """
        return self._template_field(inp_obj)

    def _string_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/pass-unconnected.cwl'
        {
            'default': 'hello inp2',
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#inp2',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7fd904cfe370>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'string'
        }
        make-template result:
        inp2: hello inp2  # default value of type "string".
        """
        return self._template_field(inp_obj)

    def _file_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/count-lines5-wf.cwl'
        {
            'default': ordereddict([('class', 'File'), ('location', 'hello.txt')]),
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#file1',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7fa708c4b0d0>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'File'
        }
        make-template result:
        file1: {class: File, location: file:///app/tests/cwl_conformance_test/v1.2/hello.txt}  # default value of type "File".

        Basically, all path and location can be treated as location.
        > As a special case, if the path field is provided but the
        location field is not, an implementation may assign the value
        of the path field to location, and remove the path field.
        """
        field = self._template_field(inp_obj)
        if isinstance(inp_obj.default, OrderedDict) and len(inp_obj.default) != 0:  # noqa: E501
            if "location" in inp_obj.default:
                field.default = inp_obj.default["location"]
            elif "path" in inp_obj.default:
                field.default = inp_obj.default["path"]
        return field

    def _stdin_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/cat-tool-shortcut.cwl'
        {
            'default': None,
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#file1',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f3f40a59d60>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'stdin'
        }
        make-template result:
        file1:  # type "File"
            class: File
            path: a/file/path
        """
        field = self._file_field(inp_obj)
        field.type = "File"
        return field

    def directory_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/dir.cwl'
        {
            'default': None,
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#indir',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f44a93efca0>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'Directory'
        }
        make-template result:
        indir:  # type "Directory"
            class: Directory
            path: a/directory/path
        """
        return self._template_field(inp_obj)

    def any_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/null-expression1-tool.cwl'
        {
            'default': 'the-default',
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#i1',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f8774eba220>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': 'Any'
        }
        make-template result:
        i1: "the-default"  # default value of type "Any".
        """
        return self._template_field(inp_obj)

    def _command__input_array_field(self, inp_obj: CommandInputParameter) -> InputField:  # noqa: E501
        """
        Generates a InputField from a CWL InputParameter.
        [TODO] more check
        inp_obj example from 'v1.2/docker-array-secondaryfiles.cwl'
        {
            'default': None,
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#fasta_path',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7fd3104d2130>,  # noqa: E501
            'secondaryFiles': [<cwl_utils.parser.cwl_v1_2.SecondaryFileSchema object at 0x7fd3104e27c0>,  # noqa: E501
                                <cwl_utils.parser.cwl_v1_2.SecondaryFileSchema object at 0x7fd3104e2940>,  # noqa: E501
                                <cwl_utils.parser.cwl_v1_2.SecondaryFileSchema object at 0x7fd3104e2a60>],  # noqa: E501
            'streamable': None,
            'type': <cwl_utils.parser.cwl_v1_2.CommandInputArraySchema object at 0x7fd3104e2dc0>
        }

        make-template result:
        require_dat: false  # type "boolean" (optional)
        fasta_path:  # array of type "File"
        - class: File
            path: a/file/path

        secondaryFiles:
        {'extension_fields': ordereddict(),
        'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f634a456460>,
        'pattern': '.bai',
        'required': False}
        {'extension_fields': ordereddict(),
        'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f634a456460>,
        'pattern': "${ if (inputs.require_dat) {return '.dat'} else {return null} }",
        'required': None}
        {'extension_fields': ordereddict(),
        'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f634a456460>,
        'pattern': '${ return null; }',
        'required': None}
        """
        field = self._template_field(inp_obj)
        field.type = inp_obj.type.items
        field.array = True
        return field

    def _command_input_enum_field(self, inp_obj: CommandInputParameter) -> NoReturn:  # noqa: E501
        """
        Generates a InputField from a CWL InputParameter.

        [TODO] do not know how to handle enum field in CWL.
        """

    def _command_input_record_field(self, inp_obj: CommandInputParameter) -> NoReturn:  # noqa: E501
        """
        Generates a InputField from a CWL InputParameter.
        v1.2/record-output.cwl
        v1.2/anon_enum_inside_array.cwl
        v1.2/record-in-secondaryFiles.cwl
        v1.2/record-in-format.cwl
        v1.2/record-out-format.cwl

        [TODO] do not know how to handle record field in CWL.
        """

    def _input_array_field(self, inp_obj: CommandInputParameter) -> InputField:
        """
        Generates a InputField from a CWL InputParameter.
        inp_obj example from 'v1.2/count-lines3-wf.cwl'
        {
            'default': None,
            'doc': None,
            'extension_fields': ordereddict(),
            'format': None,
            'id': 'file:///app/tests/cwl_conformance_test/#file1',
            'inputBinding': None,
            'label': None,
            'loadContents': None,
            'loadListing': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f26ca1b2160>,  # noqa: E501
            'secondaryFiles': None,
            'streamable': None,
            'type': <cwl_utils.parser.cwl_v1_2.InputArraySchema object at 0x7f26ca1422e0>
        }
        type:
        {
            'doc': None,
            'extension_fields': ordereddict(),
            'items': 'File',
            'label': None,
            'loadingOptions': <cwl_utils.parser.cwl_v1_2.LoadingOptions object at 0x7f26ca1b2160>,
            'name': '_:7db2ff08-5fed-4261-b514-fe5eccc43048',
            'type': 'array'
        }

        make-template result:
        file1:  # array of type "File"
            - class: File
                path: a/file/path
        """
        field = self._template_field(inp_obj)
        field.type = inp_obj.type.items
        field.array = True
        if field.label is None:
            field.label = self._clean_val(inp_obj.type.label)
        if field.doc is None:
            field.doc = self._clean_val(inp_obj.type.doc)
        return field


def wf_location_to_inputs(wf_location: Union[str, Path]) -> Inputs:
    """
    Generates Inputs from a location of CWL Workflow.
    """
    wf_docs = fetch_document(wf_location)
    wf_obj = load_document_by_string(wf_docs, uri=as_uri(wf_location))
    return Inputs(wf_obj)


def cwl_make_template(wf_location: Union[str, Path]) -> str:
    """Returns the results of cwltool --make-template."""
    logging.getLogger("cwltool").setLevel(logging.ERROR)
    logging.getLogger("salad").setLevel(logging.ERROR)

    parser = arg_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args(["--make-template", str(wf_location)])
    for key, val in get_default_args().items():
        if not hasattr(args, key):
            setattr(args, key, val)
    runtimeContext = RuntimeContext(vars(args))
    loadingContext = setup_loadingContext(None, runtimeContext, args)
    uri, _ = resolve_tool_uri(
        args.workflow,
        resolver=loadingContext.resolver,
        fetcher_constructor=loadingContext.fetcher_constructor,
    )
    loadingContext, workflowobj, uri = cwltool_fetch_document(
        uri,
        loadingContext
    )
    loadingContext, uri = resolve_and_validate_document(
        loadingContext,
        workflowobj,
        uri,
    )

    def my_represent_none(self: Any, data: Any) -> Any:
        """Force clean representation of 'null'."""
        return self.represent_scalar("tag:yaml.org,2002:null", "null")

    ruamel.yaml.representer.RoundTripRepresenter.add_representer(
        type(None), my_represent_none
    )
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent = 4
    yaml.block_seq_indent = 2
    buf = io.BytesIO()
    yaml.dump(generate_input_template(make_tool(uri, loadingContext)), buf)
    yaml_str = buf.getvalue().decode("utf-8")

    return yaml_str
