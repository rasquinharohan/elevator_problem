
from building import Building


if __name__ == '__main__':
    s = Building(2, 50, 10, [dict(time=2, id='pass1', source=1, dest=37),
                            dict(time=2, id='pass2', source=2, dest=16),
                            dict(time=10, id='pass3', source=20, dest=1),
                            dict(time=14, id='pass4', source=38, dest=48),
                            dict(time=17, id='pass5', source=26, dest=5)])
    s.schedule()