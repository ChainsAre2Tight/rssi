

import config
import storage
from storage.localization_jobs import insert_localization_jobs


if __name__ == "__main__":
    with storage.Session() as conn:
        print(insert_localization_jobs(
            conn,
            config.MEASUREMENT_ID,
            [
                (2, "A8:E2:91:40:8E:C3"),
            ]
        ))