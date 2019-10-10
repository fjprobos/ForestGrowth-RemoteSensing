import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def show_images(files):
    """

    :param files: sklearn loaded files
    :return:
    """
    images = []

    for file in files:
        print(file)
        # load color (BGR) image
        img = mpimg.imread(file)
        # img = cv2.imread(file)
        images.append(img)

        # convert BGR image to RGB for plotting
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # display the image, along with bounding box
        plt.imshow(img)
        plt.show()