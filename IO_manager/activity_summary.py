class ActivitySummary:
    def __init__(self):
        self.log = []

    def summary(self, updates, actions=""):
        if updates == "Update":
            self.log.append(actions)
        elif updates == "Fetch":
            print("Summary:\n")
            for index, history in enumerate(self.log, start=1):
                print(f"{index}){history}")
