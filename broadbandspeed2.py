from influxdb import InfluxDBClient
import json
import logging
import os
import subprocess


def setup_logging():
    logging.basicConfig(
         format='%(asctime)s %(levelname)s %(message)s',
         datefmt='%Y-%m-%d %H:%M:%S',
         level=logging.INFO
         )
    # Create a logger
    _log = logging.getLogger(__name__)
    # Create handlers
    f_handler = logging.FileHandler(get_script_dir() + '/broadbandspeed.log', 'a')
    # # Set the log level
    f_handler.setLevel(logging.INFO)
    # # Create formatter and add it to the handler
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler.setFormatter(f_format)
    # # Add the handler(s) to the log object
    _log.addHandler(f_handler)
    # # Return the log
    return _log


def get_script_dir():
    # Find the location of this script
    _dir = os.path.dirname(os.path.realpath(__file__))
    return _dir


def get_speed_test_results():
    process = subprocess.run([get_script_dir() + "/speedtest.exe", "--format=json"], 
                            stdout=subprocess.PIPE,
                            universal_newlines=True,
                            check=True)
    res = json.loads(process.stdout)
    log.info(res)
    return(res)


if __name__ == "__main__":
    log = setup_logging()

    log.info("Connecting to influx")
    client = InfluxDBClient(host='localhost',
                            port='8086',
                            database='mydb')

    log.info("Starting SpeedTest")
    speedtest = get_speed_test_results()
    print(json.dumps(speedtest, indent=2))

    json_row = [
        {
            "measurement": "broadbandspeed",
            "time": speedtest["timestamp"],
            "tags": {
                "isp_ip_address": speedtest["server"]["ip"],
                "isp": speedtest["isp"],
                "date": speedtest["timestamp"].split("T")[0],
                "dtime": speedtest["timestamp"].split("T")[1][:-1],
                "target_server": speedtest["server"]["location"],
            },

            "fields": {
                "upload_mbs": float(speedtest["upload"]["bandwidth"]) / 125000,
                "download_mbs": float(speedtest["download"]["bandwidth"]) / 125000,
                "ping_ms": float(speedtest["ping"]["latency"])
            }
        }
    ]
    print(json.dumps(json_row, indent=2,))
    client.write_points(json_row)

    log.info("Finished SpeedTest")
