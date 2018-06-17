#!/usr/bin/python

from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
from scipy import optimize
import numpy as np
import math
import os
import sys
import re
import time
plt.rcParams["font.family"] = "monospace"


# Natural sorting for correct file order
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def parse_rectangles(input_dir):
    # List and order files in input_dir
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    files = natural_sort(files)
    # Initialize rectangle dict with list of None
    rectangles = defaultdict(lambda: [None] * len(files))
    for t, file in enumerate(files):
        f = open(file, "r")
        lines = f.read().split('\n')
        for line in lines:
            if line != '':
                # Save tuple (x, y, w, h) in dict whenever a rectangle is present in a revision
                id, x, y, w, h = line.split(',')
                rectangles[id][t] = (float(x), float(y), float(w), float(h))
    return rectangles, len(files)


# Metric definition
def point_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def corner_travel(t1, t2):
    x1, y1, w1, h1 = t1
    x2, y2, w2, h2 = t2
    if math.isnan(w1):
        # 2 times the hypotenuse -- growth from center
        return 2 * math.sqrt(w2 ** 2 + h2 ** 2)
    elif math.isnan(w2):
        return 2 * math.sqrt(w1 ** 2 + h1 ** 2)
    else:
        return point_distance(x1, y1, x2, y2) \
               + point_distance(x1 + w1, y1, x2 + w2, y2) \
               + point_distance(x1, y1 + h1, x2, y2 + h2) \
               + point_distance(x1 + w1, y1 + h1, x2 + w2, y2 + h2)


# def delta_vis(df1, df2):
#     base_width = (df1['x'] + df1['w']).max()
#     base_height = (df1['y'] + df1['h']).max()
#     # Normalize by 4 * hypotenuse
#     #norm = 4 * math.sqrt(base_width ** 2 + base_height ** 2)
#
#     df = pd.merge(df1, df2, how='inner', left_index=True, right_index=True)
#     df.columns = ['x1', 'y1', 'w1', 'h1', 'x2', 'y2', 'w2', 'h2']
#     df['delta_vis'] = df.apply(lambda r: corner_travel(*list(r)), axis=1)
#     return df[['delta_vis']]


def point_hyperbole_dist(x, w, h, a):
    # Distance between a point (w,h) and a hyperbole y = a/4x where a is the area we are trying to reach
    return math.sqrt((x - w / 2) ** 2 + (a / (4 * x) - h / 2) ** 2)


def unavoidable_travel(t1, t2):
    x1, y1, w1, h1 = t1
    x2, y2, w2, h2 = t2
    if h1 * w1 - w2 * h2 < 0.00001:
        return 0
    else:
        result = optimize.minimize(point_hyperbole_dist, x0=w1, args=(w1, h1, w2 * h2))
        optimum_x = result.x[0]
        # Minimum corner travel is 4 times the minimum point-hyperbole distance
        return point_hyperbole_dist(optimum_x, w1, h1, w2 * h2) * 4


def get_color(t1, t2):
    global cmap
    if t1 is None or t2 is None:
        return cmap(0.0)
    else:
        # Compute metric value
        norm = 4 * math.sqrt(1000 ** 2 + 1000 ** 2)
        metric_value = (corner_travel(t1, t2) - unavoidable_travel(t1, t2)) / norm
        return cmap(metric_value)


# Crude drawing of the treemap
def draw(rectangle_dict, t):
    # All parameters that control the animation
    global dataset_id, output_name

    revision = math.floor(t)

    fig, ax = plt.subplots(1)
    ax.set_xlim(1000)
    ax.set_ylim(1000)
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    ax.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
    ax.set_aspect('equal', adjustable='box')
    ax.invert_xaxis()
    plt.suptitle(output_name + "-" + str(int(revision)))

    im = plt.imshow([np.arange(0, 1.1, 0.1), np.arange(0, 1.1, 0.1)], cmap=cm.get_cmap('viridis'))
    plt.colorbar(im, cmap=cm.get_cmap('viridis'))


    # fig.suptitle(("SQR - exo - Revision " + str(revision - 1) if revision > 0 else "SQR - exo - Revision 0"))
    ax.cla()  # Clear primitives (Artists) from Axes

    patch_list = []
    step = t - math.floor(t)
    for key in rectangle_dict:
        item = rectangle_dict[key]
        # if revision == 0 and item[revision] is not None:
        #     xB, yB, wB, hB = item[revision]
        #     xA = xB + wB / 2
        #     yA = yB + hB / 2
        #     hA = wA = 0
        if item[revision] is not None \
                and item[revision + 1] is not None:
            xA, yA, wA, hA = item[revision]
            xB, yB, wB, hB = item[revision + 1]

        elif item[revision] is None \
                and item[revision + 1] is not None:
            xB, yB, wB, hB = item[revision + 1]
            xA = xB + wB / 2
            yA = yB + hB / 2
            hA = wA = 0

        elif item[revision] is not None \
                and item[revision + 1] is None:
            xA, yA, wA, hA = item[revision]
            xB = xA + wA / 2
            yB = yA + hA / 2
            hB = wB = 0

        else:
            continue

        # Revision weighting for movement
        x = xA * (1 - step) + xB * step
        y = yA * (1 - step) + yB * step
        w = wA * (1 - step) + wB * step
        h = hA * (1 - step) + hB * step

        # Add text to cell
        # ax.text(x + 3, y + 30, key, color='white', fontsize=5)

        # To color rectangles we are looking back -- use last color on stop
        if revision > 0:
            if t - math.floor(t) > 0:
                prev_rect = item[revision]
                current_rect = item[revision + 1]
            else:
                prev_rect = item[revision - 1]
                current_rect = item[revision]
        else:
            prev_rect = current_rect = None

        color = get_color(prev_rect, current_rect)

        # Add patch to collection
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='#eff0f1', fc=color)
        patch_list.append(rect)

    p = PatchCollection(patch_list, match_original=True)
    ax.add_collection(p)


    fig.canvas.draw()
    fig.canvas.flush_events()
    # Multiple saves on revision change
    if t - math.floor(t) == 0:
        save_fig(5)
    else:
        save_fig(1)
    plt.close(fig)


def save_fig(n=1):
    global fig_n
    for i in range(n):
        plt.savefig(output_path + str(fig_n) + '.png')
        fig_n += 1


# Read rectangles and initialize
output_path = 'ts_' + str(int(time.time())) + '/'

os.makedirs(output_path, exist_ok=True)
os.makedirs('videos', exist_ok=True)

fig_n = 0
cmap = cm.get_cmap('viridis')
input_dir = sys.argv[1]
max_revisions = None
if len(sys.argv) > 2:
    max_revisions = sys.argv[2]

output_name = input_dir.split('/')[-2] + '-' + input_dir.split('/')[-1]
rectangle_dict, n_revisions = parse_rectangles(input_dir)


for t in np.arange(0, n_revisions - 1, 0.05):
    draw(rectangle_dict, t)
    if max_revisions is not None and t > int(max_revisions):
        break

# Copy frame names to a txt file
os.chdir(output_path)
os.system('ls | grep .*.png | sort -V > order.txt')
# Turn frames into mkv video
os.system(
    'mencoder mf://@order.txt -mf fps=10:type=png -ovc x264 -x264encopts bitrate=1200:threads=2 -o ../videos/'
    + output_name + '-' + str(n_revisions) + '.mp4')
# Delete png frames
os.system('rm -rf ../' + output_path)
sys.exit()

# Copy frame names to a txt file
# os.system('ls | grep ' + output_path + '.*.png | sort -V > ' + output_path + '.txt')
# # Turn frames into mkv video
# os.system('mencoder mf://@' + output_path + '.txt' + ' -mf fps=10:type=png -ovc x264 -x264encopts bitrate=1200:threads=2 -o ' + output_path + '.mp4')
# # Delete png frames
# os.system('xargs rm < ' + output_path + '.txt')
# os.system('rm ' + output_path + '.txt')
# sys.exit()