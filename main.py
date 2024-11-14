import pygame,time,random

pygame.init()

ZOOM = 1
CAMERA = [0,0]

clock = pygame.time.Clock()
resolution = (800,800)
screen = pygame.display.set_mode(resolution)

class Data:
    def __init__(self,sender,content,x,y,vx,vy):
        self.sender = sender
        self.content = content
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.receive_since = 0
        self.r = 3
    def received(self):
        self.receive_since = time.time()
    def draw(self):
        if self.receive_since == 0:
            power = min(1,self.content/10)
            pygame.draw.circle(screen, [255*(1-power),255*power,0], [self.x*ZOOM+CAMERA[0],self.y*ZOOM+CAMERA[1]], max(1,self.r*ZOOM))
    def update(self):
        self.x += self.vx
        self.y += self.vy
        return self.x-self.r > resolution[0] or self.x+self.r < 0 or self.y-self.r > resolution[1] or self.y+self.r < 0

class Device:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.vx = (random.random()-0.5)*2*10
        self.vy = (random.random()-0.5)*2*10
        self.probability_send = 1/60
        self.r = 20
    def send(self, message, target, speed):
        return Data(self,message,self.x,self.y,((target.x+target.vx*speed)-self.x)/speed,((target.y+target.vy*speed)-self.y)/speed)
    def draw(self):
        pygame.draw.circle(screen, [100,100,100], [self.x*ZOOM+CAMERA[0],self.y*ZOOM+CAMERA[1]], max(1,self.r*ZOOM))
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if random.random() < self.probability_send and len(world.datas) < 500:
            world.datas.append(self.send(0,world.randomDeviceButNot(self),120))
        trashs = []
        for data in world.datas:
            if data.sender != self and data.receive_since == 0:
                dx = data.x-self.x
                dy = data.y-self.y
                d = (dx**2+dy**2)**0.5
                if d < self.r+data.r:
                    world.datas.append(self.send(data.content+1,data.sender,300))
                    trashs.append(data)
        for trash in trashs:
            world.datas.remove(trash)

class World:
    def __init__(self):
        self.devices = []
        self.datas = []
    def randomDeviceButNot(self,device):
        devices_but_not = [i for i in self.devices if i != device]
        return devices_but_not[random.randint(0,len(devices_but_not)-1)]
    def update(self):
        for device in self.devices:
            device.update()
        for data in self.datas:
            data.update()
    def draw(self):
        for device in self.devices:
            device.draw()
        for data in self.datas:
            data.draw()

world = World()
for i in range(50):
    world.devices.append(Device(random.randint(50,resolution[0]-50),random.randint(50,resolution[1]-50)))

click = [False,[],[]]
while True:
    clock.tick(60)
    screen.fill((0,0,0))
    world.update()
    world.draw()
    if click[0]:
        click[1] = pygame.mouse.get_pos()
        CAMERA[0] += click[1][0]-click[2][0]
        CAMERA[1] += click[1][1]-click[2][1]
        click[2] = pygame.mouse.get_pos()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = [True,pygame.mouse.get_pos(),pygame.mouse.get_pos()]
            if event.button == 4:
                ZOOM *= 1.1
            elif event.button == 5:
                ZOOM *= 0.9
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                click = [False,[],[]]
