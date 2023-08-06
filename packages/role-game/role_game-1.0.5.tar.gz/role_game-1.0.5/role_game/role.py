import random
import time


class Role:
    def __init__(self,name='编程猫', hit_points=20, aggressivity=1, defensive_power=0):
        self.name = name
        self.hit_points = hit_points
        self.aggressivity = aggressivity
        self.defensive_power = defensive_power
        self.bag = []
        self.armor = None
        self.prop = None
        while True:
            if self.hit_points <= 0:
                time.sleep(1)
                print(self.name, '狗带了')
                del self

    def die(self):
        self.hit_points = 0
        print(self.name, '往自己脸上拍了块板砖')

    def hit_self(self):
        self.hit_points -= self.aggressivity + random.randint(0,3) - self.defensive_power
        if self.hit_points <= 0:
            print(self.name, '往自己脸上拍了块板砖')

    def kill(self,role):
        print(self.name, '作弊杀死了', role.hit_points)
        role.hit_points = 0

    def attack(self,role):
        role.hit_points -= self.aggressivity + random.randint(0, 3) - role.defensive_power
        if role.hit_points <= 0:
            print(self.name, '干掉了', role.name)

    def use(self,weapon):
        weapon.code()

    def armed_to_armor(self,armor):
        if self.armor != None:
            print('<type class.Role>（生气地）：你想剁手吗？')
        elif (armor not in self.bag):
            print('<type class.Role>（生气的）：你™的甭想无中生有！')
        else:
            self.armor = self.bag[self.bag.index(armor)]
            del self.bag[self.bag.index(armor)]
            self.aggressivity += armor.aggressivity

    def has(self,objact):
        self.bag.append(objact)

    def armed_to_prop(self, prop):
        if self.prop != None:
            print('<type class.Role>（生气地）：你想砍头吗？')
        elif (prop not in self.bag):
            print('<type class.Role>（生气的）：你™的甭想无中生有！')
        else:
            self.prop = self.bag[self.bag.index(prop)]
            del self.bag[self.bag.index(prop)]
            self.defensive_power += prop.defensive_power

    def remove_armor():
        if self.armor == None:
            print('<type class.Role>（生气地）：你想剁手吗？')
        else:
            self.bag.append(self.armor)
            self.aggressivity -= self.armor.aggressivity
            self.armor = None

    def remove_prop():
        if self.prop == None:
            print('<type class.Role>（生气地）：你想砍头吗？')
        else:
            self.bag.append(self.prop)
            self.defensive_power -= self.prop.defensive_power
            self.prop = None
