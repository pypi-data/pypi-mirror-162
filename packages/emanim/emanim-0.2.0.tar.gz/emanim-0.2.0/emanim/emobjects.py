from manim import *

class RoundedTriangle(Triangle):
    def __init__(self, corner_radius=0.18, **kwargs):
        super().__init__(**kwargs)
        self.corner_radius = corner_radius
