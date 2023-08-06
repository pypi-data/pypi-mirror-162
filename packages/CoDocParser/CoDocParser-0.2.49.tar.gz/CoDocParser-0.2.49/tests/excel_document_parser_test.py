import os

import pytest
import traceback
from docparser.doc_parser_factory import DocParserFactory

config3 = {
    "id": "AN_hpl_",
    "parse": {
        "id": "hpl",
        "name": "hpl config",
        "kv": {
            "BILL": {
                "position_pattern": [
                    "(Carrier's\\s*Reference\\s*:\\s*)|(Ref\\.\\s*\\/\\s*Réf:)"
                ],
                "value_pattern": [
                    ".*?\n(?P<bill>[a-zA-Z]{4,}\\w{4,}\\d+)"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill",
                        "action_type": "append"
                    }
                ]
            },
            "bill2": {
                "position_pattern": [
                    "^ORIGINAL\\s*B/L"
                ],
                "value_pattern": [
                    "^ORIGINAL\\s*B/L\\s*(?P<bill>[a-zA-Z]{4,}\\d{4,})"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill",
                        "action_type": "append"
                    }
                ]
            },
            "bill1": {
                "position_pattern": [
                    "^SEA\\s*WAYBILL"
                ],
                "value_pattern": [
                    "(?P<bill>[a-zA-Z]{4,}\\d{4,}[a-zA-Z]{4,}\\d+)"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill",
                        "action_type": "append"
                    }
                ]
            },
            "bill3": {
                "position_pattern": [
                    "^ORIGINAL\\s*B/L"
                ],
                "value_pattern": [
                    "(?P<bill>[a-zA-Z]{4,}\\d{4,}[a-zA-Z]{4,}\\d+)"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill",
                        "action_type": "append"
                    }
                ]
            },
            "VESSEL": {
                "position_pattern": [
                    "^Ocean\\s*Vessel\\s*:\\s*"
                ],
                "value_pattern": [
                    "(?P<Vessel>.*)"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VesselName",
                        "key": "Vessel"
                    }
                ]
            },
            "VESSEL1": {
                "position_pattern": [
                    "^Voyage\\s*N°\\s*:\\s*"
                ],
                "value_pattern": [
                    "^Voyage\\s*N°\\s*:\\s*(?P<Vessel>[a-zA-Z0-9 ]*)"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VesselName",
                        "key": "Vessel"
                    }
                ]
            },
            "VESSEL2": {
                "position_pattern": [
                    "^Ocean\\s*Vessel\\s*:\\s*"
                ],
                "value_pattern": [
                    "^Ocean\\s*Vessel\\s*:\\s*(?P<Vessel>.*)(?!=$|\n)"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VesselName",
                        "key": "Vessel",
                        "action_type": "append"
                    }
                ]
            },
            "VESSEL3": {
                "position_pattern": [
                    "^Vessel\\s*/\\s*Navire\\s*:"
                ],
                "value_pattern": [
                    "(?P<Vessel>.*)"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VesselName",
                        "key": "Vessel",
                        "action_type": "append"
                    }
                ]
            },
            "VOYAGE1": {
                "position_pattern": [
                    "^Voyage\\s*No"
                ],
                "value_pattern": [
                    "(?P<VOYAGE>^\\w{4,}$)"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VoyageNo",
                        "key": "VOYAGE"
                    }
                ]
            },
            "VOYAGE2": {
                "position_pattern": [
                    "^Voyage\\s*No\\.\\/\\s*"
                ],
                "value_pattern": [
                    "^Voyage\\s*No\\.\\/\\s*(?P<VOYAGE>\\w{4})$"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VoyageNo",
                        "key": "VOYAGE"
                    }
                ]
            },
            "VOYAGE": {
                "position_pattern": [
                    "^Voyage\\s*No"
                ],
                "value_pattern": [
                    "^Voyage\\s*No\\.:\\s*(?P<VOYAGE>\\w{4})$"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VoyageNo",
                        "key": "VOYAGE"
                    }
                ]
            },
            "ETA": {
                "position_pattern": [
                    "[\\w\\W]*?Due\\s*to\\s*arrive\\s*"
                ],
                "value_pattern": [
                    "[\\w\\W]*?Due\\s*to\\s*arrive.*?\n(?P<eta>.*)(?!=$|\n)"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "EstimatedArrivalDate",
                        "key": "eta"
                    }
                ]
            },
            "ETA1": {
                "position_pattern": [
                    "[\\W\\w]*?Port\\s*of\\s*Discharge"
                ],

                "value_pattern": [
                    "[\\W\\w]*?\\s{4,}.*\\s{3,}(?P<eta>\\w{2,}[./]\\w{2}[./]\\d{4})"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "EstimatedArrivalDate",
                        "key": "eta",
                        "action_type": "append"
                    }
                ]
            },
            "DestinationPortName": {
                "position_pattern": [
                    "[\\W\\w]*?Port\\s*of\\s*Discharge[/:]"
                ],

                "value_pattern": [
                    "[\\W\\w]*?\\s{4,}(?P<DestinationPortName>.*)\\s{3,}\\w{2,}[./]\\w{2}[./]\\d{4}",
                    "[\\W\\w]*?\\s{4,}(?P<DestinationPortName>.*)(?!=$|\n)",
                    "[\\W\\w]*?(?P<DestinationPortName>.*)(?!=$|\n)"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DestinationPortName",
                        "key": "DestinationPortName"
                    }
                ]
            },
            "DestinationPortName1": {
                "position_pattern": [
                    "[\\W\\w]*?Port\\s*of\\s*Discharge\\s*:"
                ],

                "value_pattern": [
                    "[\\W\\w]*?Port\\s*of\\s*Discharge:[\\W\\w]*?\\s{4,}(?P<DestinationPortName>.*)(?!=$|\n)"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DestinationPortName",
                        "key": "DestinationPortName"
                    }
                ]
            },
            "DeliveryPlaceName": {
                "position_pattern": [
                    "[\\W\\w]*?Place\\s*of\\s*Delivery"
                ],
                "value_pattern": [
                    "[\\W\\w]*?Place\\s*of\\s*Delivery\\s*.*?\\s*\n(?P<DeliveryPlaceName>.*)(?!=$|\n)"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DeliveryPlaceName",
                        "key": "DeliveryPlaceName"
                    }
                ]
            },
        },
        "data_type_format": {
            "EstimatedArrivalDate": {
                "data_type": "time",
                "format": ["%d/%b/%Y", "%b/%d/%Y", "%b.%d.%Y"],
                "filter": ""
            },
            "BillOfLadingsId": {
                "data_type": "str",
                "filter": "(\\s)"
            }
        },
        "address_repair": {
            "db": {
                "pub": {
                    "user": "co",
                    "pwd": "Co&23@2332$22",
                    "server": "db.uat.com:1433",
                    "database": "CO_PUB"
                }
            },
            "repairs": [
                {
                    "key": "DeliveryPlaceName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DeliveryPlaceId",
                    "old_val_handle": "empty"
                },
                {
                    "key": "DestinationPortName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DestinationPortId",
                    "old_val_handle": "empty"
                }
            ]
        }
    }
}

# msc
config2 = {
    "id": "AN_MSC_",
    "parse": {
        "id": "MSC",
        "name": "MSC config",
        "kv": {
            "VESSEL": {
                "position_pattern": [
                    "VESSEL NAME"
                ],
                "value_pattern": [
                    "(?P<Vessel>.{2,})"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 1,
                "split_pattern": [
                    "(?P<s0>^|)(?P<now>VESSEL\\s*NAME)\\s*(?P<s2>VOYAGE\\s*No\\.)\\s*(?P<s3>Estimated\\s*Arrival\\s*Date)"
                ],
                "action": [
                    {
                        "keyword": "VesselName",
                        "key": "Vessel"
                    }
                ]
            },
            "VOYAGE": {
                "position_pattern": [
                    "\\s*VOYAGE"
                ],
                "value_pattern": [
                    "(?P<VOYAGE>.{2,})"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VoyageNo",
                        "key": "VOYAGE"
                    }
                ]
            },
            "ETA": {
                "position_pattern": [
                    "\\s*Estimated\\s*Arrival\\s*Date"
                ],
                "value_pattern": [
                    "(?P<eta>.{2,})"
                ],
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "EstimatedArrivalDate",
                        "key": "eta"
                    }
                ]
            },
            "BILL": {
                "position_pattern": [
                    "^FLAG\\s*REGISTRY"
                ],
                "value_pattern": [
                    "(?P<BILL>[a-z]{4,}\\d{6,})"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "BILL"
                    }
                ]
            },
            "DestinationPortName": {
                "position_pattern": [
                    "^PORT\\s*OF\\s*DISCHARGE"
                ],

                "value_pattern": [
                    "(?P<DestinationPortName>.*)"
                ],
                "read_orgin": {"val": "PORT\\s*OF\\s*DISCHARGE", "key": "DestinationPortName"},
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DestinationPortName",
                        "key": "DestinationPortName"
                    }
                ]
            },
            "DeliveryPlaceName": {
                "position_pattern": [
                    "^FINAL\\s*DESTINATION"
                ],

                "value_pattern": [
                    "(?P<DeliveryPlaceName>.*)"
                ],
                "read_orgin": {"val": "FINAL\\s*DESTINATION", "key": "DeliveryPlaceName"},
                "repeat_count": 1,
                "find_mode": "v",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DeliveryPlaceName",
                        "key": "DeliveryPlaceName"
                    }
                ]
            },
        },
        "table": {
            "containers": {
                "position_pattern": [
                    "(^CONTAINER\\s*NUMBER)|([a-zA-Z]{4,}\\d{7,}-\\d{2}[a-zA-Z]{2})"
                ],
                "separator": "\\n",

                "find_mode": "h",
                "separator_mode": "regex",
                "column": [
                    "ContainerNo",
                    "ContainerSize"
                ],
                "behaviors": [
                    {
                        "over_action": "row",
                        "loop": 1,
                        "value_pattern": [
                            '(?P<col_1>[a-zA-Z]{4,}\\d{7,})-(?P<col_2>\\d{2}[a-zA-Z]{2})'
                        ],
                        "action": []
                    }
                ]
            }
        },
        "data_type_format": {
            "VoyageNo": {
                "data_type": "str",
                "filter": "r([/\\s])"
            },
            "EstimatedArrivalDate": {
                "data_type": "time",
                "format": "%m/%d/%Y",
                "filter": ""
            },
            "BillOfLadingsId": {
                "data_type": "str",
                "filter": "(\\s)"
            }
        },
        "address_repair": {
            "db": {
                "pub": {
                    "user": "co",
                    "pwd": "Co&23@2332$22",
                    "server": "db.uat.com:1433",
                    "database": "CO_PUB"
                }
            },
            "repairs": [
                {
                    "key": "DeliveryPlaceName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DeliveryPlaceId",
                    "old_val_handle": "empty"
                },
                {
                    "key": "DestinationPortName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DestinationPortId",
                    "old_val_handle": "empty"
                }
            ]
        }
    }
}

# wanhai
config1 = {
    "id": "AN_WANHAI_",
    "parse": {
        "id": "WANHAI",
        "name": "WANHAI config",
        "kv": {
            "ETA": {
                "position_pattern": [
                    "[\\w\\W]*Est\\.\\s*Arrival\\s*Date\\s*:\\s*"
                ],
                "value_pattern": [
                    "[\\w\\W]*Est\\.\\s*Arrival\\s*Date\\s*:\\s*(?P<ETA>[a-zA-Z]*\\s*\\d{1,2}\\s*\\d{2,4})"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [],
                "action": [
                    {
                        "keyword": "EstimatedArrivalDate",
                        "key": "ETA"
                    }
                ]
            },
            "BILL": {
                "position_pattern": [
                    "[\\w\\W]*B/L\\s*No\\s*:",
                    "B/L\\s*No\\s*:\\s*"
                ],
                "value_pattern": [
                    "[\\w\\W]*B/L\\s*No\\s*:\\s*(?P<bill>[a-zA-Z]{4}[a-zA-Z0-9]{5}\\d{4,})",
                    "B/L\\s*No\\s*:\\s*(?P<bill>[a-zA-Z0-9]{5}\\d{4,})"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill"
                    }
                ]
            },
            "BILL2": {
                "position_pattern": [
                    "B/L\\s*No\\s*:\\s*"
                ],
                "value_pattern": [
                    "(?P<bill>[a-zA-Z0-9]{5}\\d{4,})"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill"
                    }
                ]
            },
            "VOYAGE": {
                "position_pattern": [
                    "[\\w\\W]*?Voyage\\s*No\\s*:\\s*"
                ],
                "value_pattern": [
                    "(?P<VOYAGE>.*)"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VoyageNo",
                        "key": "VOYAGE"
                    }
                ]
            },
            "Vessel": {
                "position_pattern": [
                    "[\\w\\W]*?Ocean\\s*Vessel\\s*:\\s*"
                ],
                "value_pattern": [
                    "(?P<Vessel>.*)"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "VesselName",
                        "key": "Vessel"
                    }
                ]
            },
            "DestinationPortName": {
                "position_pattern": [
                    "Place\\s*of\\s*receipt\\s*:\\s*"
                ],

                "value_pattern": [
                    "(?P<DestinationPortName>[^\\n]*?)(\\n|$)"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DestinationPortName",
                        "key": "DestinationPortName"
                    }
                ]
            },
            "DeliveryPlaceName": {
                "position_pattern": [
                    "[\\w\\W]*?Place\\s*of\\s*delivery\\s*:\\s*"
                ],

                "value_pattern": [
                    ".*?\\n{1}(?P<DeliveryPlaceName>.*)$"
                ],
                "repeat_count": 1,
                "find_mode": "h",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [""],
                "action": [
                    {
                        "keyword": "DeliveryPlaceName",
                        "key": "DeliveryPlaceName"
                    }
                ]
            },
        },
        "table": {
            "containers": {
                "position_pattern": [
                    "[\\w\\W]*?([a-zA-Z]{4}\\d{7})\\s*\\d+[a-zA-Z]+\\d+\\s*[a-zA-Z]+\\d{6,}"
                ],
                "separator": "\\n",
                "find_mode": "h",
                "separator_mode": "regex",
                "column": [
                    "ContainerNo"
                ],
                "behaviors": [
                    {
                        "over_action": "row",
                        "loop": 1,
                        "value_pattern": [
                            '(?P<col_1>[a-zA-Z]{4}\\d{7})'
                        ],
                        "action": []
                    }
                ]
            }
        },
        "data_type_format": {
            "EstimatedArrivalDate": {
                "data_type": "time",
                "format": "%b  %d  %Y",
                "filter": ""
            },
        },
        "address_repair": {
            "db": {
                "pub": {
                    "user": "co",
                    "pwd": "Co&23@2332$22",
                    "server": "db.uat.com:1433",
                    "database": "CO_PUB"
                }
            },
            "repairs": [
                {
                    "key": "DeliveryPlaceName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DeliveryPlaceId",
                    "old_val_handle": "empty"
                },
                {
                    "key": "DestinationPortName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DestinationPortId",
                    "old_val_handle": "empty"
                }
            ]
        }
    }
}

config = {
    "id": "AN_COSCO_",
    "parse": {
        "id": "COSCO",
        "name": "COSCO config",
        "kv": {
            "BILL": {
                "position_pattern": [
                    "[\\w\\W]*?B/L\\s*Number\\s*:"
                ],
                "value_pattern": [
                    "[\\w\\W]*?B/L\\s*Number\\s*:(\\s*|\n)\\s*(?P<bill>[a-zA-Z]{4,}\\d{6,})"
                ],
                "repeat_count": 1,
                "find_mode": "default",
                "separator_mode": "regex",
                "is_split_cell": 0,
                "split_pattern": [
                    ""
                ],
                "action": [
                    {
                        "keyword": "BillOfLadingsId",
                        "key": "bill"
                    }
                ]
            },
            # "VESSEL": {
            #     "position_pattern": [
            #         "[\\W\\w]*?B/L\\s*Vessel/Voyage\\s*:"
            #     ],
            #     "value_pattern": [
            #         "[\\W\\w]*?B/L\\s*Vessel/Voyage\\s*:(\\s*|\\n)(?P<Vessel>.*)\\s+(?P<VOYAGE>\\w+)\\n"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "default",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "VesselName",
            #             "key": "Vessel"
            #         },
            #         {
            #             "keyword": "VoyageNo",
            #             "key": "VOYAGE"
            #         }
            #     ]
            # },
            # "PORT OF DISCHARGE": {
            #     "position_pattern": [
            #         "PORT\\s*OF\\s*DISCHARGE"
            #     ],
            #     "value_pattern": [
            #         "(?P<DISCHARGE>.*)"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "v",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "DestinationPortName",
            #             "key": "DISCHARGE"
            #         }
            #     ]
            # },
            # "PORT OF DISCHARGE1": {
            #     "position_pattern": [
            #         "PORT\\s*OF\\s*DISCHARGE"
            #     ],
            #     "value_pattern": [
            #         "PORT\\s*OF\\s*DISCHARGE\\s*\n(?P<DISCHARGE>.*)"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "default",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "DestinationPortName",
            #             "key": "DISCHARGE"
            #         }
            #     ]
            # },
            # "PLACE OF DELIVERY": {
            #     "position_pattern": [
            #         "PLACE\\s*OF\\s*DELIVERY"
            #     ],
            #     "value_pattern": [
            #         "(?P<DELIVERY>.*)"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "v",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "DeliveryPlaceName",
            #             "key": "DELIVERY"
            #         }
            #     ]
            # },
            # "PORT OF DELIVERY1": {
            #     "position_pattern": [
            #         "PLACE\\s*OF\\s*DELIVERY"
            #     ],
            #     "value_pattern": [
            #         "PLACE\\s*OF\\s*DELIVERY\\s*\n(?P<DELIVERY>.*)"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "default",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "DeliveryPlaceName",
            #             "key": "DELIVERY"
            #         }
            #     ]
            # },
            # "ETA": {
            #     "position_pattern": [
            #         "ESTIMATE\\s*ARRIVAL\\s*AT\\s*POD"
            #     ],
            #     "value_pattern": [
            #         "ESTIMATE\\s*ARRIVAL\\s*AT\\s*POD\\s*:\\s*(?P<DestinationPortName>.*)(\\s*|\n)(?P<eta>[a-zA-Z]+\\s*,\\s*\\d{2}\\s*[a-zA-Z]{2,3},\\s*\\d{4}\\s*\\d{1,2}:\\d{1,2}\\s*(AM|PM))"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "default",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "EstimatedArrivalDate",
            #             "key": "eta"
            #         },
            #         {
            #             "keyword": "DestinationPortName",
            #             "key": "DestinationPortName"
            #         }
            #     ]
            # },
            # "DELIVERY_ETA": {
            #     "position_pattern": [
            #         "EST\\s*CARGO\\s*AVAILABLE\\s*AT"
            #     ],
            #     "value_pattern": [
            #         "EST\\s*CARGO\\s*AVAILABLE\\s*AT\\s*:\\s*(?P<DeliveryPlaceName>.*)(\\s*|\n)(?P<eta>[a-zA-Z]+\\s*,\\s*\\d{2}\\s*[a-zA-Z]{2,3},\\s*\\d{4}\\s*\\d{1,2}:\\d{1,2}\\s*(AM|PM))"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "default",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "DeliveryEstimatedArrivalDate",
            #             "key": "eta"
            #         },
            #         {
            #             "keyword": "DeliveryPlaceName",
            #             "key": "DeliveryPlaceName"
            #         }
            #     ]
            # },
            # "ETA1": {
            #     "position_pattern": [
            #         "ON:\\s*[a-zA-Z]+\\s*,\\s*\\d{2}"
            #     ],
            #     "value_pattern": [
            #         "ON:\\s*(?P<eta>[a-zA-Z]+\\s*,\\s*\\d{2}\\s*[a-zA-Z]{2,3},\\s*\\d{4}\\s*\\d{1,2}:\\d{1,2}\\s*(AM|PM))"
            #     ],
            #     "repeat_count": 1,
            #     "find_mode": "default",
            #     "separator_mode": "regex",
            #     "is_split_cell": 0,
            #     "split_pattern": [
            #         ""
            #     ],
            #     "action": [
            #         {
            #             "keyword": "EstimatedArrivalDate",
            #             "key": "eta"
            #         }
            #     ]
            # },
        },
        "data_type_format": {
            "DeliveryEstimatedArrivalDate": {
                "data_type": "time",
                "format": "%A, %d %b, %Y %I:%M %p",
                "filter": ""
            },
            "EstimatedArrivalDate": {
                "data_type": "time",
                "format": "%A, %d %b, %Y %I:%M %p",
                "filter": ""
            },
            "BillOfLadingsId": {
                "data_type": "str",
                "filter": "(\\s)"
            }
        },
        "address_repair": {
            "db": {
                "pub": {
                    "user": "co",
                    "pwd": "Co&23@2332$22",
                    "server": "db.uat.com:1433",
                    "database": "CO_PUB"
                }
            },
            "repairs": [
                {
                    "key": "DeliveryPlaceName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DeliveryPlaceId",
                    "old_val_handle": "empty"
                },
                {
                    "key": "DestinationPortName",
                    "db_key": "pub",
                    "sql": "SELECT  [FullName],[LocalName],[name],[code],[Id] from Places WHERE IsDeleted = 0 and IsOcean = 1 and IsValid = 1 and ([FullName] like '%${value}%' or charindex([FullName],'${value}')> 0) ;",
                    "column": [
                        0,
                        1,
                        2,
                        3
                    ],
                    "value": 4,
                    "mapping": "DestinationPortId",
                    "old_val_handle": "empty"
                }
            ]
        }
    }
}


class TestExcelDocumentParser:

    def test_excel_file_parse(self):
        """
        单文件测试
        :return:
        """
        factory = DocParserFactory.create("excel2",
                                          r"C:\Users\APing\Desktop\temp\msc\arrival-notice-for-bl-meduia298229-on-msc-lucy-219a.xlsx",
                                          config2['parse'])
        result, errors = factory.parse()

        print(result, errors)

    # def test_excel_file_parse_more(self):
    #     dir_path = r'C:\Users\APing\Desktop\temp\cosco'
    #     files = os.listdir(dir_path)
    #     succ_list = []
    #     for f in files:
    #         if f.endswith('.xlsx') and '~$' not in f:
    #             try:
    #                 factory = DocParserFactory.create("excel2", os.path.join(dir_path, f), config['parse'])
    #                 result, errors = factory.parse()
    #                 if (len(result) > 0 and len([v for k,v in result[0].items() if v=='']) > 0) or len(result) == 0 or len(result[0]) == 0:
    #                     print(f'{f}:{result}')
    #                 elif len(result) > 0:
    #                     succ_list.append(f'{f}:{result[0]}')
    #             except Exception as e:
    #                 print(f'{f}:{e}{traceback.format_exc()}')
    #                 return
    #     print("===================================================")
    #     for item in succ_list:
    #         print(item)


if __name__ == '__main__':
    pytest.main("-q --html=report.html")
