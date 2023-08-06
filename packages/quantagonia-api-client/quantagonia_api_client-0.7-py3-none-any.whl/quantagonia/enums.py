from enum import Enum

class HybridSolverConnectionType(Enum):
	CLOUD = 0
	LOCAL = 1

class HybridSolverServers(Enum):
    PROD = "https://api.quantagonia.com"
    STAGING = "https://staging.quantagonia.com"
    DEV = "https://dev.quantagonia.com"