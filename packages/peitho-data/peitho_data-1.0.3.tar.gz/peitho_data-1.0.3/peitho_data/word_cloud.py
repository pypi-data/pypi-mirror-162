import logging

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

logging.basicConfig(level=logging.INFO)


def create_word_cloud_image(
    text: str, output_image_path: str, mask_image_path: str
) -> None:
    """
    Generates a word cloud image.

    :param text:  A string that contains all the words to be counted in word cloud
    :param output_image_path:  Path where word cloud image is to be written
    :param mask_image_path:  Path to mask image
    :return: None
    """
    logging.info(text)

    stopwords = set(STOPWORDS)  # instantiate a word cloud object
    alice_mask = np.array(Image.open(mask_image_path))
    text_wc = WordCloud(
        font_path="peitho_data/Ubuntu-B.ttf",
        background_color="white",
        max_words=2000,
        mask=alice_mask,
        stopwords=stopwords,
    )

    text_wc.generate(text)

    fig = plt.figure()
    fig.set_figwidth(14)
    fig.set_figheight(18)

    plt.imshow(text_wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(output_image_path)


if __name__ == "__main__":
    pass
