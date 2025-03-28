import re
import time
import json
import requests

from utils.logger import logger
from utils.maas import MAAS
from utils.jenkins import Jenkins
from utils.paramiko import Paramiko
from database import SYSTEM_DATA_DB_CONTROLLER


CURRENT_HOSTNAME = ""
NEW_HOSTNAME = ""
# e.g. asrock325x-png-5cr14-02b.png.dcgpu

if __name__ == "__main__":
    pattern = r"^[^.]+\..+$"
    if not re.match(pattern, NEW_HOSTNAME) or not re.match(pattern, CURRENT_HOSTNAME):
        logger.error("Invalid hostname format")
        raise RuntimeError("Invalid hostname format")

    # ======================================================
    # CONDUCTOR UPDATE
    # Note: This section configures the hostname in Conductor
    # ======================================================
    logger.info("Searching on Conductor")
    system_data = SYSTEM_DATA_DB_CONTROLLER.query(hostname_ip=CURRENT_HOSTNAME)

    if not system_data:
        logger.error("System not found")
        raise RuntimeError("System data not found")

    logger.info("System found")

    system_id = system_data[0].get("id", "")
    platform_config = system_data[0].get("platform_config", {})
    power_controllers = platform_config.get("power_controllers", [])
    platforms = system_data[0].get("platforms", {})
    platform_name = platforms.get("name", "")

    if "asrock" in platform_name.lower():
        logger.info("Detected Asrock platform")
        for power_controller in power_controllers:
            if power_controller.get("type", "") == "bmc" and CURRENT_HOSTNAME.split(".")[0] in power_controller.get("ip", ""):
                logger.info("Configuring BMC")
                #REDFISH PATCH REQUEST
                url = f"https://{power_controller["ip"]}/redfish/v1/Managers/Self/EthernetInterfaces/bond0"

                username=power_controller["user"]
                password=power_controller["pass"]

                headers = {
                    "Content-Type": "application/json",
                    "If-Match": "*"
                }

                payload = {
                    "HostName": f"bmc-{NEW_HOSTNAME.split('.')[0]}"
                }

                response = requests.patch(url, auth=(username, password), headers=headers, data=json.dumps(payload), verify=False)
                power_controller["ip"] = "bmc-" + NEW_HOSTNAME.split(".")[0] + ".amd.com" if response.status_code == 202 else power_controller["ip"]
                break
    elif "splinter" in platform_name.lower():
        pass

    logger.info("Updating on Conductor")
    response = SYSTEM_DATA_DB_CONTROLLER.update(
        dict(
            id=system_id,
            name=NEW_HOSTNAME.split(".")[0],
            hostname_ip=NEW_HOSTNAME,
            platform_config = {
                "power_controllers" : power_controllers
            }
        )
    )


    # ======================================================
    # MAAS UPDATE
    # Note: This section configures the hostname in MaaS
    # ======================================================
    site = "ust" if "pngtechno" in CURRENT_HOSTNAME else "eq"

    logger.info(f"Detected MaaS site at {site.upper()}")
    logger.info("Searching for machine in MAAS")
    maas = MAAS(site)
    machine = maas.get_machine(CURRENT_HOSTNAME.split(".")[0])

    machine_id, power_type = machine["system_id"], machine["power_type"]

    if not machine_id or not power_type:
        logger.error("Machine not found")
        raise RuntimeError("Machine ID not found")

    logger.info("Machine found")
    updated_machine = maas.update_machine(machine_id, NEW_HOSTNAME.split(".")[0], power_type)

    logger.info("Updated machine in MAAS")


    # ======================================================
    # JENKINS UNINSTALL
    # Note: This section uninstalls SUT Auth in Jenkins
    # ======================================================    
    logger.info("Uninstalling SUT Auth...")
    jenkins = Jenkins()
    TIMEOUT = 300
    uninstall_start_time = time.time()

    build_num = jenkins.uninstall_sut_auth(NEW_HOSTNAME)

    if not build_num:
        logger.error("Failed to uninstall SUT Auth")
        raise RuntimeError("Failed to uninstall SUT Auth")

    while True:
        if time.time() - uninstall_start_time > TIMEOUT:
            logger.error("Uninstall timed out")
            raise TimeoutError("Uninstall timed out")

        job_progress = jenkins.get_job_progress("uninstall", build_num)

        if job_progress.get("result") == "SUCCESS":
            logger.info("Uninstalled SUT Auth Successfully")
            break
        time.sleep(1)


    # ======================================================
    # PARAMIKO HOSTNAME CONFIG
    # Note: This section configures the hostname in SUT via SSH
    # ======================================================   
    logger.info("Configuring hostname...")
    try:
        ssh = Paramiko(hostname=NEW_HOSTNAME, username="amd", password="amd123")
        logger.info("Connected to the host")
        ssh.execute(f"sudo hostnamectl set-hostname {NEW_HOSTNAME}")
        ssh.execute(rf"sudo sed -i 's/^127\.0\.1\.1.*/127.0.1.1 {NEW_HOSTNAME} {NEW_HOSTNAME.split('.')[0]}/' /etc/hosts")
    except Exception as e:
        logger.error(f"An error occurred: {e}")  
        raise Exception("An error occurred: {e}") 
    logger.info('Configured hostname in SUT')


    # ======================================================
    # JENKINS INSTALL
    # Note: This section reinstalls SUT Auth in Jenkins
    # ======================================================   
    logger.info("Installing SUT Auth...")
    install_start_time = time.time()

    build_num = jenkins.install_sut_auth(NEW_HOSTNAME)

    if not build_num:
        logger.error("Failed to install SUT Auth, build number not found")
        raise RuntimeError("Failed to install SUT Auth")

    while True:
        if time.time() - install_start_time > TIMEOUT:
            logger.error("Install timed out")
            raise TimeoutError("Install timed out")

        job_progress = jenkins.get_job_progress("install", build_num)

        if job_progress.get("result") == "SUCCESS":
            logger.info("Installed SUT Auth Successfully")
            break

        time.sleep(1)

    logger.info("All operations completed successfully!")