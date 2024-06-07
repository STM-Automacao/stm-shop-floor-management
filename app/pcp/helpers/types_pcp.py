"""
Módulo para tipos do PCP
"""

MASSADA_CHEIA = 153
MASSADA_REPROCESSO = 114.75
MASSADA_BOLINHA = 77
RENDIMENTO_CHEIA = 2240
RENDIMENTO_REPROCESSO = 1680
RENDIMENTO_BOLINHA = 4000

PAO_POR_BANDEJA = {
    "PAO ALHO TRD 10B/400GR": 5,
    "PAO ALHO PIC 10B/400GR": 5,
    "PAO CEBOLA 10B/400GR": 5,
    "PAO ALHO TRD 10B/240GR": 3,
    "PAO ALHO PIC 10B/240GR": 3,
    "PAO ALHO SWIFT TRD 10B/400GR": 5,
    "PAO ALHO SWIFT PIC 10B/400GR": 5,
    "PAO DOCE LEITE 10B/300GR SWIFT": 3,
    "PAO ALHO BOL TRD 10B/300GR": 12,
    "PAO DOCE BOLINHA 10B/300GR": 12,
    "PAO CEBOLA BOL 10B/300GR": 12,
}

GRID_NUMBER_COLS = {
    "filter": "agNumberColumnFilter",
    "cellClass": "center-aligned-cell",
    "cellDataType": "number",
    "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": "true"},
    "headerClass": "center-aligned-header",
}

GRID_STR_NUM_COLS = {
    "filter": "agNumberColumnFilter",
    "cellClass": "center-aligned-cell",
    "cellDataType": "string",
    "filterParams": {"buttons": ["apply", "reset"], "closeOnApply": "true"},
    "headerClass": "center-aligned-header",
}
