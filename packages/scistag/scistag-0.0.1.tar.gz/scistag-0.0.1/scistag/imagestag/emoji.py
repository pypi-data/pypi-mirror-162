import io
from typing import List, Optional
from scistag.common.essential_data import ESSENTIAL_DATA_PATH
from scistag.filestag import FileStag
from scistag.imagestag import Image


class EmojiDb:
    """
    The Emoji DB provides Emoji and country flag graphics.
    By default it uses the Noto Emoji dataset embedded into the SciStag module.
    """

    @classmethod
    def get_emoji_svg(cls, sequence: List[str]) -> Optional[bytes]:
        """
        Tries to read the SVG of an emoji from the database
        :param sequence: The unicode sequence, e.g. ["u1f98c"] for a stag
        :return: The SVG data on success, otherwise None
        """
        lower_cased = [element.lower() for element in sequence]
        combined = "_".join(lower_cased)
        emoji_path = ESSENTIAL_DATA_PATH + f"images/noto/emojis/svg/emoji_{combined}.svg"
        return FileStag.load_file(emoji_path)

    @classmethod
    def render_emoji(cls, sequence: List[str], size=128) -> Optional[Image]:
        """
        Tries to read an emoji and render it to a transparent image
        :param sequence: The unicode sequence, e.g. ["u1f98c"] for a stag
        :param size: The size in pixels in which the emoji shall be rendered
        :return: The SVG data on success, otherwise None
        """
        svg_data = cls.get_emoji_svg(sequence=sequence)
        if not svg_data:
            return None
        import cairosvg
        image_data = io.BytesIO()
        cairosvg.svg2png(svg_data, write_to=image_data, output_width=size, output_height=size)
        return Image(image_data.getvalue())
