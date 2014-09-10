# Load the PingOne backend.
from samlauth import pingone

class NanolearningProvider(pingone.PingOneProvider):
    NAME = 'Applied Materials/Eteris account'
