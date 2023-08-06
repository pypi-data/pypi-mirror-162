# Press the green button in the gutter to run the script.
import os
import pytest


from docparser.doc_parser_factory import DocParserFactory


class TestExcelDocumentParser:
    """
    测试Excel文档解析器
    """

    def test_text_block_parse(self):
        """
        测试文本块解析
        """

        file = os.getcwd() + '/tests/files/cma.xlsx';
        converter = DocParserFactory.create('excel', file, {
            "containers": {
                "type": "table",
                "extractor": "mixed",
                "max_rows": 1,
                "row_split_ref_col_name": "container_no",
                "col_split_chars": "  ",
                "rect": {
                    "top": {
                        "keyword": "CONTAINER  # ",
                        "include": True
                    },
                    "bottom": {
                        "keyword": "PLEASE NOTE :",
                    }
                },
                "columns": [
                    {
                        "name": "container_no",
                        "title": "CONTAINER #",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\w{0,20}",
                    }, {
                        "name": "seal_no",
                        "title": "SEAL #",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\w{0,20}",
                    }, {
                        "name": "container_size_type",
                        "title": "SIZE/TYPE #",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\d{1,10}\\s{1,2}\\[a-z|A-Z]{2,5}",
                    }, {
                        "name": "weight",
                        "title": "WEIGHT",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\d{0,10}",
                    }, {
                        "name": "measure",
                        "title": "MEASURE",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\w{0,5}",
                    }, {
                        "name": "free_business_last_free",
                        "title": "FREE BUSINESS LAST FREE",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "childrens": [
                            {
                                "name": "day_at_port",
                                "title": "DAYS AT PORT",
                                "title_h_align": "center",
                                "title_v_align": "middle",
                                "content_pattern": "\\w{0,20}",
                            },
                            {
                                "name": "day_at_ramp",
                                "title": "DAY AT RAMP",
                                "title_h_align": "center",
                                "title_v_align": "middle",
                                "content_pattern": "\\d{1,2}/\\d{1,2}/\\d{1,2}",
                            }
                        ]
                    }, {
                        "name": "pickup_no",
                        "title": "PICKUP #",
                        "title_h_align": "center",
                        "title_v_align": "middle",
                        "content_pattern": "\\w{0,20}",
                    },
                ]
            }
        })

        result = converter.parse()

        assert result.data is not None

    # def test_standard_table_block_parse(self):
    #     """
    #     测试标准表格解析
    #     """
    #
    #     converter = DocConverterFactory.create('pdf', 'txt')
    #     output_files = converter.bulk_convert([os.getcwd() + "\\files\\zim.pdf"], os.getcwd().replace("\\tests","") +r"\output")
    #
    #     assert len(output_files) == 1
    #
    # def test_mixed_table_block_parse(self):
    #     """
    #     测试混杂模式表格解析
    #     """
    #
    #     converter = DocConverterFactory.create('pdf', 'txt')
    #     output_files = converter.bulk_convert([os.getcwd() + "\\files\\zim.pdf"],
    #                                           os.getcwd().replace("\\tests", "") + r"\output")
    #
    #     assert len(output_files) == 1


if __name__ == '__main__':
    pytest.main("-q --html=report.html")
