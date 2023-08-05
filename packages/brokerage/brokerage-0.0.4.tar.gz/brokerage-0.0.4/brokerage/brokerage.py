from .make_simulator import Simulator

def login(url, username, password, random_state=42, speed=0.1):
    return Simulator(random_state=random_state, speed=speed)
