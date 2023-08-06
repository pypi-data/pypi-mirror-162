from dataclasses import dataclass


@dataclass
class Runner:
    name: str
    runner_id: str
    parkrun_data: list
    recents: list
    junior: bool = False

    def __post_init__(self):
        self.total_parkruns = sum(x.runs for x in self.parkrun_data if not x.junior)
        self.total_junior_parkruns = sum(x.runs for x in self.parkrun_data if x.junior)
        self.shirt = None
        if self.junior and self.total_parkruns >= 10:
            self.shirt = 10
        for i in (25, 50, 100, 250, 500):
            if self.total_parkruns >= i:
                self.shirt = i

        self.band = None
        for i in (11, 21, 50, 100):
            if self.total_junior_parkruns >= i:
                self.band = i

        if self.parkrun_data:
            self.pb = min(x.pb for x in self.parkrun_data)

    def get_parkrun_data(self, parkrun):
        for p in self.parkrun_data:
            if p.event == parkrun:
                return p

    def serialise(self):
        # dataclasses.asdict gives a recursion error
        return {
            "name": self.name,
            "runner_id": self.runner_id,
            "parkrun_data": self.parkrun_data,
            "recents": self.recents,
            "junior": self.junior,
        }
