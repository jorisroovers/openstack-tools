class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def OK(msg):
        return bcolors.OKGREEN + msg + bcolors.ENDC

def INFO(msg):
        return bcolors.OKBLUE + msg + bcolors.ENDC

def NOK(msg):
        return bcolors.FAIL + msg + bcolors.ENDC

# commonly used status strings, color coded
UP = OK("OK")
DOWN = NOK("DOWN")
DONE = OK("DONE")
FAIL = NOK("FAIL")