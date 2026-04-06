import storage
import config
from compute.reconstruction import reconstruct_measurement

if __name__ == "__main__":
    with storage.Session() as conn:
        with storage.Transaction(conn) as t:
            reconstruct_measurement(t, config.MEASUREMENT_ID)