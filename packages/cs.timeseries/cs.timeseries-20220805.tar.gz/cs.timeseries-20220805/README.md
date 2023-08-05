Efficient portable machine native columnar storage of time series data
for double float and signed 64-bit integers.

*Latest release 20220805*:
* Rename @plotrange to @timerange since it is not inherently associated with plotting, support both methods and functions.
* print_figure, save_figure and saved_figure now moved to cs.mplutils.
* plot_events: use the utcoffset parameter.
* TimeSeriesBaseCommand.cmd_plot: new --bare option for unadorned plots.

The core purpose is to provide time series data storage; there
are assorted convenience methods to export arbitrary subsets
of the data for use by other libraries in common forms, such
as dataframes or series, numpy arrays and simple lists.
There are also some simple plot methods for plotting graphs.

Three levels of storage are defined here:
- `TimeSeriesFile`: a single file containing a binary list of
  float64 or signed int64 values
- `TimeSeriesPartitioned`: a directory containing multiple
  `TimeSeriesFile` files, each covering a separate time span
  according to a supplied policy, for example a calendar month
- `TimeSeriesDataDir`: a directory containing multiple
  `TimeSeriesPartitioned` subdirectories, each for a different
  time series, for example one subdirectory for grid voltage
  and another for grid power

Together these provide a hierarchy for finite sized files storing
unbounded time series data for multiple parameters.

On a personal basis, I use this as efficient storage of time
series data from my solar inverter, which reports in a slightly
clunky time limited CSV format; I import those CSVs into
time series data directories which contain the overall accrued
data; see my `cs.splink` module which is built on this module.

## Function `array_byteswapped(ary)`

Context manager to byteswap the `array.array` `ary` temporarily.

## Class `ArrowBasedTimespanPolicy(TimespanPolicy, icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A `TimespanPolicy` based on an Arrow format string.

See the `raw_edges` method for the specifics of how these are defined.

*Method `ArrowBasedTimespanPolicy.Arrow(self, when)`*:
Return an `arrow.Arrow` instance for the UNIX time `when`
in the policy timezone.

*Method `ArrowBasedTimespanPolicy.make(name, partition_format, shift)`*:
Create and register a simple `ArrowBasedTimespanPolicy`.
Return the new policy.

Parameters:
* `name`: the name for the policy; this can also be a sequence of names
* `partition_format`: the Arrow format string for naming time partitions
* `shift`: a mapping of parameter values for `Arrow.shift()`
  defining the time step from one partition to the next

*Method `ArrowBasedTimespanPolicy.name_for_time(self, when)`*:
Return a time span name for the UNIX time `when`.

*Method `ArrowBasedTimespanPolicy.partition_format_cononical(self, txt)`*:
Modify the formatted text derived from `self.PARTITION_FORMAT`.

The driving example is the 'weekly' policy, which uses
Arrow's 'W' ISO week format but trims the sub-week day
suffix.  This is sufficient if Arrow can parse the trimmed
result, which it can for 'W'. If not, a subclass might need
to override this method.

*Method `ArrowBasedTimespanPolicy.raw_edges(self, when: Union[int, float])`*:
Return the _raw_ start and end UNIX times
(inclusive and exclusive respectively)
bracketing the UNIX time `when`.

This implementation performs the following steps:
* get an `Arrow` instance in the policy timezone from the
  UNIX time `when`
* format that instance using `self.PARTITION_FORMAT`,
  modified by `self.partition_format_cononical`
* parse that string into a new `Arrow` instance which is
  the raw start time
* compute the raw end time as `calendar_start.shift(**self.ARROW_SHIFT_PARAMS)`
* return the UNIX timestamps for the raw start and end times

*Method `ArrowBasedTimespanPolicy.span_for_name(self, *a, **kw)`*:
Return a `TimePartition` derived from the `span_name`.

## Function `as_datetime64s(times, unit='s')`

Return a Numpy array of `datetime64` values
computed from an iterable of `int`/`float` UNIX timestamp values.

The optional `unit` parameter (default `'s'`) may be one of:
- `'s'`: seconds
- `'ms'`: milliseconds
- `'us'`: microseconds
- `'ns'`: nanoseconds
and represents the precision to preserve in the source time
when converting to a `datetime64`.
Less precision gives greater time range.

## Function `datetime64_as_timestamp(dt64: numpy.datetime64)`

Return the UNIX timestamp for the `datetime64` value `dt64`.

## Function `deduce_type_bigendianness(typecode: str) -> bool`

Deduce the native endianness for `typecode`,
an array/struct typecode character.

## Class `Epoch(Epoch, builtins.tuple, TimeStepsMixin)`

The basis of time references with a starting UNIX time `start`
and the `step` defining the width of a time slot.

*Method `Epoch.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `Epoch`, handy for use with `pformat()` or `pprint()`.

*Method `Epoch.promote(epochy)`*:
Promote `epochy` to an `Epoch` (except for `None`).

`None` remains `None`.

An `Epoch` remains unchanged.

An `int` or `float` argument will be used as the `step` in
an `Epoch` starting at `0`.

A 2-tuple of `(start,step)` will be used to construct a new `Epoch` directly.

*Property `Epoch.typecode`*:
The `array` typecode for the times from this `Epoch`.

## Function `get_default_timezone_name()`

Return the default timezone name.

## Class `HasEpochMixin(TimeStepsMixin)`

A `TimeStepsMixin` with `.start` and `.step` derive from `self.epoch`.

*Method `HasEpochMixin.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `HasEpochMixin`, handy for use with `pformat()` or `pprint()`.

*Property `HasEpochMixin.start`*:
The start UNIX time from `self.epoch.start`.

*Property `HasEpochMixin.step`*:
The time slot width from `self.epoch.step`.

*Property `HasEpochMixin.time_typecode`*:
The `array` typecode for times from `self.epoch`.

## Function `main(argv=None)`

Run the command line tool for `TimeSeries` data.

## Function `plot_events(*a, tz: Optional[datetime.tzinfo] = None, utcoffset: Union[int, float, NoneType] = None, **kw)`

Plot `events`, an iterable of objects with `.unixtime`
attributes such as an `SQLTagSet`.
Return the `Axes` on which the plot was made.

Parameters:
* `events`: an iterable of objects with `.unixtime` attributes
* `value_func`: a callable to compute the y-axis value from an event
* `start`: optional start UNIX time, used to crop the events plotted
* `stop`: optional stop UNIX time, used to crop the events plotted
* `figure`,`ax`: optional arguments as for `cs.mplutils.axes`
* `utcoffset`: optional UTC offset for presentation
Other keyword parameters are passed to `Axes.scatter`.

## Class `TimePartition(TimePartition, builtins.tuple, TimeStepsMixin)`

A `namedtuple` for a slice of time with the following attributes:
* `epoch`: the reference `Epoch`
* `name`: the name for this slice
* `start_offset`: the epoch offset of the start time (`self.start`)
* `end_offset`: the epoch offset of the end time (`self.stop`)

These are used by `TimespanPolicy` instances to express the partitions
into which they divide time.

*Method `TimePartition.__contains__(self, when: Union[int, float]) -> bool`*:
Test whether the UNIX timestamp `when` lies in this partition.

*Method `TimePartition.__iter__(self)`*:
A generator yielding times from this partition from
`self.start` to `self.stop` by `self.step`.

*Method `TimePartition.offsets(self)`*:
Return an iterable of the epoch offsets from `self.start` to `self.stop`.

*Property `TimePartition.start`*:
The start UNIX time derived from `self.epoch` and `self.start_offset`.

*Property `TimePartition.step`*:
The epoch step size.

*Property `TimePartition.stop`*:
The end UNIX time derived from `self.epoch` and `self.end_offset`.

## Function `timerange(*da, **dkw)`

A decorator intended for plotting functions or methods which
presents optional `start` and `stop` leading positional
parameters and optional `tz` or `utcoffset` keyword parameters.
The decorated function will be called with leading `start`
and `stop` positional parameters and a specific `utcoffset`
keyword parameter.

The as-decorated function is called with the following parameters:
* `start`: an optional UNIX timestamp positional for the
  start of the range; if omitted the default is `self.start`;
  this is a required parameter if the decorator has `needs_start=True`
* `stop`: an optional UNIX timestamp positional parameter for the end
  of the range; if omitted the default is `self.stop`;
  this is a required parameter if the decorator has `needs_stop=True`
* `tz`: optional timezone `datetime.tzinfo` object or
  specification as for `tzfor()`;
  this is used to infer a UTC offset in seconds
* `utcoffset`: an optional offset from UTC time in seconds
Other parameters are passed through to the deocrated function.

A decorated *method* is then called as:

    method(self, start, stop, *a, utcoffset=utcoffset, **kw)

where `*a` and `**kw` are the additional positional and keyword
parameters respectively, if any.

A decorated *function* is called as:

    function(start, stop, *a, utcoffset=utcoffset, **kw)

The `utcoffset` is an offset to apply to UTC-based time data
for _presentation_ on the graph, largely because the plotting
functions use `DataFrame.plot` which broadly ignores attempts
to set locators or formatters because it supplies its own.
The plotting function would shift the values of the `DataFrame`
index using this value.

If neither `utcoffset` or `tz` is supplied by the caller, the
`utcoffset` is `0.0`.
A specified `utcoffset` is passed through.
A `tz` is promoted to a `tzinfo` instance via the `tzfor()`
function and applied to the `stop` timestamp to obtain a
`datetime` from which the `utcoffset` will be derived.
It is an error to specify both `utcoffset` and `tz`.

## Class `TimeSeries(cs.resources.MultiOpenMixin, cs.context.ContextManagerMixin, HasEpochMixin, TimeStepsMixin)`

Common base class of any time series.

*Method `TimeSeries.__getitem__(self, index)`*:
Return a datum or list of data.

*Method `TimeSeries.as_np_array(*a, **kw)`*:
Return a `numpy.array` 1xN array containing the data from `start` to `stop`,
default from `self.start` and `self.stop` respectively.

*Method `TimeSeries.as_pd_series(*a, **kw)`*:
Return a `pandas.Series` containing the data from `start` to `stop`,
default from `self.start` and `self.stop` respectively.

*Property `TimeSeries.csv_header`*:
The value of the `csv.header` tag for this `TimeSeries`, or `None`.

*Method `TimeSeries.data(self, start, stop)`*:
Return an iterable of `(when,datum)` tuples for each time `when`
from `start` to `stop`.

*Method `TimeSeries.data2(self, start, stop)`*:
Like `data(start,stop)` but returning 2 lists: one of time and one of data.

*Method `TimeSeries.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `TimeSeries`, handy for use with `pformat()` or `pprint()`.

*Property `TimeSeries.np_type`*:
The `numpy` type corresponding to `self.typecode`.

*Method `TimeSeries.offset_slice(self, astart: int, astop: int, pad=False, prepad=False)`*:
Return a slice of the underlying array
for the array indices `astart:astop`.

If `astop` implies values beyond the end of the array
and `pad` is true, pad the resulting list with `self.fill`
to the expected length.

If `astart` is an offset before the start of the array
raise an `IndexError` unless `prepad` is true,
in which case the list of values will be prepended
with enough of `self.fill` to reach the array start.

*Method `TimeSeries.plot(*a, tz: Optional[datetime.tzinfo] = None, utcoffset: Union[int, float, NoneType] = None, **kw)`*:
Convenience shim for `DataFrame.plot` to plot data from
`start` to `stop`.  Return the plot `Axes`.

Parameters:
* `start`,`stop`: the time range
* `label`: optional label for the graph
* `runstate`: optional `RunState`, ignored in this implementation
* `utcoffset`: optional timestamp skew from UTC in seconds
* `figure`,`ax`: optional arguments as for `cs.mplutils.axes`
Other keyword parameters are passed to `DataFrame.plot`.

*Method `TimeSeries.slice(self, start, stop, pad=False, prepad=False)`*:
Return a slice of the underlying array
for the times `start:stop`.

If `stop` implies values beyond the end of the array
and `pad` is true, pad the resulting list with `self.fill`
to the expected length.

If `start` corresponds to an offset before the start of the array
raise an `IndexError` unless `prepad` is true,
in which case the list of values will be prepended
with enough of `self.fill` to reach the array start.

*Method `TimeSeries.startup_shutdown(self)`*:
This is required, even if empty.

*Method `TimeSeries.update_tag(self, tag_name, new_tag_value)`*:
Update tag with new value.

## Function `timeseries_from_path(tspath: str, epoch: Union[cs.timeseries.Epoch, Tuple[Union[int, float], Union[int, float]], int, float, NoneType] = None, typecode=None)`

Turn a time series filesystem path into a time series:
* a file: a `TimeSeriesFile`
* a directory holding `.csts` files: a `TimeSeriesPartitioned`
* a directory: a `TimeSeriesDataDir`

## Class `TimeSeriesBaseCommand(cs.cmdutils.BaseCommand)`

Abstract base class for command line interfaces to `TimeSeries` data files.

Command line usage:

    Usage: timeseriesbase subcommand [...]
      Subcommands:
        fetch ...
          Fetch raw data files from the primary source to a local spool.
          To be implemented in subclasses.
        help [-l] [subcommand-names...]
          Print the full help for the named subcommands,
          or for all subcommands if no names are specified.
          -l  Long help even if no subcommand-names provided.
        import ...
          Import data into the time series.
          To be implemented in subclasses.
        info
          Report information.
        plot [-f] [-o imgpath.png] [--show] [--tz tzspec] start-time [stop-time] [{glob|fields}...]
          Plot the data from specified fields for the specified time range.
          Options:
            --bare          Strip axes and padding from the plot.
            -f              Force. -o will overwrite an existing image file.
            -o imgpath.png  File system path to which to save the plot.
            --show          Show the image in the GUI.
            --tz tzspec     Skew the UTC times presented on the graph
                            The default skew is 0 i.e. UTC.
                            to emulate the timezone specified by tzspec.
            --stacked       Stack the plot lines/areas.
            start-time      An integer number of days before the current time
                            or any datetime specification recognised by
                            dateutil.parser.parse.
            stop-time       Optional stop time, default now.
                            An integer number of days before the current time
                            or any datetime specification recognised by
                            dateutil.parser.parse.
            glob|fields     If glob is supplied, constrain the keys of
                            a TimeSeriesDataDir by the glob.

*Method `TimeSeriesBaseCommand.cmd_fetch(self, argv)`*:
Usage: {cmd} ...
Fetch raw data files from the primary source to a local spool.
To be implemented in subclasses.

*Method `TimeSeriesBaseCommand.cmd_import(self, argv)`*:
Usage: {cmd} ...
Import data into the time series.
To be implemented in subclasses.

*Method `TimeSeriesBaseCommand.cmd_info(self, argv)`*:
Usage: {cmd}
Report information.

*Method `TimeSeriesBaseCommand.cmd_plot(self, argv)`*:
Usage: {cmd} [-f] [-o imgpath.png] [--show] [--tz tzspec] start-time [stop-time] [{{glob|fields}}...]
Plot the data from specified fields for the specified time range.
Options:
  --bare          Strip axes and padding from the plot.
  -f              Force. -o will overwrite an existing image file.
  -o imgpath.png  File system path to which to save the plot.
  --show          Show the image in the GUI.
  --tz tzspec     Skew the UTC times presented on the graph
                  The default skew is 0 i.e. UTC.
                  to emulate the timezone specified by tzspec.
  --stacked       Stack the plot lines/areas.
  start-time      An integer number of days before the current time
                  or any datetime specification recognised by
                  dateutil.parser.parse.
  stop-time       Optional stop time, default now.
                  An integer number of days before the current time
                  or any datetime specification recognised by
                  dateutil.parser.parse.
  glob|fields     If glob is supplied, constrain the keys of
                  a TimeSeriesDataDir by the glob.

*Method `TimeSeriesBaseCommand.parsetime(timespec: str) -> float`*:
Parse `timespec` into a UNIX timestamp.
`timespec` may be one of the following:
* an integer number of days, indicating a time before _now_
* a float, an absolute UNIX timestamp in seconds
* any format recognised by `dateutil.parser.parse`, assuming the
  system local time if no timezone is specified in `timespec`.

*Method `TimeSeriesBaseCommand.poptime(self, argv: List[str], argname: str = 'timespec', **kw)`*:
Pop a _days_ or _timespec_ argument from the command line,
return an aware `datetime`.

## Class `TimeSeriesCommand(TimeSeriesBaseCommand, cs.cmdutils.BaseCommand)`

Command line interface to `TimeSeries` data files.

Command line usage:

    Usage: timeseries [-s ts-step] tspath subcommand...
        -s ts-step  Specify the UNIX time step for the time series,
                    used if the time series is new and checked otherwise.
        tspath      The filesystem path to the time series;
                    this may refer to a single .csts TimeSeriesFile, a
                    TimeSeriesPartitioned directory of such files, or
                    a TimeSeriesDataDir containing partitions for
                    multiple keys.
      Subcommands:
        dump
          Dump the contents of tspath.
        fetch ...
          Fetch raw data files from the primary source to a local spool.
          To be implemented in subclasses.
        help [-l] [subcommand-names...]
          Print the full help for the named subcommands,
          or for all subcommands if no names are specified.
          -l  Long help even if no subcommand-names provided.
        import csvpath datecol[:conv] [import_columns...]
          Import data into the time series.
          csvpath   The CSV file to import.
          datecol[:conv]
                    Specify the timestamp column and optional
                    conversion function.
                    "datecol" can be either the column header name
                    or a numeric column index counting from 0.
                    If "conv" is omitted, the column should contain
                    a UNIX seconds timestamp.  Otherwise "conv"
                    should be either an identifier naming one of
                    the known conversion functions or an "arrow.get"
                    compatible time format string.
          import_columns
                    An optional list of column names or their derived
                    attribute names. The default is to import every
                    numeric column except for the datecol.
        info
          Report infomation about the time series stored at tspath.
        plot [-f] [-o imgpath.png] [--show] [--tz tzspec] start-time [stop-time] [{glob|fields}...]
          Plot the data from specified fields for the specified time range.
          Options:
            --bare          Strip axes and padding from the plot.
            -f              Force. -o will overwrite an existing image file.
            -o imgpath.png  File system path to which to save the plot.
            --show          Show the image in the GUI.
            --tz tzspec     Skew the UTC times presented on the graph
                            The default skew is 0 i.e. UTC.
                            to emulate the timezone specified by tzspec.
            --stacked       Stack the plot lines/areas.
            start-time      An integer number of days before the current time
                            or any datetime specification recognised by
                            dateutil.parser.parse.
            stop-time       Optional stop time, default now.
                            An integer number of days before the current time
                            or any datetime specification recognised by
                            dateutil.parser.parse.
            glob|fields     If glob is supplied, constrain the keys of
                            a TimeSeriesDataDir by the glob.
        test [testnames...]
          Run some tests of functionality.

*Method `TimeSeriesCommand.apply_preargv(self, argv)`*:
Parse a leading time series filesystem path from `argv`,
set `self.options.ts` to the time series,
return modified `argv`.

*Method `TimeSeriesCommand.cmd_dump(self, argv)`*:
Usage: {cmd}
Dump the contents of tspath.

*Method `TimeSeriesCommand.cmd_import(self, argv)`*:
Usage: {cmd} csvpath datecol[:conv] [import_columns...]
Import data into the time series.
csvpath   The CSV file to import.
datecol[:conv]
          Specify the timestamp column and optional
          conversion function.
          "datecol" can be either the column header name
          or a numeric column index counting from 0.
          If "conv" is omitted, the column should contain
          a UNIX seconds timestamp.  Otherwise "conv"
          should be either an identifier naming one of
          the known conversion functions or an "arrow.get"
          compatible time format string.
import_columns
          An optional list of column names or their derived
          attribute names. The default is to import every
          numeric column except for the datecol.

*Method `TimeSeriesCommand.cmd_info(self, argv)`*:
Usage: {cmd}
Report infomation about the time series stored at tspath.

*Method `TimeSeriesCommand.cmd_test(self, argv)`*:
Usage: {cmd} [testnames...]
Run some tests of functionality.

## Class `TimeSeriesDataDir(TimeSeriesMapping, builtins.dict, cs.resources.MultiOpenMixin, cs.context.ContextManagerMixin, cs.fs.HasFSPath, cs.configutils.HasConfigIni, HasEpochMixin, TimeStepsMixin)`

A directory containing a collection of `TimeSeriesPartitioned` subdirectories.

*Method `TimeSeriesDataDir.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `TimeSeriesDataDir`, handy for use with `pformat()` or `pprint()`.

*Method `TimeSeriesDataDir.keys(self, fnglobs: Union[str, List[str], NoneType] = None)`*:
Return a list of the known keys, derived from the subdirectories,
optionally constrained by `fnglobs`.
If provided, `fnglobs` may be a glob string or list of glob strings
suitable for `fnmatch`.

*Method `TimeSeriesDataDir.make_ts(self, key)`*:
Create a `TimeSeriesPartitioned` for `key`.

*Property `TimeSeriesDataDir.policy_name`*:
The `policy.name` config value, usually a key from
`TimespanPolicy.FACTORIES`.

*Method `TimeSeriesDataDir.shortname(self)`*:
Return `self.shortpath`.

*Method `TimeSeriesDataDir.startup_shutdown(self)`*:
Context manager for `MultiOpenMixin`.
Close the sub time series and save the config if modified.

*Property `TimeSeriesDataDir.tz`*:
The `policy.tz` config value, a timezone name.

## Class `TimeSeriesFile(TimeSeries, cs.resources.MultiOpenMixin, cs.context.ContextManagerMixin, HasEpochMixin, TimeStepsMixin, cs.fs.HasFSPath)`

A file containing a single time series for a single data field.

This provides easy access to a time series data file.
The instance can be indexed by UNIX time stamp for time based access
or its `.array` property can be accessed for the raw data.

The data file itself has a header indicating the file data big endianness,
the datum type and the time type (both `array.array` type codes).
Following these are the start and step sizes in the time type format.
This is automatically honoured on load and save.

A new file will use the native endianness, but files of other
endianness are correctly handled, making a `TimeSeriesFile`
portable between architectures.

Read only users can just instantiate an instance and access
its `.array` property, or use the `peek` and `peek_offset` methods.

Read/write users should use the instance as a context manager,
which will automatically update the file with the array data
on exit:

    with TimeSeriesFile(fspath) as ts:
        ... work with ts here ...

Note that the save-on-close is done with `TimeSeries.flush()`
which only saves if `self.modified`.
Use of the `__setitem__` or `pad_to` methods set this flag automatically.
Direct access via the `.array` will not set it,
so users working that way for performance should update the flag themselves.

A `TimeSeriesFile` has two underlying modes of operation:
in-memory `array.array` mode and direct-to-file `mmap` mode.

The in-memory mode reads the whole file into an `array.array` instance,
and all updates then modify the in-memory `array`.
The file is saved when the context manager exits or when `.save()` is called.
This maximises efficiency when many accesses are done.

The `mmap` mode maps the file into memory, and accesses operate
directly against the file contents.
This is more efficient for just a few accesses,
but every "write" access (setting a datum) will make the mmapped page dirty,
causing the OS to queue it for disc.
This mode is recommended for small accesses
such as updating a single datum, eg from polling a data source.

Presently the mode used is triggered by the access method.
Using the `peek` and `poke` methods uses `mmap` by default.
Other accesses default to use the in-memory mode.
Access to the `.array` property forces use of the `array` mode.
Poll/update operations should usually choose to use `peek`/`poke`.

*Method `TimeSeriesFile.__init__(self, *a, **kw)`*:
Prepare a new time series stored in the file at `fspath`
containing machine native data for the time series values.

Parameters:
* `fspath`: the filename of the data file
* `typecode` optional expected `array.typecode` value of the data;
  if specified and the data file exists, they must match;
  if not specified then the data file must exist
  and the `typecode` will be obtained from its header
* `epoch`: optional `Epoch` specifying the start time and
  step size for the time series data in the file;
  if specified and the data file exists, they must match;
  if not specified then the data file must exist
  and the `epoch` will be obtained from its header
* `fill`: optional default fill values for `pad_to`;
  if unspecified, fill with `0` for `'q'`
  and `float('nan')` for `'d'`

*Method `TimeSeriesFile.__getitem__(self, when: Union[int, float, slice])`*:
Return the datum for the UNIX time `when`.

If `when` is a slice, return a list of the data
for the times in the range `start:stop`
as given by `self.range(start,stop)`.
This will raise an `IndexError` if `start` corresponds to
an offset before the beginning of the array.

*Method `TimeSeriesFile.__setitem__(self, when, value)`*:
Set the datum for the UNIX time `when`.

*Property `TimeSeriesFile.array`*:
The time series as an `array.array` object.
This loads the array data from `self.fspath` on first use.

*Method `TimeSeriesFile.array_index(self, when) -> int`*:
Return the array index corresponding the time UNIX time `when`.

*Method `TimeSeriesFile.array_index_bounds(self, start, stop) -> (<class 'int'>, <class 'int'>)`*:
Return a `(array_start,array_stop)` pair for the array indices
between the UNIX times `start` and `stop`.

Example:

   >>> ts = TimeSeriesFile('tsfile.csts', 'd', epoch=(19.1, 1.2))
   >>> ts.array_index_bounds(20,30)
   (0, 9)

*Method `TimeSeriesFile.array_indices(self, start, stop)`*:
Return an iterable of the array indices for the UNIX times
from `start` to `stop` from this `TimeSeries`.

Example:

   >>> ts = TimeSeriesFile('tsfile.csts', 'd', epoch=(19.1, 1.2))
   >>> list(ts.array_indices(20,30))
   [0, 1, 2, 3, 4, 5, 6, 7, 8]

*Method `TimeSeriesFile.array_length(self)`*:
The length of the time series data,
from `len(self.array)`.

*Method `TimeSeriesFile.file_offset(self, offset: int) -> int`*:
Return the file position for the data with position `offset`.

*Method `TimeSeriesFile.flush(self, keep_array=False)`*:
Save the data file if `self.modified`.

*Method `TimeSeriesFile.index_when(self, index: int)`*:
Return the UNIX time corresponding to the array index `index`.

*Method `TimeSeriesFile.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `TimeSeriesFile`, handy for use with `pformat()` or `pprint()`.

*Method `TimeSeriesFile.pad_to(self, when, fill=None)`*:
Pad the time series to store values up to the UNIX time `when`.

The `fill` value is optional and defaults to the `fill` value
supplied when the `TimeSeries` was initialised.

*Method `TimeSeriesFile.peek(self, when: Union[int, float]) -> Union[int, float]`*:
Read a single data value for the UNIX time `when`.

This method uses the `mmap` interface if the array is not already loaded.

*Method `TimeSeriesFile.peek_offset(self, offset: int) -> Union[int, float]`*:
Read a single data value from `offset`.

This method uses the `mmap` interface if the array is not already loaded.

*Method `TimeSeriesFile.poke(self, when: Union[int, float], value: Union[int, float])`*:
Write a single data value for the UNIX time `when`.

This method uses the `mmap` interface if the array is not already loaded.

*Method `TimeSeriesFile.poke_offset(self, offset: int, value: Union[int, float])`*:
Write a single data value at `offset`.

This method uses the `mmap` interface if the array is not already loaded.

*Method `TimeSeriesFile.save(self, fspath=None, truncate=False)`*:
Save the time series to `fspath`, default `self.fspath`.

*Warning*:
if the file endianness is not the native endianness,
the array will be byte swapped temporarily
during the file write operation.
Concurrent users should avoid using the array during this function.

*Method `TimeSeriesFile.save_to(self, *a, **kw)`*:
Save the time series to `fspath`.

*Warning*:
if the file endianness is not the native endianness,
the array will be byte swapped temporarily
during the file write operation.
Concurrent users should avoid using the array during this function.

Note:
the default behaviour (`truncate=False`) overwrites the data in place,
leaving data beyond the in-memory array untouched.
This is more robust against interruptions or errors,
or updates by other programmes (beyond the in-memory array).
However, if the file is changing endianness or data type
(which never happens without deliberate effort)
this could leave a mix of data, resulting in nonsense
beyond the in-memory array.

*Method `TimeSeriesFile.setitems(self, whens, values, *, skipNone=False)`*:
Bulk set values.

*Property `TimeSeriesFile.stop`*:
The end time of this array;
the UNIX time of the first time slot beyond the end of the array.

*Property `TimeSeriesFile.tags`*:
The `TagSet` associated with this `TimeSeriesFile` instance.

## Class `TimeSeriesFileHeader(cs.binary.SimpleBinary, types.SimpleNamespace, cs.binary.AbstractBinary, cs.binary.BinaryMixin, HasEpochMixin, TimeStepsMixin)`

The binary data structure of the `TimeSeriesFile` file header.

This is 24 bytes long and consists of:
* the 4 byte magic number, `b'csts'`
* the file bigendian marker, a `struct` byte order indicator
  with a value of `b'>'` for big endian data
  or `b'<'` for little endian data
* the datum typecode, `b'd'` for double float
  or `b'q'` for signed 64 bit integer
* the time typecode, `b'd'` for double float
  or `b'q'` for signed 64 bit integer
* a pad byte, value `b'_'`
* the start UNIX time, a double float or signed 64 bit integer
  according to the time typecode and bigendian flag
* the step size, a double float or signed 64 bit integer
  according to the time typecode and bigendian flag

In addition to the header values tnd methods this also presents:
* `datum_type`: a `BinarySingleStruct` for the binary form of a data value
* `time_type`:  a `BinarySingleStruct` for the binary form of a time value

*Method `TimeSeriesFileHeader.parse(bfr)`*:
Parse the header record, return a `TimeSeriesFileHeader`.

*Property `TimeSeriesFileHeader.struct_endian_marker`*:
The endianness indicatoe for a `struct` format string.

*Method `TimeSeriesFileHeader.transcribe(self)`*:
Transcribe the header record.

## Class `TimeSeriesMapping(builtins.dict, cs.resources.MultiOpenMixin, cs.context.ContextManagerMixin, HasEpochMixin, TimeStepsMixin)`

A group of named `TimeSeries` instances, indexed by a key.

This is the basis for `TimeSeriesDataDir`.

*Method `TimeSeriesMapping.__missing__(self, key)`*:
Create a new entry for `key` if missing.
This implementation looks up the rules.

*Method `TimeSeriesMapping.__setitem__(self, key: str, ts)`*:
Insert a time series into this `TimeSeriesMapping`.
`key` may not already be present.

*Method `TimeSeriesMapping.as_pd_dataframe(*a, **kw)`*:
Return a `numpy.DataFrame` containing the specified data.

Parameters:
* `start`: start time of the data
* `stop`: end time of the data
* `keys`: optional iterable of keys, default from `self.keys()`

*Method `TimeSeriesMapping.csv_header(self, key: str) -> str`*:
Return the CSV header name for `key`.

*Method `TimeSeriesMapping.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `TimeSeriesMapping`, handy for use with `pformat()` or `pprint()`.

*Method `TimeSeriesMapping.key_typecode(self, key)`*:
The `array` type code for `key`.
This default method returns `'d'` (float64).

*Method `TimeSeriesMapping.make_ts(self, key)`*:
Return the `TimeSeries` for `key`,
creating it if necessary.

*Method `TimeSeriesMapping.plot(*a, tz: Optional[datetime.tzinfo] = None, utcoffset: Union[int, float, NoneType] = None, **kw)`*:
Convenience shim for `DataFrame.plot` to plot data from
`start` to `stop` for each key in `keys`.
Return the plot `Axes`.

Parameters:
* `start`: optional start, default `self.start`
* `stop`: optional stop, default `self.stop`
* `keys`: optional list of keys, default all keys
* `label`: optional label for the graph
* `runstate`: optional `RunState` to allow interruption
* `figure`,`ax`: optional arguments as for `cs.mplutils.axes`
Other keyword parameters are passed to `DataFrame.plot`.

*Method `TimeSeriesMapping.read_csv(self, *a, **kw)`*:
Shim for `pandas.read_csv` to read a CSV file and save the contents
in this `TimeSeriesMapping`.
Return the `DataFrame` used for the import.

Parameters:
* `csvpath`: the filesystem path of the CSV file to read,
  passed to `pandas.read_csv`
* `column_name_map`: an optional rename mapping for column names
  as detailed below
* `pd_read_csv_kw`: other keyword arguments are passed to
  `pandas.read_csv`

The `column_name_map` may have the following values:
* `None`: the default, which renames columns using the
  `column_name_to_identifier` function from `cs.mappings` to
  create identifiers from column names
* `id`: the builtin `id` function, which leaves column names unchanged
* a `bool`: use `column_name_to_identifier` with
  its `snake_case` parameter set to `column_name_map`
* a `callable`: compute the renamed column name from
  `column_name_map(column_name)`
* otherwise assume `column_name_map` is a mapping and compute
  the renamed column name as
  `column_name_map.get(column_name,column_name)`

*Method `TimeSeriesMapping.shortname(self)`*:
Return a short identifying name for this `TimeSeriesMapping`.
For example, `TimeSeriesDataDir` returns `self.shortpath`
for this function.

*Method `TimeSeriesMapping.startup_shutdown(self)`*:
Context manager for `MultiOpenMixin`.
Close the sub time series.

*Method `TimeSeriesMapping.to_csv(self, start, stop, f, *, columns=None, key_map=None, df_mangle=None, **to_csv_kw)`*:
Return `pandas.DataFrame.to_csv()` for the data between `start` and `stop`.

*Method `TimeSeriesMapping.validate_key(key)`*:
Check that `key` is a valid key, raise `valueError` if not.
This implementation requires that `key` is an identifier.

## Class `TimeSeriesPartitioned(TimeSeries, cs.resources.MultiOpenMixin, cs.context.ContextManagerMixin, HasEpochMixin, TimeStepsMixin, cs.fs.HasFSPath)`

A collection of `TimeSeries` files in a subdirectory.
We have one of these for each `TimeSeriesDataDir` key.

This class manages a collection of files
named by the partition from a `TimespanPolicy`,
which dictates which partition holds the datum for a UNIX time.

*Method `TimeSeriesPartitioned.__init__(self, dirpath: str, typecode: str, *, epoch: Union[cs.timeseries.Epoch, Tuple[Union[int, float], Union[int, float]], int, float, NoneType] = None, policy, fstags: Optional[cs.fstags.FSTags] = None)`*:
Initialise the `TimeSeriesPartitioned` instance.

Parameters:
* `dirpath`: the directory filesystem path,
  known as `.fspath` within the instance
* `typecode`: the `array` type code for the data
* `epoch`: the time series `Epoch`
* `policy`: the partitioning `TimespanPolicy`

The instance requires a reference epoch
because the `policy` start times will almost always
not fall on exact multiples of `epoch.step`.
The reference allows for reliable placement of times
which fall within `epoch.step` of a partition boundary.
For example, if `epoch.start==0` and `epoch.step==6` and a
partition boundary came at `19` due to some calendar based
policy then a time of `20` would fall in the partion left
of the boundary because it belongs to the time slot commencing
at `18`.

If `epoch` or `typecode` are omitted the file's
fstags will be consulted for their values.
The `start` parameter will further fall back to `0`.
This class does not set these tags (that would presume write
access to the parent directory or its `.fstags` file)
when a `TimeSeriesPartitioned` is made by a `TimeSeriesDataDir`
instance it sets these flags.

*Method `TimeSeriesPartitioned.__getitem__(self, index: Union[int, float, slice, str])`*:
Obtain various things from this `TimeSeriesPartitioned`
according to the type of `index`:
* `int` or `float`: the value for the UNIX timestamp `index`
* `slice`: a list of the values for the UNIX timestamp slice `index`
* `*.csts`: the `TimeSeriesFile` named `index` within this
  `TimeSeriesPartitioned`
* partition name: the `TimeSeriesFile` for the policy time partition

*Method `TimeSeriesPartitioned.data(self, start, stop)`*:
Return a list of `(when,datum)` tuples for the slot times from `start` to `stop`.

*Method `TimeSeriesPartitioned.info_dict(self, d=None)`*:
Return an informational `dict` containing salient information
about this `TimeSeriesPartitioned`, handy for use with `pformat()` or `pprint()`.

*Method `TimeSeriesPartitioned.partition(self, start, stop)`*:
Return an iterable of `(when,subseries)` for each time `when`
from `start` to `stop`.

*Method `TimeSeriesPartitioned.partition_name_from_filename(tsfilename: str) -> str`*:
Return the time span name from a `TimeSeriesFile` filename.

*Method `TimeSeriesPartitioned.partitioned_spans(self, start, stop)`*:
Generator yielding a sequence of `TimePartition`s covering
the range `start:stop` such that `start` falls within the first
partition via `self.policy`.

*Method `TimeSeriesPartitioned.plot(*a, tz: Optional[datetime.tzinfo] = None, utcoffset: Union[int, float, NoneType] = None, **kw)`*:
Convenience shim for `DataFrame.plot` to plot data from
`start` to `stop`.
Return the plot `Axes`.

Parameters:
* `start`,`stop`: the time range
* `figure`,`ax`: optional arguments as for `cs.mplutils.axes`
* `label`: optional label for the graph
Other keyword parameters are passed to `Axes.plot`
or `DataFrame.plot` for new axes.

*Method `TimeSeriesPartitioned.setitems(self, whens, values, *, skipNone=False)`*:
Store `values` against the UNIX times `whens`.

This is most efficient if `whens` are ordered.

*Property `TimeSeriesPartitioned.start`*:
The earliest time in any component `TimeSeriesFile`.

*Method `TimeSeriesPartitioned.startup_shutdown(self)`*:
Close the subsidiary `TimeSeries` instances.

*Property `TimeSeriesPartitioned.stop`*:
The latest time in any component `TimeSeriesFile`.

*Method `TimeSeriesPartitioned.subseries(self, spec: Union[str, int, float])`*:
Return the `TimeSeries` for `spec`,
which may be a partition name or a UNIX time.

*Property `TimeSeriesPartitioned.tags`*:
The `TagSet` associated with this `TimeSeriesPartitioned` instance.

*Method `TimeSeriesPartitioned.timeseriesfile_from_partition_name(self, partition_name)`*:
Return the `TimeSeriesFile` associated with the supplied partition_name.

*Method `TimeSeriesPartitioned.timeseriesfiles(self)`*:
Return a mapping of partition name to associated `TimeSeriesFile`
for the existing time series data files.

*Method `TimeSeriesPartitioned.tsfilenames(self)`*:
Return a list of the time series data filenames.

## Class `TimespanPolicy(icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A class implementing a policy allocating times to named time spans.

The `TimeSeriesPartitioned` uses these policies
to partition data among multiple `TimeSeries` data files.

Probably the most important methods are:
* `span_for_time`: return a `TimePartition` from a UNIX time
* `span_for_name`: return a `TimePartition` a partition name

*Method `TimespanPolicy.__init__(self, epoch: Union[cs.timeseries.Epoch, Tuple[Union[int, float], Union[int, float]], int, float])`*:
Initialise the policy.

*Method `TimespanPolicy.from_name(policy_name: str, epoch: Union[cs.timeseries.Epoch, Tuple[Union[int, float], Union[int, float]], int, float, NoneType] = None, **policy_kw)`*:
Factory method to return a new `TimespanPolicy` instance
from the policy name,
which indexes `TimespanPolicy.FACTORIES`.

*Method `TimespanPolicy.name_for_time(self, when)`*:
Return a time span name for the UNIX time `when`.

*Method `TimespanPolicy.partitioned_spans(self, start, stop)`*:
Generator yielding a sequence of `TimePartition`s covering
the range `start:stop` such that `start` falls within the first
partition.

Note that these partitions fall in the policy partitions,
but are bracketed by `[round_down(start):stop]`.
As such they will have the correct policy partition names
but the boundaries of the first and last spans
start at `round_down(start)` and end at `stop` respectively.
This makes the returned spans useful for time ranges from a subseries.

*Method `TimespanPolicy.promote(*a, **kw)`*:
Factory to promote `policy` to a `TimespanPolicy` instance.

The supplied `policy` may be:
* `str`: return an instance of the named policy
* `TimespanPolicy` subclass: return an instance of the subclass
* `TimespanPolicy` instance: return the instance

*Method `TimespanPolicy.raw_edges(self, when: Union[int, float])`*:
Return the _raw_ start and end UNIX times
(inclusive and exclusive respectively)
bracketing the UNIX time `when`.
This is the core method that a policy must implement.

These are the direct times implied by the policy.
For example, with a policy for a calendar month
this would return the start second of that month
and the start second of the following month.

These times are used as the basis for the time slots allocated
to a particular partition by the `span_for_time(when)` method.

*Method `TimespanPolicy.register_factory(factory: Callable, name: str)`*:
Register a new policy `factory` under then supplied `name`.

*Method `TimespanPolicy.span_for_name(self, span_name)`*:
Return a `TimePartition` derived from the `span_name`.

*Method `TimespanPolicy.span_for_time(self, when)`*:
Return a `TimePartition` enclosing `when`, a UNIX timestamp.

The boundaries of the partition are derived from the "raw"
start and end times returned by the `raw_edges(when)` method,
but fall on time slot boundaries defined by `self.epoch`.

Because the raw start/end times will usually fall within a
time slot instead of exactly on an edge a decision must be
made as to which partition a boundary slot falls.

This implementation chooses that the time slot spanning the
"raw" start second of the partition belongs to that partition.
As a consequence, the last "raw" seconds of the partition
will belong to the next partition
as their time slot overlaps the "raw" start of the next partition.

*Method `TimespanPolicy.spans_for_times(self, whens)`*:
Generator yielding `(when,TimePartition)` for each UNIX
time in the iterabe `whens`.
This is most efficient if times for a particular span are adjacent,
trivially so if the times are ordered.

## Class `TimespanPolicyAnnual(ArrowBasedTimespanPolicy, TimespanPolicy, icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A annual time policy.
PARTITION_FORMAT = 'YYYY'
ARROW_SHIFT_PARAMS = {'years': 1}

## Class `TimespanPolicyDaily(ArrowBasedTimespanPolicy, TimespanPolicy, icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A daily time policy.
PARTITION_FORMAT = 'YYYY-MM-DD'
ARROW_SHIFT_PARAMS = {'days': 1}

## Class `TimespanPolicyMonthly(ArrowBasedTimespanPolicy, TimespanPolicy, icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A monthly time policy.
PARTITION_FORMAT = 'YYYY-MM'
ARROW_SHIFT_PARAMS = {'months': 1}

## Class `TimespanPolicyWeekly(ArrowBasedTimespanPolicy, TimespanPolicy, icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A weekly time policy.
PARTITION_FORMAT = 'W'
ARROW_SHIFT_PARAMS = {'weeks': 1}

*Method `TimespanPolicyWeekly.partition_format_cononical(self, txt)`*:
Modify the formatted text derived from `self.PARTITION_FORMAT`.

The driving example is the 'weekly' policy, which uses
Arrow's 'W' ISO week format but trims the sub-week day
suffix.  This is sufficient if Arrow can parse the trimmed
result, which it can for 'W'. If not, a subclass might need
to override this method.

## Class `TimespanPolicyYearly(ArrowBasedTimespanPolicy, TimespanPolicy, icontract._metaclass.DBC, HasEpochMixin, TimeStepsMixin)`

A annual time policy.
PARTITION_FORMAT = 'YYYY'
ARROW_SHIFT_PARAMS = {'years': 1}

## Class `TimeStepsMixin`

Methods for an object with `start` and `step` attributes.

*Method `TimeStepsMixin.offset(self, when: Union[int, float]) -> int`*:
Return the step offset for the UNIX time `when` from `self.start`.

Example in a `TimeSeries`:

   >>> ts = TimeSeriesFile('tsfile.csts', 'd', epoch=(19.1, 1.2))
   >>> ts.offset(19.1)
   0
   >>> ts.offset(20)
   0
   >>> ts.offset(22)
   2

*Method `TimeStepsMixin.offset_bounds(self, start, stop) -> (<class 'int'>, <class 'int'>)`*:
Return the bounds of `(start,stop)` as offsets
(`self.start` plus multiples of `self.step`).

*Method `TimeStepsMixin.offset_range(self, start, stop)`*:
Return an iterable of the offsets from `start` to `stop`
in units of `self.step`
i.e. `offset(start) == 0`.

Example in a `TimeSeries`:

   >>> ts = TimeSeriesFile('tsfile.csts', 'd', epoch=(19.1, 1.2))
   >>> list(ts.offset_range(20,30))
   [0, 1, 2, 3, 4, 5, 6, 7, 8]

*Method `TimeStepsMixin.range(self, start, stop)`*:
Return an iterable of the times from `start` to `stop`.

Eample in a `TimeSeries`:

   >>> ts = TimeSeriesFile('tsfile.csts', 'd', epoch=(19.1, 1.2))
   >>> list(ts.range(20,30))
   [19.1, 20.3, 21.5, 22.700000000000003, 23.900000000000002, 25.1, 26.3, 27.5, 28.700000000000003]


Note that if the `TimeSeries` uses `float` values for `start` and `step`
then the values returned here will not necessarily round trip
to array indicies because of rounding.

As such, these times are useful for supplying the index to
a time series as might be wanted for a graph, but are not
reliably useful to _obtain_ the values from the time series.
So this is reliable:

    # works well: pair up values with their times
    graph_data = zip(ts.range(20,30), ts[20:30])

but this is unreliable because of rounding:

    # unreliable: pair up values with their times
    times = list(ts.range(20, 30))
    graph_data = zip(times, [ts[t] for t in times])

The reliable form is available as the `data(start,stop)` method.

Instead, the reliable way to obtain the values between the
UNIX times `start` and `stop` is to directly fetch them
from the `array` underlying the `TimeSeries`.
This can be done using the `offset_bounds`
or `array_indices` methods to obtain the `array` indices,
for example:

    astart, astop = ts.offset_bounds(start, stop)
    return ts.array[astart:astop]

or more conveniently by slicing the `TimeSeries`:

    values = ts[start:stop]

*Method `TimeStepsMixin.round_down(self, when)`*:
Return `when` rounded down to the start of its time slot.

*Method `TimeStepsMixin.round_up(self, when)`*:
Return `when` rounded up to the start of the next time slot.

*Method `TimeStepsMixin.when(self, offset)`*:
Return `self.start+offset*self.step`.

## Class `TypeCode(builtins.str)`

A valid `array` typecode with convenience methods.

*Property `TypeCode.default_fill`*:
The default fill for the type code.

*Method `TypeCode.promote(t)`*:
Promote `t` to a `TypeCode`.

*Method `TypeCode.struct_format(self, bigendian)`*:
Return a `struct` format string for the supplied big endianness.

*Property `TypeCode.type`*:
The Python type for this `TypeCode`.

## Function `tzfor(tzspec: Union[datetime.tzinfo, str, NoneType] = None) -> datetime.tzinfo`

Promote the timezone specification `tzspec` to a `tzinfo` instance.
If `tzspec` is an instance of `tzinfo` it is returned unchanged.
If `tzspec` is omitted or the string `'local'` this returns
`dateutil.tz.gettz()`, the local system timezone.
Otherwise it returns `dateutil.tz.gettz(tzspec)`.

# Release Log



*Release 20220805*:
* Rename @plotrange to @timerange since it is not inherently associated with plotting, support both methods and functions.
* print_figure, save_figure and saved_figure now moved to cs.mplutils.
* plot_events: use the utcoffset parameter.
* TimeSeriesBaseCommand.cmd_plot: new --bare option for unadorned plots.

*Release 20220626*:
* New TypeCode(str) representing an array type code with associated properties and methods.
* New TimeSeriesMapping.read_csv wrapper for pandas.read_csv to import a CSV file into a TimeSeriesMapping.
* TimeSeriesFile.save,save_to: open the file for overwrite, not truncate, by default.
* TimeSeriesFile: new setitems(whens,values) method for fast batch updates.
* as_datetime64s: accept optional units parameter to trade off range versus precision.
* @plotrange: accept new optional tz/utcoffset parameters and pass the resulting utcoffset to the wrapped function along with a huge disclaimer about timezones and plots.
* New tzfor(tzspec) to return a tzinfo object from dateutil.tz.gettz, accepts 'local' for the system local default timezone.
* TimeSeriesMapping.as_pd_dataframe: accept optional utcoffset to skew the index for the DataFrame, used for time presentation in plots.
* New TimeSeriesMapping.to_csv(start,stop,f) method to write CSV data between start and stop to a file via DataFrame.to_csv.
* TimeSeriesBaseCommand: new parsetime and poptime methods, cmd_plot: update to expect start-time and optional stop-time.

*Release 20220606*:
Initial PyPI release.
