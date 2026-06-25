from datetime import date

from vanilla_option_black_sholes import OptionType


class VanillaOptionVannaVolga:
    def __init__(self, T: date, K: float, option_type: OptionType) -> None:
        self.T = T
        self.K = K
        self.type = option_type
