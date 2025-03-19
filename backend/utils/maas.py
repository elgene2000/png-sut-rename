import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
from oauthlib.oauth1 import SIGNATURE_PLAINTEXT

load_dotenv()

MAAS_CONFIG = {
    "eq": {
        "host": os.environ.get("MAAS_EQ_HOST"),
        "api_key": os.environ.get("MAAS_EQ_MAAS_API_KEY"),
    },
    "ust": {
        "host": os.environ.get("MAAS_UST_HOST"),
        "api_key": os.environ.get("MAAS_UST_MAAS_API_KEY"),
    },
}


class MAAS:
    def __init__(self, loc: str):
        if loc not in ("eq", "ust"):
            raise ValueError("loc must be either 'eq' or 'ust'")

        self.HOST = MAAS_CONFIG[loc]["host"]
        self.API_KEY = MAAS_CONFIG[loc]["api_key"]
        self.CONSUMER_KEY, self.CONSUMER_TOKEN, self.SECRET = self.API_KEY.split(":")
        self.MAAS = OAuth1Session(
            self.CONSUMER_KEY,
            resource_owner_key=self.CONSUMER_TOKEN,
            resource_owner_secret=self.SECRET,
            signature_method=SIGNATURE_PLAINTEXT,
        )

    def get_machine(self, name: str) -> str | None:
        # e.g. name = asrock325x-png-5cr14-02b
        try:
            node = self.MAAS.get(
                f"{self.HOST}/MAAS/api/2.0/machines/", params={"hostname": name}
            )
            node.raise_for_status()
            if len(node.json()) == 0:
                return None
            return node.json()[0]
        except Exception as e:
            return None

    def update_machine(
        self, machine_id: str, new_name: str, power_type: str
    ) -> str | None:
        # e.g. name = asrock325x-png-5cr14-02b
        try:
            node = self.MAAS.put(
                f"{self.HOST}/MAAS/api/2.0/machines/{machine_id}/",
                data={
                    "hostname": new_name,
                    **(
                        {
                            "power_parameters_power_on_uri": f"http://png-dcgpuval-platypiserver.png.dcgpu/api/v1/{new_name}/power_on_pxe",
                            "power_parameters_power_off_uri": f"http://png-dcgpuval-platypiserver.png.dcgpu/api/v1/{new_name}/power_off_pxe",
                            "power_parameters_power_query_uri": f"http://png-dcgpuval-platypiserver.png.dcgpu/api/v1/{new_name}/power_check_pxe",
                        }
                        if power_type == "webhook"
                        else {}
                    ),
                },
            )
            node.raise_for_status()
            if len(node.json()) == 0:
                return None
            return node.json()
        except:
            return None
