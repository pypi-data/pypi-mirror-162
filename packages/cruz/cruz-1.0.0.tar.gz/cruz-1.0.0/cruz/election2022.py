import pyarrow as pa
import pandas as pd
import requests
import io

import numpy as np

import random
from enum import Enum

BASE_URL = "https://data.noteable.io"
ELECTION_DATA = "santa-cruz-election-2022"

MEASURE_D = "measure-d.arrow"
MEASURE_C = "measure-c.arrow"


def load_dataset(
    race="measure-d",
    namespace="santa-cruz-election-2022",
):
    if race.upper() == "measure-d":
        url = f"{BASE_URL}/{ELECTION_DATA}/{MEASURE_D}"
    elif race.upper() == "measure-c":
        url = f"{BASE_URL}/{ELECTION_DATA}/{MEASURE_C}"
    else:
        raise ValueError("Invalid dataset name. Pick either measure-d or measure-c.")

    response = requests.get(url, stream=True)

    with pa.ipc.open_file(io.BytesIO(response.content)) as reader:
        df = reader.read_pandas()
        return craft_visual_index(df)


mid_right_digits = ["6", "7", "8"]
mid_left_digits = ["1", "2", "3"]


class City(Enum):
    SANTA_CRUZ = 1
    CAPITOLA = 2
    WATSONVILLE = 3
    SCOTTS_VALLEY = 4


# The districts, from West to East (left to right)
district_order = "35124"


def remap_district(s):
    """
    Remaps a district number to the visual order.

    3 -> 1
    5 -> 2
    1 -> 3
    2 -> 4
    4 -> 5

    """
    return str(district_order.index(s) + 1)


def rework_spot(s):
    district = s[0]

    first_digit = remap_district(s[0])
    city_digit = s[1]

    final_digits = s[2:]

    # City of Santa Cruz
    if city_digit == City.SANTA_CRUZ:
        # Santa Cruz is primarily in district 3. There are two precincts in districts 5 and 1 though.
        if district == "3":
            return f"1{random.choice(mid_right_digits)}{final_digits}"
        if district == "1":
            return f"3{random.choice(mid_left_digits)}{final_digits}"
        if district == "5":
            return f"2{random.choice(mid_right_digits)}{final_digits}"
        else:
            return f"{first_digit}{random.choice('23456')}{final_digits}"
    elif city_digit == City.CAPITOLA:
        if district == "1":
            return f"{first_digit}{3}{final_digits}"
        if district == "2":
            return f"3{random.choice(mid_right_digits)}{final_digits}"
    elif city_digit == City.WATSONVILLE:
        if district == "4":
            return f"4{random.choice(mid_right_digits)}{final_digits}"
        if district == "2":
            return f"43{final_digits}"
    elif city_digit == City.SCOTTS_VALLEY:
        # We keep it the same for Scotts Valley since it's only one precinct
        pass

    final = first_digit + city_digit + s[2:]
    return final


def craft_visual_index(df: pd.DataFrame):
    """Create a column that allows for dot plots that roughly mirrors the
    visual order of the cities districts."""
    # Reassign a visual index to the dataframe
    df["remapped_precinct"] = df["Precinct"].map(rework_spot).astype(int)
    df.sort_values(by="remapped_precinct", inplace=True)
    df["Geographic Index"] = np.linspace(0, 1, num=len(df.index))
    df.drop(columns=["remapped_precinct"], inplace=True)
    return df
