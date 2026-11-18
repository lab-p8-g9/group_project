# In-memory activity log used to report application actions.


class ActivitySummary:
    # Record activity updates and print them as a numbered summary.

    def __init__(self):
        self.log = []

    def summary(self, updates, actions=""):
        # Update or fetch the activity log.
        if updates == "Update":
            self.log.append(actions)
        elif updates == "Fetch":
            print("Summary:\n")
            for index, history in enumerate(self.log, start=1):
                print(f"{index}){history}")
