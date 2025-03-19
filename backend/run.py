import re
from database import SYSTEM_DATA_DB_CONTROLLER
from utils.maas import MAAS

CURRENT_HOSTNAME = "asrock355x-png-5cr12-02b.png.dcgpu"
NEW_HOSTNAME = "asrock357x-png-5cr12-02b.png.dcgpu"
# e.g. asrock325x-png-5cr14-02b.png.dcgpu

if __name__ == "__main__":
    # CONDUCTOR UPDATE
    pattern = r"^[^.]+\..+$"
    if not re.match(pattern, NEW_HOSTNAME) or not re.match(pattern, CURRENT_HOSTNAME):
        raise RuntimeError("Invalid hostname format")

    print("Searching on Conductor")
    system_data = SYSTEM_DATA_DB_CONTROLLER.query(hostname_ip=CURRENT_HOSTNAME)

    if not system_data:
        raise RuntimeError("System data not found")

    print("System found")

    print("Updating on Conductor")
    response = SYSTEM_DATA_DB_CONTROLLER.update(
        dict(
            id=system_data[0].id,
            name=NEW_HOSTNAME.split(".")[0],
            hostname_ip=NEW_HOSTNAME,
        )
    )

    # MAAS UPDATE
    loc = "ust" if "pngtechno" in CURRENT_HOSTNAME else "eq"

    print(f"Detected MaaS site at {loc.upper()}")
    maas = MAAS(loc)
    machine = maas.get_machine(CURRENT_HOSTNAME.split(".")[0])

    machine_id, power_type = machine["system_id"], machine["power_type"]
    
    if not machine_id or not power_type:
        raise RuntimeError("Machine ID not found")

    updated_machine = maas.update_machine(machine_id, NEW_HOSTNAME.split(".")[0], power_type)

    print("Updated machine in MAAS")

    # JENKINS