import json
import os
from pathlib import Path

from manim import (
    DOWN,
    RIGHT,
    UP,
    Arrow,
    FadeIn,
    GrowArrow,
    LaggedStart,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    config,
)

PAPER = "#f4f0e7"
INK = "#18251f"
GREEN = "#2f6e55"
CORAL = "#dc745c"


class FocuslyDiagram(Scene):
    def construct(self) -> None:
        spec = json.loads(Path(os.environ["FOCUSLY_MANIM_SPEC"]).read_text())
        config.background_color = PAPER

        title = Text(spec["title"], color=INK, font_size=54, weight="BOLD").to_edge(UP)
        circles = VGroup(
            *[
                VGroup(
                    RoundedRectangle(
                        width=3,
                        height=1.35,
                        corner_radius=0.22,
                        stroke_width=0,
                        fill_color=CORAL if index == len(spec["nodes"]) - 1 else GREEN,
                        fill_opacity=1,
                    ),
                    Text(node, color=PAPER, font_size=30, weight="BOLD"),
                )
                for index, node in enumerate(spec["nodes"])
            ]
        ).arrange(RIGHT, buff=1.15)
        circles.move_to(DOWN * 0.2)
        if circles.width > 12:
            circles.scale_to_fit_width(12)
        arrows = VGroup(
            *[
                Arrow(
                    circles[index].get_right(),
                    circles[index + 1].get_left(),
                    color=INK,
                    buff=0.18,
                    stroke_width=7,
                )
                for index in range(len(circles) - 1)
            ]
        )

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.6)
        self.play(LaggedStart(*(FadeIn(node) for node in circles), lag_ratio=0.25), run_time=1.4)
        if len(arrows):
            self.play(LaggedStart(*(GrowArrow(arrow) for arrow in arrows), lag_ratio=0.2))
        self.wait(max(0.1, spec["duration"] - self.time))
