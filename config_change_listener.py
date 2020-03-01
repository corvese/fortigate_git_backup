from fastapi import FastAPI
from starlette.requests import Request
from fortigate_backup import fortigate_backup
import creds

app = FastAPI()

@app.get("/configuration_backup")
def read_root(request: Request):
    client_host = request.client.host
    backup = fortigate_backup(
        fortigate_ip=client_host, 
        username=creds.username, 
        password=creds.password
        )
    backup.backup

