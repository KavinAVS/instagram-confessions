#!/usr/bin/env python

# pylint: disable=missing-module-docstring

import logging
import os

from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont  # type: ignore
from PIL.ImageFont import FreeTypeFont  # type: ignore

logging.basicConfig(level="DEBUG")
logger = logging.getLogger(__name__)


def wrap_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    direction: str = "ltr",
) -> str:
    """
    Wraps the text at the given width.

    :param font: Font to use.

    :param text: Text to fit.

    :param max_width: Maximum width of the final text, in pixels.

    :param max_height: Maximum height height of the final text, in pixels.

    :param spacing: The number of pixels between lines.

    :param direction: Direction of the text. It can be 'rtl' (right to
                      left), 'ltr' (left to right) or 'ttb' (top to bottom).
                      Requires libraqm.

    :return: The wrapped text.
    """

    words = text.split()

    lines: list[str] = [""]
    curr_line_width = 0

    for word in words:
        if curr_line_width == 0:
            word_width = font.getlength(word, direction)

            lines[-1] = word
            curr_line_width = word_width
        else:
            new_line_width = font.getlength(f"{lines[-1]} {word}", direction)

            if new_line_width > max_width:
                # Word is too long to fit on the current line
                word_width = font.getlength(word, direction)

                # Put the word on the next line
                lines.append(word)
                curr_line_width = word_width
            else:
                # Put the word on the current line
                lines[-1] = f"{lines[-1]} {word}"
                curr_line_width = new_line_width

    return "\n".join(lines)


# pylint: disable=too-many-arguments
def try_fit_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    max_height: int,
    spacing: int = 4,
    direction: str = "ltr",
) -> Optional[str]:
    """
    Attempts to wrap the text into a rectangle.

    Tries to fit the text into a box using the given font at decreasing sizes,
    based on ``scale_factor``. Makes ``max_iterations`` attempts.

    :param font: Font to use.

    :param text: Text to fit.

    :param max_width: Maximum width of the final text, in pixels.

    :param max_height: Maximum height height of the final text, in pixels.

    :param spacing: The number of pixels between lines.

    :param direction: Direction of the text. It can be 'rtl' (right to
                      left), 'ltr' (left to right) or 'ttb' (top to bottom).
                      Requires libraqm.

    :return: If able to fit the text, the wrapped text. Otherwise, ``None``.
    """

    words = text.split()

    line_height = font.size

    if line_height > max_height:
        # The line height is already too big
        return None

    lines: list[str] = [""]
    curr_line_width = 0

    for word in words:
        if curr_line_width == 0:
            word_width = font.getlength(word, direction)

            if word_width > max_width:
                # Word is longer than max_width
                return None

            lines[-1] = word
            curr_line_width = word_width
        else:
            new_line_width = font.getlength(f"{lines[-1]} {word}", direction)

            if new_line_width > max_width:
                # Word is too long to fit on the current line
                word_width = font.getlength(word, direction)
                new_num_lines = len(lines) + 1
                new_text_height = (new_num_lines * line_height) + (
                    new_num_lines * spacing
                )

                if word_width > max_width or new_text_height > max_height:
                    # Word is longer than max_width, and
                    # adding a new line would make the text too tall
                    return None

                # Put the word on the next line
                lines.append(word)
                curr_line_width = word_width
            else:
                # Put the word on the current line
                lines[-1] = f"{lines[-1]} {word}"
                curr_line_width = new_line_width

    return "\n".join(lines)


# pylint: disable=too-many-arguments
def fit_text(
    font: FreeTypeFont,
    text: str,
    max_width: int,
    max_height: int,
    spacing: int = 4,
    scale_factor: float = 0.8,
    max_iterations: int = 5,
    direction: str = "ltr",
) -> Tuple[FreeTypeFont, str]:
    """
    Automatically determines text wrapping and appropriate font size.

    Tries to fit the text into a box using the given font at decreasing sizes,
    based on ``scale_factor``. Makes ``max_iterations`` attempts.

    If unable to find an appropriate font size within ``max_iterations``
    attempts, wraps the text at the last attempted size.

    :param font: Font to use.

    :param text: Text to fit.

    :param max_width: Maximum width of the final text, in pixels.

    :param max_height: Maximum height height of the final text, in pixels.

    :param spacing: The number of pixels between lines.

    :param scale_factor:

    :param max_iterations: Maximum number of attempts to try to fit the text.

    :param direction: Direction of the text. It can be 'rtl' (right to
                      left), 'ltr' (left to right) or 'ttb' (top to bottom).
                      Requires libraqm.

    :return: The font at the appropriate size and the wrapped text.
    """

    initial_font_size = font.size

    logger.debug('Trying to fit text "%s"', text)

    for i in range(max_iterations):
        trial_font_size = int(initial_font_size * pow(scale_factor, i))
        trial_font = font.font_variant(size=trial_font_size)

        logger.debug("Trying font size %i", trial_font_size)

        wrapped_text = try_fit_text(
            trial_font,
            text,
            max_width,
            max_height,
            spacing,
            direction,
        )

        if wrapped_text:
            logger.debug("Successfully fit text")
            return (trial_font, wrapped_text)

    # Give up and wrap the text at the last size
    logger.debug("Gave up trying to fit text; just wrapping text")
    wrapped_text = wrap_text(trial_font, text, max_width, direction)

    return (trial_font, wrapped_text)


def make_text_image(text, name, post_num, bg_color, filename, width=1024, height=1024) -> None:
    """Generate test images for text auto-wrapping."""

    font = ImageFont.truetype( os.path.join(os.path.dirname(__file__), "fonts/HelveticaNeueLight.ttf"), size=40)
    
    with Image.new(
        mode="RGB", size=(width, height), color=bg_color
    ) as image:
        
        draw = ImageDraw.Draw(image)
        
        msg_height=height-100
        msg_width=width
        
        fontsize, wrapped_text =  fit_text(font, text, msg_width-100, msg_height-100)
        draw.multiline_text(
            xy=( msg_width/2, msg_height/2 ),
            text=wrapped_text,
            fill="black",
            font=fontsize,
            anchor="mm",
            spacing=4,
            align="center",
        )
        
        name_height = 100
        name_width = (width/3)*2
        
        fontsize, wrapped_text =  fit_text(font, name, name_width-50, name_height)
        draw.multiline_text(
            xy=(50, height-(name_height/2) ),
            text=wrapped_text,
            fill="black",
            font=fontsize,
            anchor="lm",
            spacing=4,
            align="center",
        )
        
        post_height = 100
        post_width = width/3
        
        fontsize, wrapped_text =  fit_text(font, post_num, post_width-50, post_height)
        draw.multiline_text(
            xy=( width-50 , height-(post_height/2) ),
            text=wrapped_text,
            fill="black",
            font=fontsize,
            anchor="rm",
            spacing=4,
            align="center",
        )
        
        if not os.path.isdir("./temp"):
            os.makedirs("./temp")
            
        output_path = f'./temp/{filename}.jpg'
        image.save(output_path, "JPEG", quality=100)