#!/usr/bin/env python2.7

import requests
import sys
import os
import argparse
import datetime as dt
import wget
import yaml
import re


API_ENDPOINT = "https://api-argonaut.rokubun.cat/api"
HEADERS = {'user-agent': 'custom app', 'ApiKey': 'ARGONAUT.PUB.609B-4D9E-80B7', 'accept': 'application/json'}


def run(argonaut_log, base_station, images_metadata, secret_token, workspace):

    global API_ENDPOINT
    global HEADERS
    global TOKEN
    
    # Generate dictionary with the provided files
    if base_station is not None and images_metadata is not None:
        files = {'rover_file': open(argonaut_log, 'rb'), 
                 'base_file': open(base_station, 'rb'), 
                 'metadata_file': open(images_metadata, 'rb')}
    elif base_station is not None and images_metadata is None:
        files = {'rover_file': open(argonaut_log, 'rb'), 
                 'base_file': open(base_station, 'rb')}
    elif base_station is None and images_metadata is not None:
        files = {'rover_file': open(argonaut_log, 'rb'), 
                 'metadata_file': open(images_metadata, 'rb')}
    elif base_station is None and images_metadata is None:
        files = {'rover_file': open(argonaut_log, 'rb')}

    data = {'type': 'GNSS', 'token': secret_token}
    url = API_ENDPOINT + "/processes/"

    # Generate POST query
    query = requests.post(url, headers=HEADERS, files=files, data=data)

    if query.status_code == 200:

        task_id = query.json()['id']
        n_msg = 0

        # Loop until processing finishes
        while True:

            # Get status
            result = requests.get(url + str(task_id) + "?token=" + secret_token, headers=HEADERS)

            if result.json()["process"]["status"] == "PENDING":
                sys.stderr.write("Waiting for task to be accepted by PaaS\n")
                sys.stdout.flush()

            # Log messages generated during processing
            elif result.json()["process"]["status"] == "RUNNING":
                msg = result.json()['log']
                if len(msg) > n_msg:
                    n_msg = len(msg)
                    sys.stderr.write(msg.pop()['message'])

            if result.json()["process"]["status"] == "FINISHED":

                for res in result.json()["results"]:

                    if res["name"][-4:] == ".zip":

                        # Download results
                        filename = os.path.join(workspace,  "result_" + dt.datetime.now().strftime("%Y-%m-%d_%H.%M.%S") + ".zip")
                        sys.stderr.write("Downloading results to [" + filename + "]\n")
                        wget.download(res['url'], filename)

                exit(0)

    elif query.status_code == 401 and query.json()["message"] == "User token not found":

        sys.stderr.write("Provided secret token [" + secret_token + "] not found in database. Please go to the Software tab in your "
                         "Rokubun's PaaS account personal area and copy it from there (https://paas.rokubun.cat/#!/account)\n")
        exit(1)
    
    else: 

        sys.stderr.write("Something has gone wrong with your request. Please send us an email to saas@rokubun.cat, and we'll take care of "
                         "it as soon as possible\n")
        exit(1)



# ----------------------

if __name__ == "__main__":

    # Read command line arguments
    parser = argparse.ArgumentParser(description="This is Rokubun's API script for Argonaut data processing. "
                                                 "The script takes care of uploading the GNSS logs from Argonaut "
                                                 "alongside with the metadata from the drone's camera to Rokubun's "
                                                 "PaaS. The script returns a ZIP file with the new metadata file, "
                                                 "which has more precise geo-tags for all the images. The ZIP "
                                                 "also contains additional information on the GNSS processing "
                                                 "that took place")

    parser.add_argument('--configuration-file', '-c',
                        required=False, type=str,
                        help="YAML file with configuration to use. See configuration_template.yaml for more info on the file format" 
                             "Inputs provided in this file will be overwritten by the following command-line arguments (if provided)")
    parser.add_argument('--argonaut-log', '-a',
                        required=False, type=str,
                        help="(Mandatory) Argonaut LOG file (.rok extension) with the GNSS data to process")
    parser.add_argument('--base-station', '-b', required=False, type=str,
                        help="(Optional) GNSS file for the reference station. If not provided, a station "
                             "from the neighbouring networks will be used")
    parser.add_argument('--images-metadata', '-i',
                        required=False, type=str,
                        help="(Optional) CSV file containing the metadata for every image acquired by the sensor flown alongside "
                             "with Argonaut")
    parser.add_argument('--secret-token', '-s',
                        required=False, type=str,
                        help="(Mandatory) User's secret token. Can be found in the Account section of User's tab in paas.rokubun.cat"
                             "It consists of 30 alphanumeric characters in uppercase following the structure: "
                             "XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX")
    parser.add_argument('--workspace', '-w',
                        required=False, type=str,
                        help="(Mandatory) Workspace where result will be saved. If it doesn't exist, will be created")

    args = parser.parse_args()    

    # Variables declaration
    argonaut_log = None
    base_station = None
    images_metadata = None
    secret_token = None
    workspace = None

    # Read inputs from YAML
    if args.configuration_file is not None:
        if not os.path.isfile(args.configuration_file):
            sys.stderr.write("Path to the provided YAML configuration file [" + args.configuration_file + "] not correct. "
                 "Check and run again\n")
            exit(1)
        with open(args.configuration_file, 'r') as y:
            configuration = yaml.load(y)

        for conf in configuration:
            if conf == "argonaut-log":
                if configuration["argonaut-log"] is not None:
                    argonaut_log = configuration["argonaut-log"]
            elif conf == "base-station":
                if configuration["base-station"] is not None:
                    base_station = configuration["base-station"]
            elif conf == "images-metadata":
                if configuration["images-metadata"] is not None:
                    images_metadata = configuration["images-metadata"]
            elif conf == "secret-token":
                if configuration["secret-token"] is not None:
                    secret_token = configuration["secret-token"]
            elif conf == "workspace":
                if configuration["workspace"] is not None:
                    workspace = configuration["workspace"]
            else:
                sys.stderr.write("Found unknown tag [" + conf + "] in YAML configuration file. Will be ignored\n")
                
    # Read inputs from command-line arguments (will overwrite the ones from YAML)
    if args.argonaut_log is not None:
        argonaut_log = args.argonaut_log
    if args.base_station is not None:
        base_station = args.base_station
    if args.images_metadata is not None:
        images_metadata = args.images_metadata
    if args.secret_token is not None:
        secret_token = args.secret_token

    if args.workspace is not None:
        workspace = args.workspace

    # Check that provided inputs exist and are correct
    if argonaut_log is not None and not os.path.isfile(argonaut_log):
        sys.stderr.write("Path to the provided Argonaut LOG file [" + argonaut_log + "] not correct. "
                         "Check and run again\n")
        exit(1)
    if base_station is not None and not os.path.isfile(base_station):
        sys.stderr.write("Path to the provided GNSS file for the reference station [" + base_station + "] not correct. "
                         "Check and run again\n")
        exit(1)
    if images_metadata is not None and not os.path.isfile(images_metadata):
        sys.stderr.write("Path to the CSV file containing the metadata for every image [" + images_metadata + "] not correct. "
                         "Check and run again\n")
        exit(1)
    if secret_token is not None and re.match("[A-Z|0-9]{6}-[A-Z|0-9]{6}-[A-Z|0-9]{6}-[A-Z|0-9]{6}-[A-Z|0-9]{6}", secret_token) is None:
        sys.stderr.write("User's provided secret token [" + secret_token + "] doesn't match the expected format of "
                         "30 alphanumeric characters in uppercase following the structure: "
                         "XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX."
                         "Please check it again in your Rokubun's PaaS account personal area and copy "
                         "it from there (https://paas.rokubun.cat/#!/account)\n")
        exit(1)
    if not os.path.isdir(workspace):
        os.makedirs(workspace)   

    # Check on mandatory inputs
    if argonaut_log is None:
        sys.stderr.write("Missing required Argonaut LOG\n")
        exit(1)
    if secret_token is None:
        sys.stderr.write("Missing required secret-token to identify the user\n")
        exit(1)
    if workspace is None:
        sys.stderr.write("Missing required path to workspace where to keep the results\n")
        exit(1)

    # Print provided inputs
    xstr = lambda s: s or ""    # Cast None to empty strings
    sys.stderr.write("Provided inputs: \n")
    sys.stderr.write("    argonaut-log = " + xstr(argonaut_log) + "\n")
    sys.stderr.write("    base-station = " + xstr(base_station) + "\n")
    sys.stderr.write("    images-metadata = " + xstr(images_metadata) + "\n")
    sys.stderr.write("    secret-token = " + xstr(secret_token) + "\n")
    sys.stderr.write("    workspace = " + xstr(workspace) + "\n")

    run(argonaut_log, base_station, images_metadata, secret_token, workspace)


