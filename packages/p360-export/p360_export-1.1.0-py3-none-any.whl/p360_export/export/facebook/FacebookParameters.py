import random
from typing import List


class FacebookParameters:
    def generate_parameters(self, df_size, schema) -> dict:
        session_id = random.randint(1, 1000000)
        return {
            "payload": {"schema": schema, "data": []},
            "session": {"session_id": session_id, "batch_seq": 0, "last_batch_flag": False, "estimated_num_total": df_size},
        }

    def update_parameters(self, parameters: dict, batch: List[List[str]], is_last_batch: bool):
        if is_last_batch:
            parameters["session"]["last_batch_flag"] = True
        parameters["payload"]["data"] = batch
        parameters["session"]["batch_seq"] += 1
