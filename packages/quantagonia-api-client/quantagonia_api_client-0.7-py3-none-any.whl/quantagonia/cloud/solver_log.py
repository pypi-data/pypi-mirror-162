class SolverLog:
    def __init__(self):
        self.log: str = ""

    """
    takes as input the updated log. It will make sure that the old log is contained in the new log, and print the
    difference to the screen
    """
    def update_log(self, new_log: str) -> None:
        if new_log == "":
            return

        old_log_len = len(self.log)

        if self.log != new_log[:old_log_len]:
            print("WARNING: there was some suspicious discrepancy in the solver log received from the server. "
                  "The solver log might not be printed in the order as the solver generated it.")

        print(new_log[old_log_len:], end='')
        self.log = new_log
