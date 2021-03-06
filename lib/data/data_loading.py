# Here we add all functions that load info from either local files o internet
from sklearn.datasets import load_files
from keras.utils import np_utils
import numpy as np
from glob import glob
import ee
from pykml import parser
from os import path


def load_images(main_folder_path):
    """

    :param main_folder_path:
    :return:
    """

    # This dict will handle all files references as sklearn.datasets.load_files datasets
    output_dict = {}

    # load train, test, and validation datasets
    train_files, train_targets, train_sklearn_target_names = load_dataset(main_folder_path+'/train')
    valid_files, valid_targets, valid_sklearn_target_names = load_dataset(main_folder_path+'/valid')
    test_files, test_targets, test_sklearn_target_names = load_dataset(main_folder_path+'/test')
    benchmark_files, benchmark_targets, benchmark_sklearn_target_names = load_dataset(main_folder_path + '/benchmark')

    # load list of batch names
    target_names = [item[20:-1] for item in sorted(glob(main_folder_path+"/train/*/"))]

    output_dict['train_files'] = train_files
    output_dict['train_targets'] = train_targets
    output_dict['valid_files'] = valid_files
    output_dict['valid_targets'] = valid_targets
    output_dict['test_files'] = test_files
    output_dict['test_targets'] = test_targets
    output_dict['benchmark_files'] = benchmark_files
    output_dict['benchmark_targets'] = benchmark_targets

    # output_dict will also contain the target names of the categories
    output_dict['target_names'] = target_names

    # Lets print the target names:
    for name in target_names:
        print(name)
    # And the target matrices_
    for target in train_targets:
        print(target)


    return output_dict


# define function to load train, test, and validation datasets
def load_dataset(path):
    data = load_files(path)
    files = np.array(data['filenames'])
    targets = np_utils.to_categorical(np.array(data['target']), 20)
    target_names_sklearn = data['target_names']
    print(target_names_sklearn)
    print(data['target'])
    print(data['target_names'])
    return files, targets, target_names_sklearn


def get_earth_engine_green_cover(poligons):
    """
    Given a set of poligons, we use earth engine to massively get the green cover percentage inside each
    poligon over earth. This will be used to classy images in their respective batch labels.
    :param poligons:
    :return:
    """

    #  If you call ee.Initialize() without any arguments (as the preceding command does), the API tries
    #  to read credentials from a file located in a subfolder of your home directory.
    #  The location of the credentials file depends on your operating system. On Windows, the location is
    # %UserProfile%\.config\earthengine\credentials

    ee.Initialize()

    # After authentication/initialization we iterate over the poligos handled with a pandas data_frame
    # and start getting the tree_cover from the "Hansen Global Forest Change" Earth Engine Satellite collection

    green_cover_output = []

    for p in poligons:
        name = p[0]
        coordinates = p[1]

        # Define a region in the angol region

        geometry = ee.Geometry.Rectangle(coordinates[0], coordinates[1], coordinates[-2], coordinates[-1])

        gfc2014 = ee.Image('UMD/hansen/global_forest_change_2015')
        Image = gfc2014.select(['treecover2000'])

        stats = Image.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=30, bestEffort=True)
        green_cover = stats.getInfo()
        print(green_cover)

        output_tuple = name, green_cover

        green_cover_output.append(output_tuple)

    return green_cover_output


def read_poligons(kml_path):
    """
    Read kml file with the poligon information and return a df with that info

    Example:
        kml_file = path.join('list.kml')

    with open(kml_file) as f:
        doc = parser.parse(f).getroot()

    for e in doc.Document.Folder.Placemark:
        coor = e.Point.coordinates.text.split(',')

    :param path:
    :return:
    """
    kml_file = path.join(kml_path)  # 'forest_growth.kml'

    with open(kml_file) as f:
        doc = parser.parse(f).getroot()

    poligons_list = []

    for e in doc.Document.Folder.Placemark:
        name = e.name
        coordinates = e.Polygon.outerBoundaryIs.LinearRing.coordinates.text.split(',')
        clean_coordinates = []

        # We clean up the coordinates from not numeric data:
        for c in range(8):
            coordinates[c] = coordinates[c].replace('\n\t\t\t\t\t\t\t', '')
            coordinates[c] = coordinates[c].replace('0 ', '')
            clean_coordinates.append(coordinates[c])

        for e in range(len(clean_coordinates)):
            clean_coordinates[e] = float(clean_coordinates[e])

        out_tuple = name, clean_coordinates
        poligons_list.append(out_tuple)
        print out_tuple

    return poligons_list
