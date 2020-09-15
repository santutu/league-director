from leaguedirector.utils import find_procs_by_name, find_port_by_pid


class ReplayApiHostSingleton:
    _instance = None
    _host = 'https://127.0.0.1:2999'

    def __init__(self):
        if not ReplayApiHostSingleton._instance:
            print("__init__ method called but nothing is created")
        else:
            print("instance already created:", self.getInstance())

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = ReplayApiHostSingleton()
        return cls._instance

    def get_host(self):
        return self._host

    def set_host(self, host):
        self._host = host
        return self

    def find_and_set_host(self):
        processes = find_procs_by_name("League of Legends.exe")
        if len(processes) == 0:
            return False

        port = find_port_by_pid(processes[0].pid)

        self.set_host(f"https://127.0.0.1:{port}")

        return True
