import pygame
import time
import random

# Initialize Pygame
pygame.init()

# Constants
INITIAL_ZOOM = 1.0
INITIAL_CAMERA_POSITION = [0, 0]
RESOLUTION = (800, 800)
MAX_DATA_PACKETS = 500
FPS = 60

# Initialize screen and clock
clock = pygame.time.Clock()
screen = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("Device Network Simulation")

class DataPacket:
    """
    Represents a data packet sent between devices.
    """
    def __init__(self, sender, content, x, y, vx, vy):
        """
        Initializes the DataPacket.

        Args:
            sender (Device): The device sending the packet.
            content (int): The content level of the packet.
            x (float): The x-coordinate of the packet.
            y (float): The y-coordinate of the packet.
            vx (float): The velocity in the x-direction.
            vy (float): The velocity in the y-direction.
        """
        self.sender = sender
        self.content = content
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.received_time = 0
        self.radius = 3

    def mark_as_received(self):
        """
        Marks the data packet as received by recording the current time.
        """
        self.received_time = time.time()

    def draw(self, zoom, camera):
        """
        Draws the data packet on the screen.

        Args:
            zoom (float): The current zoom level.
            camera (list): The current camera position.
        """
        if self.received_time == 0:
            power = min(1, self.content / 10)
            color = [
                255 * (1 - power),
                255 * power,
                0
            ]
            position = [
                self.x * zoom + camera[0],
                self.y * zoom + camera[1]
            ]
            pygame.draw.circle(screen, color, position, max(1, int(self.radius * zoom)))

    def update(self):
        """
        Updates the position of the data packet.

        Returns:
            bool: True if the packet is out of bounds, False otherwise.
        """
        self.x += self.vx
        self.y += self.vy
        return (
            self.x - self.radius > RESOLUTION[0] or
            self.x + self.radius < 0 or
            self.y - self.radius > RESOLUTION[1] or
            self.y + self.radius < 0
        )

class Device:
    """
    Represents a device in the network.
    """
    def __init__(self, x, y):
        """
        Initializes the Device.

        Args:
            x (int): The initial x-coordinate.
            y (int): The initial y-coordinate.
        """
        self.x = x
        self.y = y
        self.vx = (random.random() - 0.5) * 20
        self.vy = (random.random() - 0.5) * 20
        self.send_probability = 1 / 60
        self.radius = 20

    def send_data(self, content, target, speed):
        """
        Creates a DataPacket to send to a target device.

        Args:
            content (int): The content level of the data.
            target (Device): The target device.
            speed (float): The speed at which the data is sent.

        Returns:
            DataPacket: The created data packet.
        """
        vx = ((target.x + target.vx * speed) - self.x) / speed
        vy = ((target.y + target.vy * speed) - self.y) / speed
        return DataPacket(self, content, self.x, self.y, vx, vy)

    def draw(self, zoom, camera):
        """
        Draws the device on the screen.

        Args:
            zoom (float): The current zoom level.
            camera (list): The current camera position.
        """
        color = [100, 100, 100]
        position = [
            self.x * zoom + camera[0],
            self.y * zoom + camera[1]
        ]
        pygame.draw.circle(screen, color, position, max(1, int(self.radius * zoom)))

    def update(self, world):
        """
        Updates the device's position and handles sending data.

        Args:
            world (World): The world containing all devices and data packets.
        """
        self.x += self.vx
        self.y += self.vy

        if random.random() < self.send_probability and len(world.data_packets) < MAX_DATA_PACKETS:
            target_device = world.get_random_device(exclude=self)
            if target_device:
                new_data = self.send_data(content=0, target=target_device, speed=120)
                world.data_packets.append(new_data)

        collided_packets = []
        for packet in world.data_packets:
            if packet.sender != self and packet.received_time == 0:
                distance = ((packet.x - self.x) ** 2 + (packet.y - self.y) ** 2) ** 0.5
                if distance < self.radius + packet.radius:
                    new_content = packet.content + 1
                    new_packet = self.send_data(content=new_content, target=packet.sender, speed=300)
                    world.data_packets.append(new_packet)
                    collided_packets.append(packet)

        for packet in collided_packets:
            world.data_packets.remove(packet)

class World:
    """
    Represents the simulation world containing devices and data packets.
    """
    def __init__(self):
        """
        Initializes the World.
        """
        self.devices = []
        self.data_packets = []

    def get_random_device(self, exclude=None):
        """
        Selects a random device excluding the specified device.

        Args:
            exclude (Device, optional): The device to exclude from selection.

        Returns:
            Device or None: A randomly selected device or None if no other devices exist.
        """
        eligible_devices = [device for device in self.devices if device != exclude]
        if not eligible_devices:
            return None
        return random.choice(eligible_devices)

    def update(self):
        """
        Updates all devices and data packets in the world.
        """
        for device in self.devices:
            device.update(self)

        out_of_bounds_packets = []
        for packet in self.data_packets:
            if packet.update():
                out_of_bounds_packets.append(packet)

        for packet in out_of_bounds_packets:
            self.data_packets.remove(packet)

    def draw(self, zoom, camera):
        """
        Draws all devices and data packets on the screen.

        Args:
            zoom (float): The current zoom level.
            camera (list): The current camera position.
        """
        for device in self.devices:
            device.draw(zoom, camera)
        for packet in self.data_packets:
            packet.draw(zoom, camera)

def main():
    """
    The main function that runs the simulation.
    """
    # Initialize world with devices
    world = World()
    for _ in range(50):
        x = random.randint(50, RESOLUTION[0] - 50)
        y = random.randint(50, RESOLUTION[1] - 50)
        world.devices.append(Device(x, y))

    zoom_level = INITIAL_ZOOM
    camera_position = INITIAL_CAMERA_POSITION.copy()
    is_panning = False
    previous_mouse_pos = (0, 0)

    running = True
    while running:
        clock.tick(FPS)
        screen.fill((0, 0, 0))
        world.update()
        world.draw(zoom_level, camera_position)

        # Handle panning
        if is_panning:
            current_mouse_pos = pygame.mouse.get_pos()
            dx = current_mouse_pos[0] - previous_mouse_pos[0]
            dy = current_mouse_pos[1] - previous_mouse_pos[1]
            camera_position[0] += dx
            camera_position[1] += dy
            previous_mouse_pos = current_mouse_pos

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_panning = True
                    previous_mouse_pos = event.pos
                elif event.button == 4:
                    zoom_level *= 1.1
                elif event.button == 5:
                    zoom_level *= 0.9

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_panning = False

    pygame.quit()

if __name__ == "__main__":
    main()
