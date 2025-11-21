from pathlib import Path
from locust import HttpUser, task, between, LoadTestShape  # type: ignore
from typing import Any, List, Tuple
import orjson


from itertools import cycle


class SourcesUser(HttpUser):
    wait_time = between(0.1, 0.1)

    # def on_start(self):
    #     path = Path('/workspace/backend/locust/fuzzing.txt')
    #     with open(path, "r") as f:
    #         lines = [l.strip() for l in f.readlines() if l.strip()]

    #     self.payloads = cycle(lines)

    @task
    def fuzz(self):
        # payload = next(self.payloads)
        # self.client.get(f"/{payload}")
        self.client.get("/users")


class ConstantRPSLoadShape(LoadTestShape):
    target_rps = 2000  # Celowana liczba żądań na sekundę
    ramp_up_time = 50  # Czas w sekundach do osiągnięcia pełnego obciążenia
    time_limit = 600  # Czas trwania testu

    def tick(self):  # type: ignore
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_rps = min(self.target_rps, run_time * (self.target_rps / self.ramp_up_time))

        user_count = current_rps
        spawn_rate = user_count / run_time if run_time > 0 else user_count

        return (user_count, spawn_rate)
