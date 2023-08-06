"""This module defines the Document object,
which includes the input and output fields for the model,
as well as the OCR data and page images of the document"""
import copy
import itertools
import logging
import os
from collections import OrderedDict
from typing import Dict, List, Tuple, Any, Optional

import fitz
from cloudstorageio import CloudInterface
from fitz.utils import getColor, getColorList

from pycognaize.common.enums import IqDocumentKeysEnum
from pycognaize.document.field import FieldMapping
from pycognaize.document.field.field import Field
from pycognaize.document.page import Page
from pycognaize.document.tag import TableTag
from pycognaize.document.tag.cell import Cell
from pycognaize.document.tag.tag import Tag


class Document:
    """Definition of input and output for a single document,
     depending on a given model"""

    def __init__(self,
                 input_fields: 'OrderedDict[str, List[Field]]',
                 output_fields: 'OrderedDict[str, List[Field]]',
                 pages: Dict[int, Page],
                 metadata: Dict[str, Any]):
        self._metadata = metadata
        self._pages: Dict[int, Page] = pages
        self._x: OrderedDict[str, List[Field]] = input_fields
        self._y: OrderedDict[str, List[Field]] = output_fields

    @property
    def x(self) -> 'OrderedDict[str, List[Field]]':
        """Returns a dictionary, where keys are input field names
        and values are list of Field objects"""
        return self._x

    @property
    def y(self) -> 'OrderedDict[str, List[Field]]':
        """Returns a dictionary, where keys are output field names
        and values are list of Field objects"""
        return self._y

    @property
    def metadata(self) -> Dict[str, Any]:
        """Returns document metadata"""
        return self._metadata

    @property
    def id(self) -> str:
        """Returns the pycognaize id of the document"""
        return self.metadata['document_id']

    @property
    def document_src(self):
        """Returns the source of the document"""
        return self.metadata['src']

    @property
    def pages(self) -> Dict[int, Page]:
        """Returns a dictionary, where each key is the page number
        and values are Page objects"""
        return self._pages

    @staticmethod
    def get_matching_table_cells_for_tag(
            tag: Tag,
            table_tags: List[TableTag],
            one_to_one: bool
    ) -> List[Tuple[Tag, TableTag, Cell, float]]:
        """Create a list which includes the original extraction tag,
           the corresponding table tag and Cell objects
           and the IOU of the intersection

        :param tag: The `tag` for which matching
            table and cells should be found
        :param table_tags: List of `table_tag`s
        :param one_to_one: If true,
            for each tag only one corresponding cell will be returned
        :return: List of tuples,
            which include the original extraction tag,
            the corresponding table tag and Cell objects
            and the IOU of the intersection
        """
        intersection = []
        if isinstance(tag, TableTag):
            return []
        for ttag in table_tags:
            if ttag.page.page_number != tag.page.page_number:
                continue
            for cell in ttag.cells.values():
                temp_cell = copy.deepcopy(cell)
                temp_cell.page = ttag.page
                iou = tag.iou(temp_cell)
                if iou <= 0:
                    continue
                if one_to_one:
                    if (not intersection or (
                            intersection and intersection[0][-1] < iou
                    )):
                        intersection = [(tag, ttag, cell, iou)]
                else:
                    intersection.append((tag, ttag, cell, iou))
        return intersection

    def get_table_cell_overlap(
            self, source_field: str,
            one_to_one: bool) -> List[Tuple[Tag, TableTag, Cell, float]]:
        """Create a list which includes the original extraction tag,
           the corresponding table tag and Cell objects
           and the IOU of the intersection

        :param source_field: Name of the field,
            for which to return the corresponding table cells
        :param one_to_one: If true,
            for each tag only one corresponding cell will be returned
        :return: List of tuples,
            which include the original extraction tag,
            the corresponding table tag and Cell objects
            and the IOU of the intersection
        """
        # noinspection PyUnresolvedReferences
        table_tags = [
            tag
            for fields in itertools.chain(self.x.values(), self.y.values())
            for field in fields
            for tag in field.tags
            if isinstance(tag, TableTag)
        ]
        res = []
        if source_field in self.x:
            fields = self.x[source_field]
        elif source_field in self.y:
            fields = self.y[source_field]
        else:
            return []
        for field in fields:
            for tag in field.tags:
                intersection = self.get_matching_table_cells_for_tag(
                    tag=tag, table_tags=table_tags, one_to_one=one_to_one)
                res.extend(intersection)
        return res

    def to_dict(self) -> dict:
        """Converts Document object to dict"""
        input_fields = OrderedDict(
            {name: [field.to_dict() for field in fields]
             for name, fields in self.x.items()})
        output_fields = OrderedDict(
            {name: [field.to_dict() for field in fields]
             for name, fields in self.y.items()})
        data = OrderedDict(input_fields=input_fields,
                           output_fields=output_fields,
                           metadata=self.metadata)
        return data

    @classmethod
    def from_dict(cls, raw: dict, data_path: str) -> 'Document':
        """Document object created from data of dict
        :param raw: document dictionary
        :param data_path: path to the documents OCR and page images
        """
        if not isinstance(raw, dict):
            raise TypeError(
                f"Expected dict for 'raw' argument got {type(raw)} instead")
        metadata = raw['metadata']
        pages = OrderedDict({page_n: Page(page_number=page_n,
                                          document_id=metadata['document_id'],
                                          path=data_path)
                             for page_n in range(
                1, metadata['numberOfPages'] + 1)})
        input_fields = OrderedDict(
            {name: [
                FieldMapping[
                    field[IqDocumentKeysEnum.data_type.value]
                ].value.construct_from_raw(raw=field, pages=pages)
                for field in fields]
             for name, fields in raw['input_fields'].items()})
        output_fields = OrderedDict(
            {name: [
                FieldMapping[
                    field[IqDocumentKeysEnum.data_type.value]
                ].value.construct_from_raw(raw=field, pages=pages)
                for field in fields]
             for name, fields in raw['output_fields'].items()})
        return cls(input_fields=input_fields, output_fields=output_fields,
                   pages=pages, metadata=metadata)

    def _collect_all_tags_for_fields(self,
                                     field_names: List[str],
                                     is_input_field: bool = True) -> List[Tag]:
        """Collect all tags of given field names from either input or output
            fields

        :param field_names: List of strings representing the field names
        :param is_input_field: If true, collect tags from input fields,
            otherwise collect tags from output fields
        :return: List of tags from the specified fields
        """
        all_tags = []
        if is_input_field:
            field_dict = self.x
            field_type = 'input field'
        else:
            field_dict = self.y
            field_type = 'output field'
        if field_names is not None:
            for field_name in field_names:
                if field_name not in field_dict.keys():
                    raise ValueError(f'Invalid {field_type} {field_name}')
                for field in field_dict.get(field_name, []):
                    for tag in field.tags:
                        all_tags.append(tag)
        return all_tags

    def to_pdf(self,
               input_fields: Optional[List[str]] = None,
               output_fields: Optional[List[str]] = None,
               input_color: str = 'deeppink1',
               output_color: str = 'deepskyblue3',
               input_opacity: float = 0.2,
               output_opacity: float = 0.3) -> bytes:

        """
        Adds tags of input_fields and output_fields to the bytes object
        representing the pdf file of the document.

        :param input_fields: Input fields
        :param output_fields: Output fields
        :param input_color: The color of the annotation rectangle
            of the input field
        :param output_color: The color of the annotation rectangle
            of the output field
        :param input_opacity: The opacity of the annotation rectangle
            of the input field
        :param output_opacity: The opacity of the annotation rectangle
            of the output field
        :return: bytes object of the pdf
        """

        ci = CloudInterface()
        pdf_path = os.path.join(self.pages[1].path, self.document_src) + '.pdf'

        with ci.open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        doc_fitz = fitz.open('pdf', pdf_bytes)

        if input_fields is not None:
            input_tags = self._collect_all_tags_for_fields(
                field_names=input_fields, is_input_field=True)
            for tag in input_tags:
                pdf_bytes = annotate_pdf(
                    doc=doc_fitz,
                    tag=tag,
                    color=input_color,
                    opacity=input_opacity)
        if output_fields is not None:
            input_tags = self._collect_all_tags_for_fields(
                field_names=output_fields, is_input_field=False)
            for tag in input_tags:
                pdf_bytes = annotate_pdf(
                    doc=doc_fitz,
                    tag=tag,
                    color=output_color,
                    opacity=output_opacity)
        return pdf_bytes


def annotate_pdf(doc: fitz.Document,
                 tag: Tag,
                 color: str,
                 opacity: float = 0.3) -> bytes:
    """An annotated Document pdf in bytes"""
    page = doc[tag.page.page_number-1]
    x0 = tag.left * page.MediaBox.width / 100
    y0 = tag.top * page.MediaBox.height / 100
    x1 = tag.right * page.MediaBox.width / 100
    y1 = tag.bottom * page.MediaBox.height / 100
    annot_rect = fitz.Rect(x0, y0, x1, y1)
    if color.upper() not in getColorList():
        raise ValueError(f'Wrong color {color}')
    if opacity < 0 or opacity > 1:
        raise ValueError(f'Wrong opacity value {opacity}')
    color_dict = {"stroke": getColor(color), "fill": getColor(color)}
    annot = page.add_rect_annot(annot_rect)
    annot.set_colors(color_dict)
    annot.set_opacity(opacity)
    annot.update()
    return doc.write()


def filter_out_invalid_tables(tables):
    valid_tables = []
    for table in tables:
        if not table.tags:
            logging.warning('removing table with no tags')
            continue

        valid_tables.append(table)
    return valid_tables


def assign_indices_to_tables(tables: List['Field']):
    tables_dict = {}
    valid_tables = filter_out_invalid_tables(tables)
    tables = sorted(valid_tables, key=lambda x: (
        x.tags[0].page.page_number, x.tags[0].top, x.tags[0].left))

    for table in tables:
        page_number = table.tags[0].page.page_number
        try:
            # find all tables in the current page
            # and get the index for next table
            table_last_index = [
                current_index
                for (table_page_number, current_index) in tables_dict.keys()
                if page_number == table_page_number
            ][-1] + 1
        except IndexError:
            table_last_index = 0
        tables_dict[(page_number, table_last_index)] = table
    return tables_dict
