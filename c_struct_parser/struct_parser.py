#!/usr/bin/env python3
"""
Struct Parser Tool - Extract struct values from binary dumps

Copyright (C) 2025 Mohamed Elmoncef HAMDI mohamedelmoncef.hamdi@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import struct
import re
import argparse
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class DataType(Enum):
    BOOL = "bool"
    CHAR = "char"
    INT8 = "int8_t"
    INT16 = "int16_t"
    INT32 = "int32_t"
    INT64 = "int64_t"
    UINT8 = "uint8_t"
    UINT16 = "uint16_t"
    UINT32 = "uint32_t"
    UINT64 = "uint64_t"
    FLOAT = "float"
    DOUBLE = "double"
    POINTER = "pointer"
    STRUCT = "struct"
    ENUM = "enum"
    UNKNOWN = "unknown"


@dataclass
class ArrayInfo:
    dimensions: List[int]

    @property
    def total_size(self) -> int:
        result = 1
        for dim in self.dimensions:
            result *= dim
        return result


@dataclass
class FieldInfo:
    name: str
    type_name: str
    data_type: DataType
    offset: int
    size: int
    is_array: bool = False
    array_info: Optional[ArrayInfo] = None
    nested_struct: Optional["StructInfo"] = None


@dataclass
class StructInfo:
    name: str
    fields: List[FieldInfo]
    size: int
    alignment: int = 4


class StructParser:
    TYPE_SIZES = {
        DataType.BOOL: 1,
        DataType.CHAR: 1,
        DataType.INT8: 1,
        DataType.INT16: 2,
        DataType.INT32: 4,
        DataType.INT64: 8,
        DataType.UINT8: 1,
        DataType.UINT16: 2,
        DataType.UINT32: 4,
        DataType.UINT64: 8,
        DataType.FLOAT: 4,
        DataType.DOUBLE: 8,
        DataType.POINTER: 8,
        DataType.ENUM: 4,
    }

    STRUCT_FORMATS = {
        DataType.BOOL: "?",
        DataType.CHAR: "c",
        DataType.INT8: "b",
        DataType.INT16: "h",
        DataType.INT32: "i",
        DataType.INT64: "q",
        DataType.UINT8: "B",
        DataType.UINT16: "H",
        DataType.UINT32: "I",
        DataType.UINT64: "Q",
        DataType.FLOAT: "f",
        DataType.DOUBLE: "d",
        DataType.POINTER: "Q",
    }

    def __init__(self, definition_file: str):
        self.definition_file = definition_file
        self.structs_cache: Dict[str, StructInfo] = {}
        self.known_structs = self.extract_all_struct_names()

    def parse_data_type(self, type_str: str) -> DataType:
        """Determine data type from string"""
        type_map = {
            "bool": DataType.BOOL,
            "char": DataType.CHAR,
            "int8_t": DataType.INT8,
            "int16_t": DataType.INT16,
            "int32_t": DataType.INT32,
            "int64_t": DataType.INT64,
            "uint8_t": DataType.UINT8,
            "uint16_t": DataType.UINT16,
            "uint32_t": DataType.UINT32,
            "uint64_t": DataType.UINT64,
            "float": DataType.FLOAT,
            "double": DataType.DOUBLE,
        }

        for key, value in type_map.items():
            if key in type_str:
                return value

        if "*" in type_str:
            return DataType.POINTER
        elif type_str.endswith("_t"):
            return DataType.ENUM

        return DataType.UNKNOWN

    def extract_all_struct_names(self) -> Dict[str, str]:
        """
        Extract all 'typedef struct { ... } Name;' definitions.
        Returns dict: {name: body_text}
        """
        with open(self.definition_file, "r") as f:
            content = f.read()

        pattern = r"typedef\s+struct\s*{([^}]*)}\s*(\w+)\s*;"
        matches = re.findall(pattern, content, re.DOTALL)
        return {name.strip(): body.strip() for body, name in matches}

    def parse_array_dimensions(self, line: str) -> Optional[ArrayInfo]:
        """Extract array dimensions from field declaration"""
        pattern = r"\[(\d+)\]"
        matches = re.findall(pattern, line)
        if matches:
            dimensions = [int(m) for m in matches]
            return ArrayInfo(dimensions)
        return None

    def parse_field(
        self, line: str, current_offset: int, max_alignment: int
    ) -> Tuple[Optional[FieldInfo], int]:
        """Parse a single field with proper alignment."""
        line = line.strip().rstrip(";")
        if not line or line.startswith("//") or line.startswith("/*"):
            return None, current_offset

        array_info = self.parse_array_dimensions(line)
        is_array = array_info is not None
        clean_line = re.sub(r"\[.*?\]", "", line)

        parts = clean_line.split()
        if len(parts) < 1:
            return None, current_offset

        field_name = parts[-1]
        type_tokens = parts[:-1]
        if not type_tokens:
            return None, current_offset
        type_name = " ".join(type_tokens)

        base_type_str = type_tokens[0].lower()
        data_type = DataType.UNKNOWN

        type_map = {
            "bool": DataType.BOOL,
            "char": DataType.CHAR,
            "_Bool": DataType.BOOL,
            "signed": DataType.INT32,
            "unsigned": DataType.UINT32,
            "int": DataType.INT32,
            "short": DataType.INT16,
            "long": DataType.INT64,
            "float": DataType.FLOAT,
            "double": DataType.DOUBLE,
        }

        if base_type_str in type_map:
            data_type = type_map[base_type_str]
        elif "int8_t" in type_name:
            data_type = DataType.INT8
        elif "int16_t" in type_name:
            data_type = DataType.INT16
        elif "int32_t" in type_name:
            data_type = DataType.INT32
        elif "int64_t" in type_name:
            data_type = DataType.INT64
        elif "uint8_t" in type_name:
            data_type = DataType.UINT8
        elif "uint16_t" in type_name:
            data_type = DataType.UINT16
        elif "uint32_t" in type_name:
            data_type = DataType.UINT32
        elif "uint64_t" in type_name:
            data_type = DataType.UINT64
        elif "*" in type_name:
            data_type = DataType.POINTER
        elif type_name in self.known_structs:
            data_type = DataType.STRUCT
        else:
            data_type = DataType.ENUM

        if data_type == DataType.STRUCT:
            nested_info = self.parse_struct_definition(type_name)
            if nested_info:
                base_size = nested_info.size
                natural_align = nested_info.alignment
            else:
                base_size = 1
                natural_align = 1
        else:
            base_size = self.TYPE_SIZES.get(data_type, 4)
            natural_align = min(base_size, 8)  # cap at 8

        if is_array:
            total_elements = array_info.total_size
            size = base_size * total_elements
            alignment = natural_align
        else:
            size = base_size
            alignment = natural_align

        if current_offset % alignment != 0:
            current_offset += alignment - (current_offset % alignment)

        field = FieldInfo(
            name=field_name,
            type_name=type_name,
            data_type=data_type,
            offset=current_offset,
            size=size,
            is_array=is_array,
            array_info=array_info,
        )

        if data_type == DataType.STRUCT and type_name in self.known_structs:
            nested_info = self.parse_struct_definition(type_name)
            field.nested_struct = nested_info
            if nested_info:
                field.size = (
                    nested_info.size
                    if not is_array
                    else nested_info.size * array_info.total_size
                )
                alignment = nested_info.alignment

        new_max_align = max(max_alignment, alignment)

        return field, current_offset + size, new_max_align

    def old_parse_field(
        self, line: str, current_offset: int
    ) -> Tuple[Optional[FieldInfo], int]:
        """Parse a single field from struct definition"""
        line = line.strip().rstrip(";")
        if not line:
            return None, current_offset

        array_info = self.parse_array_dimensions(line)
        is_array = array_info is not None

        clean_line = re.sub(r"\[.*?\]", "", line)

        parts = clean_line.rsplit(None, 1)
        if len(parts) != 2:
            return None, current_offset

        type_name, field_name = parts

        data_type = self.parse_data_type(type_name)

        base_size = self.TYPE_SIZES.get(data_type, 4)
        if data_type == DataType.CHAR and is_array:
            size = array_info.total_size if array_info else base_size
        elif is_array:
            size = base_size * (array_info.total_size if array_info else 1)
        else:
            size = base_size

        alignment = min(base_size, 8)
        if current_offset % alignment != 0:
            current_offset += alignment - (current_offset % alignment)

        field = FieldInfo(
            name=field_name,
            type_name=type_name,
            data_type=data_type,
            offset=current_offset,
            size=size,
            is_array=is_array,
            array_info=array_info,
        )

        return field, current_offset + size

    def parse_struct_definition(self, struct_name: str) -> Optional[StructInfo]:
        if struct_name in self.structs_cache:
            return self.structs_cache[struct_name]

        if struct_name not in self.known_structs:
            return None

        struct_body = self.known_structs[struct_name]
        lines = struct_body.split("\n")

        fields = []
        current_offset = 0
        max_alignment = 1

        for line in lines:
            result = self.parse_field(line, current_offset, max_alignment)
            if len(result) == 3:
                field, current_offset, max_alignment = result
                if field:
                    fields.append(field)
            # else: skip comments/empty lines

        if current_offset % max_alignment != 0:
            current_offset += max_alignment - (current_offset % max_alignment)

        struct_info = StructInfo(
            name=struct_name,
            fields=fields,
            size=current_offset,
            alignment=max_alignment,
        )

        self.structs_cache[struct_name] = struct_info
        return struct_info

    def read_value(self, dump_data: bytes, field: FieldInfo, base_offset: int) -> Any:
        offset = base_offset + field.offset

        if field.data_type == DataType.STRUCT and field.nested_struct:
            if field.is_array and field.array_info:
                results = []
                struct_size = field.nested_struct.size
                for i in range(field.array_info.total_size):
                    elem_offset = offset + i * struct_size
                    results.append(
                        self.read_struct(dump_data, field.nested_struct, elem_offset)
                    )
                return results
            else:
                return self.read_struct(dump_data, field.nested_struct, offset)

        elif field.data_type == DataType.CHAR and field.is_array:
            data = dump_data[offset : offset + field.size]
            try:
                return data.split(b"\x00")[0].decode("utf-8", errors="replace")
            except:
                return "<binary data>"

        elif field.is_array and field.data_type in self.STRUCT_FORMATS:
            fmt_char = self.STRUCT_FORMATS[field.data_type]
            total = field.array_info.total_size if field.array_info else 1
            fmt = f"{total}{fmt_char}"
            try:
                values = struct.unpack_from(fmt, dump_data, offset)
                return list(values)
            except:
                return "<invalid array>"

        elif field.data_type in self.STRUCT_FORMATS:
            fmt = self.STRUCT_FORMATS[field.data_type]
            try:
                value = struct.unpack_from(fmt, dump_data, offset)[0]
                if field.data_type == DataType.BOOL:
                    return bool(value)
                return value
            except:
                return None

        else:
            return "<unknown>"

    def read_struct(
        self, dump_data: bytes, struct_info: StructInfo, offset: int
    ) -> Dict[str, Any]:
        """Read entire struct from dump"""
        result = {}
        for field in struct_info.fields:
            result[field.name] = self.read_value(dump_data, field, offset)
        return result

    def extract_values(
        self, dump_file: str, struct_name: str, offset: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Extract struct values from dump file"""
        struct_info = self.parse_struct_definition(struct_name)
        if not struct_info:
            print(f"Error: Could not find struct '{struct_name}' in definition file")
            return None

        with open(dump_file, "rb") as f:
            dump_data = f.read()

        if offset + struct_info.size > len(dump_data):
            print(
                f"Error: Offset {offset} + struct size {struct_info.size} exceeds dump size {len(dump_data)}"
            )
            return None

        return {
            "struct_name": struct_name,
            "struct_size": struct_info.size,
            "offset": offset,
            "values": self.read_struct(dump_data, struct_info, offset),
        }

    def scan_for_struct(
        self, dump_file: str, struct_name: str, pattern: Optional[bytes] = None
    ) -> List[Dict[str, Any]]:
        """Scan dump file for potential struct instances"""
        struct_info = self.parse_struct_definition(struct_name)
        if not struct_info:
            return []

        with open(dump_file, "rb") as f:
            dump_data = f.read()

        results = []

        if pattern:
            offset = 0
            while offset < len(dump_data):
                idx = dump_data.find(pattern, offset)
                if idx == -1:
                    break

                if idx + struct_info.size <= len(dump_data):
                    values = self.read_struct(dump_data, struct_info, idx)
                    results.append({"offset": idx, "values": values})

                offset = idx + 1
        else:
            for offset in range(
                0, len(dump_data) - struct_info.size + 1, struct_info.alignment
            ):
                values = self.read_struct(dump_data, struct_info, offset)

                if struct_info.fields:
                    first_field = struct_info.fields[0]
                    first_value = values.get(first_field.name)

                    if first_field.data_type == DataType.BOOL and first_value in [
                        True,
                        False,
                    ]:
                        results.append({"offset": offset, "values": values})
        print("hre")
        return results


def print_values(data: Dict[str, Any], indent: int = 0) -> None:
    """Pretty print extracted values"""
    prefix = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                print_values(value, indent + 1)
            elif isinstance(value, bool):
                print(f"{prefix}{key}: {str(value).lower()}")
            elif isinstance(value, (int, float)):
                if key.startswith("0x"):
                    print(f"{prefix}{key}: 0x{value:x}")
                else:
                    print(f"{prefix}{key}: {value}")
            else:
                print(f"{prefix}{key}: {value}")
    else:
        print(f"{prefix}{data}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract struct values from binary dumps"
    )
    parser.add_argument("dump_file", help="Binary dump file")
    parser.add_argument("struct_name", help="Name of struct to extract")
    parser.add_argument("definition_file", help="Header file with struct definitions")
    parser.add_argument(
        "-o",
        "--offset",
        type=lambda x: int(x, 0),
        default=0,
        help="Offset in dump file (default: 0, supports hex with 0x prefix)",
    )
    parser.add_argument(
        "-s",
        "--scan",
        action="store_true",
        help="Scan entire dump for struct instances",
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format"
    )
    parser.add_argument("-p", "--pattern", help="Search pattern (hex string)")

    args = parser.parse_args()

    parser_obj = StructParser(args.definition_file)

    if args.scan:
        pattern = bytes.fromhex(args.pattern) if args.pattern else None
        results = parser_obj.scan_for_struct(args.dump_file, args.struct_name, pattern)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Found {len(results)} potential instances of {args.struct_name}:")
            for i, result in enumerate(results):
                print(f"\nInstance {i+1} at offset 0x{result['offset']:x}:")
                print_values(result["values"], 1)
    else:
        result = parser_obj.extract_values(
            args.dump_file, args.struct_name, args.offset
        )

        if result:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(
                    f"Struct: {result['struct_name']} (size: {result['struct_size']} bytes)"
                )
                print(f"Offset: 0x{result['offset']:x}")
                print("=" * 50)
                print_values(result["values"])
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
