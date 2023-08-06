# -*- coding: utf-8 -*-
from docparser.core.table_virtual_block import TableVirtualBlock


class CmaAnTableVirtualBlock(TableVirtualBlock):
    """
    CMA到港通知书表格扩展实现
    """

    def __init__(self, sheet, block_config):
        self.virtual_table = None
        cma_config = {
            # VESSEL:CMA CGM LYRA
            "vessel": {"keyword": "VESSEL"},
            # VOYAGE:  0TX92W1MA
            "voyage": {"keyword": "VOYAGE"},
            # POD ETA:  07/15/2021
            "podeta": {"keyword": "POD ETA"},
            # OPERATIONAL DISCH.PORT: LOS ANGELES, CA
            "dischport": {"keyword": "OPERATIONAL DISCH.PORT"},
            # PLACE OF RECEIPT:
            "placeofreceipt": {"keyword": "PLACE OF RECEIPT"},
            # FPD ETA:
            "fpdeta": {"keyword": "FPD ETA"},
            # OPERATIONAL LOAD PORT: XIAMEN
            "operationalloadport": {"keyword": "OPERATIONAL LOAD PORT"},
            # PLACE OF DELIVERY:
            "placeofdelivery": {"keyword": "PLACE OF DELIVERY"},
            # DEST.CARG MODE: Port
            "dest.cargmode": {"keyword": "DEST.CARG MODE"},
            # DESTINATION: LOS ANGELES, CA
            "destination": {"keyword": "DESTINATION"},
            # IT NUMBER: Local Clear
            "itnumber": {"keyword": "IT NUMBER"},
            # PLACE OF ISSUE: LOS ANGELES, CA
            "placeofissue": {"keyword": "PLACE OF ISSUE"},
            # IT ISSUED DATE:
            "itissueddate": {"keyword": "IT ISSUED DATE"},
            # LOAD PICKUP POOL ADDRESS: FENIX MARINE TERMINAL
            "loadpickuppooladdress": {"keyword": "LOAD PICKUP POOL ADDRESS"},
            # CLEARANCE POINT:   LOS ANGELES, CA
            "clearancepoint": {"keyword": "CLEARANCE POINT"},
            # FIRMS CODE:    Y257
            "firmscode": {"keyword": "FIRMS CODE"},
            # EMPTY RETURN DEPOT: Please Check   https://apps.usa.cma-cgm.com/econtainer/ daily
            "emptyreturndepot": {"keyword": "EMPTY RETURN DEPOT"},
            # RELEASE DATE:    07/23/2021
            "releasedate": {"keyword": "RELEASE DATE"},
            # PAYMENT RECEIVED:    NO
            "paymentreceived": {"keyword": "PAYMENT RECEIVED"},
            # OBL RECEIVED:YES
            "oblreceived": {"keyword": "OBL RECEIVED"},
            # SCAC:CMDU
            "scac": {"keyword": "SCAC"},
            # B/L#:XIA0707492
            "billno": {"keyword": "B/L#"},
            # BILL TYPE:Waybill
            "billtype": {"keyword": "BILL TYPE"},
            "containers": {
                # CONTAINER# : TRHU7122680
                "containerno": {"keyword": "CONTAINER#"},
                # SEAL#:  C0135997
                "sealno": {"keyword": "SEAL#"},
                # SIZE/TYPE: 40HC
                "size": {"keyword": "SIZE/TYPE"},
                # PIECE QTY&TYPE: 1060 CARTONS
                "qty": {"keyword": "PIECE QTY&TYPE"},
                # WEIGHT: 15909 LBS
                "weight": {"keyword": "WEIGHT"},
                # MEASURE:2398.00 FTQ
                "measure": {"keyword": "MEASURE"},
                # FREE BUSINESS DAYS AT PORT:
                "freebusinessdaysatport": {"keyword": "FREE BUSINESS DAYS AT PORT"},
                # LAST FREE DAY AT RAMP:
                "lastfreedayatramp": {"keyword": "LAST FREE DAY AT RAMP"},
                # PICKUP#:
                "pickupno": {"keyword": "PICKUP#"}
            }
        }
