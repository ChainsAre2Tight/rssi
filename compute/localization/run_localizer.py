import my_types

# TODO: move to an appropriate place
from cmd.viz.viz_skibidi import RSSILocalizer, Config
import config


def run_localizer(
    loc_input: my_types.LocalizationInput,
) -> dict:

    cfg = Config(
        n=config.PATH_LOSS_EXPONENT,
        aggregate_rssi="median",
        compute_covariance=False,
    )

    localizer = RSSILocalizer(
        devices=loc_input.devices,
        GainModels=loc_input.gain_models,
        rssi_values=loc_input.rssi_values,
        positions=loc_input.positions,
        config=cfg,
    )

    return localizer.localize(verbose=False)
