import pandas as pd
from gui.models.sim_connections import AspenConnection


def main():
    from tests_.mock_data import ASPEN_BKP_FILE_PATH

    con_obj = AspenConnection(ASPEN_BKP_FILE_PATH)

    sim_data = con_obj.get_simulation_data()

    # convert uneven dict of arrays into dataframe. Empty values are NaN
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in sim_data.items()]))

    print(df)


if __name__ == "__main__":
    main()
