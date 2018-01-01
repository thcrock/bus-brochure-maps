from math import floor, ceil
from os import listdir
from os.path import isfile, join
import re
from urllib.request import urlopen, urlretrieve

from bs4 import BeautifulSoup
from wand.image import Image

ROUTE_MAP_DIR = 'images/route'
GRID_MAP_DIR = 'images/grid'

def grab_and_crop_images():
    url = 'http://www.transitchicago.com/travel_information/bus_schedules.aspx'
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    # find all links on the page whose
    # target URLs cotain 'asset.aspx'
    # and texts contain 'Schedule'
    links = soup.find_all('a', href=re.compile('asset.aspx'), text=re.compile('Schedule'))
    for index, link in enumerate(links):
        # download the target URL of the lonk, and load as an image
        file_name, headers = urlretrieve('http://www.transitchicago.com/{}'.format(link['href']))
        img = Image(filename=file_name)
        page = img.sequence[0]

        # lookup cropping dimensions based on the page's width
        crop_lookup = {
            261: {'left': 0, 'top': 60, 'width': int(page.width/1), 'height': int(page.height) - 120},
            504: {'left': int(page.width / 2), 'top': 60, 'width': int(page.width/2), 'height': int(page.height) - 120},
            792: {'left': int(page.width / 3) * 2, 'top': 60, 'width': int(page.width/3), 'height': int(page.height) - 120},
            1008: {'left': int(page.width / 4), 'top': 60, 'width': int(page.width/4), 'height': int(page.height) - 120},
            1050: {'left': int(page.width / 4), 'top': 80, 'width': int(page.width/4), 'height': int(page.height) - 160},
        } 
        # crop, make background white and save!
        page.crop(**(crop_lookup[page.width]))
        page.alpha_channel = False
        new_image = Image(image=page)
        new_image.save(filename='{}/{}.png'.format(
            ROUTE_MAP_DIR,
            str(index).zfill(3)
        ))

def assemble_poster(n_cols):
    # collect the full filename for each file in the output directory
    filenames = [
        join(ROUTE_MAP_DIR, f)
        for f in listdir(ROUTE_MAP_DIR)
        if isfile(join(ROUTE_MAP_DIR, f))
    ]
    n_files = len(filenames)
    # compute number of rows, rounding up so we include all images
    n_rows = ceil(n_files / n_cols)
    # the width and height are given by the first step, i just figured it out manually
    col_width = 252
    row_height = 492

    # precompute the image canvas size
    new_image = Image(height=n_rows*row_height, width=n_cols*col_width)
    for index, filename in enumerate(sorted(filenames)):
        img = Image(filename=filename)
        x_index = (index % n_cols) * col_width
        y_index = floor(index / n_cols) * row_height
        # paste in the individual image at the right slot
        new_image.composite(img, left=x_index, top=y_index)
    new_image.save(filename='{}/{}_cols.png'.format(GRID_MAP_DIR, n_cols))

if __name__ == '__main__':
    grab_and_crop_images()
    assemble_poster(n_cols=22)
