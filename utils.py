import pygame
from os import getcwd
from os.path import join
from math import pi


text_storage: dict[str, pygame.Surface] = {}
image_storage: dict[str, pygame.Surface] = {}


def get_path(*path: str) -> str:
    return join(getcwd(), *path)


def fetch_text(font: pygame.font.Font, text: str, color=(255, 255, 255)) -> pygame.Surface:
    if text not in text_storage:
        text_storage[text] = font.render(text, True, color)
    return text_storage[text]


def fetch_image(name: str, rot: float = 0) -> pygame.Surface:
    img_name = name
    while rot > pi*2:
        rot -= pi*2
    while rot < 0:
        rot += pi*2
    name = f"{name}|{rot}"
    if name not in image_storage:
        image_storage[name] = pygame.image.load(get_path("assets", img_name)).convert_alpha()
        if rot != 0:
            mod_image = image_storage[f"{img_name}|0"] if image_storage[f"{img_name}|0"] in image_storage else image_storage[name]
            image_storage[name] = pygame.transform.rotate(mod_image, -rot*180/pi)
    return image_storage[name]
