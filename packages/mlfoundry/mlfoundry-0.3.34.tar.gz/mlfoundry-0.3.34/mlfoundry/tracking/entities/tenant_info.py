from pydantic import BaseModel


class AuthServerInfo(BaseModel):
    auth_server_url: str

    class Config:
        allow_mutation = False
