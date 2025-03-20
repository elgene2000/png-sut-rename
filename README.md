
# PNG SUT Renaming

This repo simplifies the process of renaming SUT within the same site.


## How to Use?

### manual_run.py


#### Prerequisite
1. Create env file at `.\backend\.env`
2. Export env
```
#CONDUCTOR
AMD_EMAIL=''
ATS_SECRET=''
VERIFY_CERTS=False
REQUEST_TIMEOUT=120
ATS_URL="https://conductor.amd.com"

#JENKINS
JENKINS_USER=''
JENKINS_CREDS=''

#MAAS
MAAS_EQ_HOST=''
MAAS_EQ_MAAS_API_KEY=''
MAAS_UST_HOST=''
MAAS_UST_MAAS_API_KEY=''
```

3. Enter OLD/NEW Hostname at `manual_run.py`
```
CURRENT_HOSTNAME = ""
NEW_HOSTNAME = ""
# e.g. asrock325x-png-5cr14-02b.png.dcgpu
```

#### Steps
```
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
python manual_run.py
```


