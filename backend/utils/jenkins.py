import os, time
import requests
from dotenv import load_dotenv

load_dotenv()


class Jenkins:
    def __init__(self):
        self.HOST = "http://dcgpuauto-jenkins.amd.com:8080"
        self.USER = os.environ.get("JENKINS_USER")
        self.CREDS = os.environ.get("JENKINS_CREDS")

    def install_sut_auth(self, new_hostname):
        # Install Jenkins
        payload = {
            "SUT_HOSTNAME": new_hostname,
            "SUT_CREDENTIALS": "default_-amd__credentials",
        }
        response = requests.post(
            f"{self.HOST}/job/At-Scale/job/sut-auth/job/manual-install-prod/buildWithParameters",
            auth=(self.USER, self.CREDS),
            data=payload,
        )
        if response.status_code == 201:
            loc = response.headers.get("Location").split("/")[-2]

            timeout = 60  # Maximum time to wait for the build number
            start_time = time.time()

            while time.time() - start_time < timeout:
                queue_response = requests.get(
                    f"{self.HOST}/queue/item/{loc}/api/json", auth=(self.USER, self.CREDS)
                )
                
                queue_data = queue_response.json()

                if "executable" in queue_data and "number" in queue_data["executable"]:
                    build_num = queue_data["executable"]["number"]
                    return build_num
                time.sleep(1)
            raise TimeoutError("Failed to get build number")
        else:
            print(f"Failed to install SUT Auth")
            return None

    def uninstall_sut_auth(self, new_hostname: str):
        # Uninstall Jenkins
        payload = {"SUT_HOSTNAME": new_hostname, "SUT_CREDENTIALS": "amd_recovery"}
        response = requests.post(
            f"{self.HOST}/job/At-Scale/job/sut-auth/job/manual-uninstall-prod/buildWithParameters",
            auth=(self.USER, self.CREDS),
            data=payload,
        )
        if response.status_code == 201:
            loc = response.headers.get("Location").split("/")[-2]

            timeout = 60  # Maximum time to wait for the build number
            start_time = time.time()

            while time.time() - start_time < timeout:
                queue_response = requests.get(
                    f"{self.HOST}/queue/item/{loc}/api/json", auth=(self.USER, self.CREDS)
                )
                
                queue_data = queue_response.json()

                if "executable" in queue_data and "number" in queue_data["executable"]:
                    build_num = queue_data["executable"]["number"]
                    return build_num
                time.sleep(1)
            raise TimeoutError("Failed to get build number")
        else:
            print(f"Failed to uninstall SUT Auth")
            return None

    def get_job_progress(self, type: str, build_num: str):
        if type not in ("install", "uninstall"):
            raise ValueError("type must be either 'install' or 'uninstall'")

        job_response = requests.get(
            f"{self.HOST}/job/At-Scale/job/sut-auth/job/manual-{type}-prod/{build_num}/api/json",
            auth=(self.USER, self.CREDS),
        )
        return job_response.json()
