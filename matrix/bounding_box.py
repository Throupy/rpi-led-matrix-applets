from dataclasses import dataclass


@dataclass
class BoundingBox:
    # Co-ordinate like structure, always rectangles
    x1: int
    y1: int
    x2: int
    y2: int

    def overlaps(self, other: "BoundingBox") -> bool:
        """Check if this bounding box overlaps with another"""
        # thank god for chatgpt for this one...
        return not (
            self.x2 <= other.x1
            or self.x1 >= other.x2
            or self.y2 <= other.y1
            or self.y1 >= other.y2
        )

    def is_within_screen_bounds(self, width: int, height: int) -> bool:
        """Check if this bounding box is within the matrix bounds (e.g. 64x64)"""
        return self.x1 >= 0 and self.y1 >= 0 and self.x2 <= width and self.y2 <= height
