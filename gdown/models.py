from dataclasses import dataclass


@dataclass
class GdownRsp:
    url: str
    output: str
    last_modified: str
    total_time: str
