import storage
import config
from compute.reconstruction import reconstruct_measurement

if __name__ == "__main__":
    with storage.Session() as conn:
        reconstruct_measurement(conn, config.MEASUREMENT_ID)