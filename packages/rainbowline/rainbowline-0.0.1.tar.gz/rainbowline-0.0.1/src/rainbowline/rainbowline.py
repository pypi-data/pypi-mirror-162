import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


def make_segments(x, y):
    """
    Create list of line segments from x and y coordinates, in the correct format for LineCollection:
    an array of the form   numlines x (points per line) x 2 (x and y) array
    """
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments


def rainbow_line(x, y, c=None, cmap=plt.get_cmap('jet'), norm=None, ax=None, autoscale_view=True, **kwargs):
    """
    Plot a colored line with coordinates x and y.
    Optionally specify colors in the array c.
    Optionally specify a colormap, a norm function and other line kwargs.
    """
    if ax is None:
        ax = plt.gca()  # type: plt.Axes
    # Default colors either by index if present or equally spaced on [0,1]:
    if c is None:
        if hasattr(x, "index") and hasattr(x.index, "__iter__"):
            c = x.index
        elif hasattr(y, "index") and hasattr(y.index, "__iter__"):
            c = y.index
        else:
            c = np.linspace(0.0, 1.0, len(x))
    if norm is None:
        norm = plt.Normalize(np.nanmin(c), np.nanmax(c))
    elif type(norm) in (int, float):
        norm = plt.Normalize(0, norm)
    else:
        try:
            norm = plt.Normalize(*norm)
        except Exception as err:
            raise ValueError(f"Norm value {norm} could not be correctly interpreted.") from err

    c = np.asarray(c)
    segments = make_segments(x, y)
    lc = LineCollection(segments, array=c, cmap=cmap, norm=norm, **kwargs)
    ax.add_collection(lc)
    if autoscale_view:
        ax.autoscale_view()
        ax.relim()
    return lc


if __name__ == "__main__":
    x = np.arange(0, 50, 0.1)
    y = np.sin(x)
    rainbow_line(x, y, c=x)
    rainbow_line(x, y+2, c=y)
    # rainbow_line([0, 1, 2], [2, 10, 50])
    plt.show()
