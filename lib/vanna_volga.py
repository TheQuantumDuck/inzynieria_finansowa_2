from datetime import date

from _typeshed import ProfileFunction
from vanilla_option_black_sholes import (
    OptionType,
    VanillaOptionBlackSholes,
    strike_for_delta,
)


def vanna_volga_costs(
    df_d: float,
    df_f: float,
    S_t: float,
    sigma_atm: float,
    sigma_25C: float,
    sigma_25P: float,
    t: date,
    T: date,
    delta_forward: bool,
    delta_premium: bool,
    base: int,
):
    F_t = (df_f / df_d) * S_t
    K_25C = strike_for_delta(
        delta=0.25,
        option_type=OptionType.CALL,
        df_d=df_d,
        df_f=df_f,
        S_t=S_t,
        sigma=sigma_25C,
        t=t,
        T=T,
        forward=delta_forward,
        premium=delta_premium,
        base=base,
    )
    K_25P = strike_for_delta(
        delta=0.25,
        option_type=OptionType.PUT,
        df_d=df_d,
        df_f=df_f,
        S_t=S_t,
        sigma=sigma_25P,
        t=t,
        T=T,
        forward=delta_forward,
        premium=delta_premium,
        base=base,
    )
    call = VanillaOptionBlackSholes(T=T, K=K_25C, option_type=OptionType.CALL)
    put = VanillaOptionBlackSholes(T=T, K=K_25P, option_type=OptionType.PUT)
    C_25 = call.price(
        df_d=df_d,
        df_f=df_f,
        S_t=S_t,
        sigma=sigma_25C,
        t=t,
        base=base,
    )
    C_atm = call.price(
        df_d=df_d,
        df_f=df_f,
        S_t=S_t,
        sigma=sigma_atm,
        t=t,
        base=base,
    )
    P_25 = put.price(
        df_d=df_d,
        df_f=df_f,
        S_t=S_t,
        sigma=sigma_25P,
        t=t,
        base=base,
    )
    P_atm = call.price(
        df_d=df_d,
        df_f=df_f,
        S_t=S_t,
        sigma=sigma_atm,
        t=t,
        base=base,
    )
    vanna_25C, volga_25P =
    vanna_25P =
