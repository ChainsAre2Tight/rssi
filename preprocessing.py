import storage
from compute.reconstruction import reconstruct_measurement

if __name__ == "__main__":
    with storage.Session() as conn:
        reconstruct_measurement(conn, 1)