A few conveniences for working with matplotlib.

*Latest release 20220805*:
Initial PyPI release.

## Function `axes(figure=None, ax=None, **fig_kw) -> matplotlib.axes._axes.Axes`

Return a set of `Axes`.

Parameters:
* `figure`: optional `Figure` from which to obtain the `Axes`
  or an `(x,y)` figure size or an `(x,y,dpi)` figure size
* `ax`: optional `Axes` or axes index

If `ax` is already an `Axes` it is returned unchanged.
Otherwise `ax` should be the index of a set of axes,
default `0`.

If `figure` is a `Figure`, `ax` is used to select one of its
sets of axes.

Otherwise a `Figure` is created and a set of axes is selected.
The default figure size comes from `DEFAULT_FIGURE_SIZE` (`(10, 7)`)
and the default dpi comes from `DEFAULT_FIGURE_DPI` (`100`).
The `figure` positional parameter may be supplied
as a 2-tuple `(fig_dx,fig_dy)` to override the default size
or as a 3-tuple `(fig_dx,fig_dy,dpi)` to override the default size and dpi.

## Function `print_figure(figure_or_ax, imgformat=None, file=None)`

Print `figure_or_ax` to a file.

Parameters:
* `figure_or_ax`: a `matplotlib.figure.Figure` or an object
  with a `.figure` attribute such as a set of `Axes`
* `imgformat`: optional output format; if omitted use `'sixel'`
  if `file` is a terminal, otherwise `'png'`
* `file`: the output file, default `sys.stdout`

## Function `remove_decorations(figure_or_ax: Union[matplotlib.figure.Figure, matplotlib.axes._axes.Axes])`

Remove all decorations from a `Figure` or `Axes` instance,
intended for making bare plots such as a tile in GUI.

Presently this removes:
- axes markings and legend from each axis
- the padding from all the figure subplots

## Function `save_figure(figure_or_ax, imgpath: str, force=False)`

Save a `Figure` to the file `imgpath`.

Parameters:
* `figure_or_ax`: a `matplotlib.figure.Figure` or an object
  with a `.figure` attribute such as a set of `Axes`
* `imgpath`: the filesystem path to which to save the image
* `force`: optional flag, default `False`: if true the `imgpath`
  will be written to even if it exists

## Function `saved_figure(figure_or_ax, dir=None, ext=None)`

Context manager to save a `Figure` to a file and yield the file path.

Parameters:
* `figure_or_ax`: a `matplotlib.figure.Figure` or an object
  with a `.figure` attribute such as a set of `Axes`
* `dir`: passed to `tempfile.TemporaryDirectory`
* `ext`: optional file extension, default `'png'`

# Release Log



*Release 20220805*:
Initial PyPI release.
