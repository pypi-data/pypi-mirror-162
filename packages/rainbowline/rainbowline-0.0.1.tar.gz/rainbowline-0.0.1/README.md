# rainbowline

A simple library for plotting lines with color gradients in matplotlib.

![Example plot](example.png)

## Usage
The function ``rainbow_line()`` has the following arguments:
* ``x``: the x values to plot
* ``y``: the y values to plot
* ``c``: the values to map to a color using the specified ``cmap``. If not provided, the index of x or y will be used if possible.
* ``cmap``: (optional) colormap to apply to the ``c`` values. Defaults to 'jet'.
* ``norm``: (optional) normalization for ``c`` values. If not given, the min and max values of ``c`` will be used. One of the following:
  - matplotlib norm object.
  - float or int: in this case, values will be normalized to the range (0, norm)
  - tuple defining the min and max values to which to normalize
* ``ax``: (optional) matplotlib Axes object on  which to plot
* ``autoscale_view``: whether to scale the axes to the extents of the plot. Default True.
* ``**kwargs``: (optional) kwargs which will be passed to matplotlib ``LineCollection`` constructor.