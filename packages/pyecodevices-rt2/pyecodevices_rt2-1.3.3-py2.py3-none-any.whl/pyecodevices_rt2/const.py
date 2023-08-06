PRODUCT_ENTRY = "product"
PRODUCT_VALUE = "EcoDevices_RT"

INDEX_GET_LINK = "Index=All"
RESPONSE_ENTRY = "status"
RESPONSE_SUCCESS_VALUE = "Success"

RT2_API_GET_LINK_CACHED = {
    "Get=D": {},
    "Get=R": {},
    "Get=S": {},
    "Get=VO": {},
    "Get=FP": {},
    "Get=XENO": {},
    "Get=XTHL": {},
    "Index=All": {},
    "Index=S": {},
    "DIndex=S": {},
    "Price=S": {},
    "DPrice=S": {},
    "Price=E": {},
    "Price=all": {},
}


RT2_API = {
    "counter": {
        "value": {
            "get": {"link": "Index=All", "entry": "Index_C%d"},
            "set": {"link": "SetC%02d=%s"},
        },
        "price": {"get": {"link": "Price=all", "entry": "Price_C%d"}},
    },
    "digitalinput": {"status": {"get": {"link": "Get=D", "entry": "D%d"}}},
    "enocean_sensor": {"value": {"get": {"link": "Get=XENO", "entry": "ENO ANALOG%d"}}},
    "enocean_switch": {
        "value": {
            "get": {"link": "Get=XENO", "entry": "ENO ACTIONNEUR%d"},
            "set": {
                "link_on": "SetEnoPC=%d",
                "link_off": "ClearEnoPC=%d",
                "link_toggle": "ToggleEnoPC=%d",
            },
        }
    },
    "post": {
        "instant": {"get": {"link": "Get=S", "entry": "INSTANT_POSTE%d%s"}},
        "index": {"get": {"link": "Index=S", "entry": "INDEX_POSTE%d%s"}},
        "index_day": {"get": {"link": "DIndex=S", "entry": "DAY_INDEX_POSTE%d%s"}},
        "price": {"get": {"link": "Price=S", "entry": "PRICE_POSTE%d%s"}},
        "price_day": {"get": {"link": "DPrice=S", "entry": "DAY_PRICE_POSTE%d%s"}},
    },
    "subpost": {
        "instant": {"get": {"link": "Get=S", "entry": "P%d_SSP%d"}},
        "index": {"get": {"link": "Index=S", "entry": "P%d_SSP%d"}},
        "index_day": {"get": {"link": "DIndex=S", "entry": "P%d_SSP%d"}},
        "price": {"get": {"link": "Price=S", "entry": "P%d_SSP%d"}},
        "price_day": {"get": {"link": "DPrice=S", "entry": "P%d_SSP%d"}},
    },
    "relay": {
        "value": {
            "get": {"link": "Get=R", "entry": "R%d"},
            "set": {
                "link_on": "SetR=%02d",
                "link_off": "ClearR=%02d",
                "link_toggle": "ToggleR=%02d",
            },
        }
    },
    "supplierindex": {
        "index": {"get": {"link": "Index=All", "entry": "Index_TI%d"}},
        "price": {"get": {"link": "Price=E", "entry": "Price_TI%d"}},
    },
    "toroid": {
        "index": {"get": {"link": "Index=All", "entry": "Index_TORE%d"}},
        "price": {"get": {"link": "Price=all", "entry": "Price_TORE%d"}},
    },
    "virtualoutput": {
        "value": {
            "get": {"link": "Get=VO", "entry": "VO%d"},
            "set": {
                "link_on": "SetVO=%03d",
                "link_off": "ClearVO=%03d",
                "link_toggle": "ToggleVO=%03d",
            },
        }
    },
    "x4fp": {
        "value": {
            "get": {
                "link": "Get=FP",
                "entry": "FP%d Zone %d",
                "convert": {
                    0: -1,
                    "Confort": 0,
                    "Eco": 1,
                    "Hors Gel": 2,
                    "Arret": 3,
                    "Confort -1": 4,
                    "Confort -2": 5,
                },
            },
            "set": {"link": "SetFP%02d=%d"},
        }
    },
    "xthl": {
        "temperature": {"get": {"link": "Get=XTHL", "entry": "THL%d-TEMP"}},
        "humidity": {"get": {"link": "Get=XTHL", "entry": "THL%d-HUM"}},
        "luminosity": {"get": {"link": "Get=XTHL", "entry": "THL%d-LUM"}},
    },
}
