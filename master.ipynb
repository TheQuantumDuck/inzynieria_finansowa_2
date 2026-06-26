import pandas as pd
import numpy as np
from .dates import year_fraction
from .import_data import load_market, MarketEngine
from .vanilla_option import OptionType, VanillaOptionBlackSholes, d
from .binary_option import CoNBlackScholes, AoNBlackScholes
# from .digital_option import

file = "market_data.xlsx"
tenor= "3M"


#idea jest taka, że wypisuje ceny danego typu opcji np. AoN dla danego tenoru, następnie porównuje je z wycenami BS z sigmaATM
#product type określa czy mamy vanilla, con, aon, one touch up/down ect
class ProductType(IntEnum):
    Vanilla = 1
    CoN = 2
    AoN = 3
  
def price_options(file: str, tenor: str, imply_PLN:bool, option_type: OptionType, product_type:):
    market = load_market(file, tenor)
    m_engine = MarketEngine(market)
