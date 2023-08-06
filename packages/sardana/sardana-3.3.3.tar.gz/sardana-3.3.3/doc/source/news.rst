###########
What's new?
###########

Below you will find the most relevant news that brings the Sardana releases.
For a complete list of changes consult the Sardana `CHANGELOG.md \
<https://gitlab.com/sardana-org/sardana/-/blob/develop/CHANGELOG.md>`_ file.

****************************
What's new in Sardana 3.3.3?
****************************

Date: 2022-08-10 (*Jul22* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

Added
=====

* *View* and *Edit* alternative use modes of :ref:`expconf_ui`. These modes let
  avoid annoying pop-ups with external changes e.g. when experiment configuration was
  changed programmatically by a macro.
* Allow to **not acquire** the last point in :ref:`sardana-users-scan-continuous`
  (by specifying negative value of ``nr_interv`` macro parameters e.g.
  ``ascanct mot01 0 3 -3 1`` will acquire only 3 scan points).
  This enables scans composed from only one scan point and does not extend the motion
  range beyond the point that was requested as the final position plus the necessary
  deceleration range.
* `~sardana.macroserver.macros.scan.rscanct` macro - continuous scan with multiple regions.
* `~sardana.macroserver.macros.expert.reconfig` macro - reconfigure a single axis element
  or the whole controller. Reconfiguration consists of the element initialization
  and application of memorized attribute values.
* Recalculate and set software limits in the
  `~sardana.macroserver.macros.standard.set_user_pos` macro.
* Fully stop :ref:`macro sequences in Spock <sardana-spock-sequences>`
  (*multiline input* macro execution) with ``Ctrl+c`` by propagating
  `KeyboardInterrupt` exception.
* Possibility to use spectrum attributes in :ref:`sardana-users-scan-snapshot`
  in SPEC recorder.
* Improved *instruments* usage experience:

  * Show NeXus class in the `~sardana.macroserver.macros.lists.lsi` macro
  * Add `~sardana.macroserver.macros.expert.definstr` macro for defining new instruments

* Fix order of :ref:`sardana-controller-howto-controller-memorized`.
* :ref:`Trigger/gate coupled and multiplexor modes in position domain <sardana-triggergatecontroller-howto-output-id>`.
* Allow to load :ref:`sardanacustomsettings` from `.ini` configuration files.

Changed
=======

* `~sardana.macroserver.macros.scan.timescan` first parameter from ``nr_interv``
  to ``nb_points`` what results in one acquisition less during the scan.
* Allow to execute new macros during :ref:`sardana-macro-handling-macro-stop-and-abort`.
* `~sardana.pool.controller.TriggerGateController` API: `~sardana.pool.controller.Synchronizer.PreSynchOne()`
  and `~sardana.pool.controller.Synchronizer.SynchOne()` receive
  synchronization description in position domain in :term:`dial position` instead of
  :term:`user position`. The old way was maintained for backwards compatibility but is
  **deprecated**.

Fixed
=====

* Corruption of move targets leading to wrong movements, especially affecting
  motor groups - some motors were erroneously sent to 0.
* Decouple attribute default values from memorized values i.e. changes of the
  attribute default values in the controller code will take effect.
* Issues with aborting :ref:`sardana-users-scan-continuous`.
* Avoid hung :ref:`sardana-acquisition-measgrp` with hardware synchronization
  when working with extended timeout.

Removed
=======

* *Hard links* in NXscan HDF5 files ``measurement`` group pointing to 
  ``measurement/pre_scan_snapshot`` items. Optionally could be re-introduced as
  *soft links* using `~sardana.sardanacustomsettings.NXSCANH5_RECORDER_LINK_PRE_SCAN_SNAPSHOT`.
* *Auto-update* mode in :ref:`expconf_ui` in favor of the *View* mode.
* Master timer/monitor from measurement group configuration. Measurement group
  configurations with master timer/monitor are still supported but are **deprecated**.

****************************
What's new in Sardana 3.2.1?
****************************

Date: 2022-03-21

Type: hotfix release

Fixed
=====

* Make Sardana compatible with Python 3.10.
* Regression introduced in Sardana 3.2.0 causing hangs on motion/acquisition start.
* Macro plotting for matplotlib < 3.

  
**************************
What's new in Sardana 3.2?
**************************

Date: 2022-01-31 (*Jul21* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

Added
=====

* Possibility to *release* hung operations e.g. motion or acquisition hung due to a hung hardware
  controller. Such a release could be issued, for example, from Spock using further 
  :kbd:`Control+c` in the process of :ref:`sardana-spock-stopping`.
* `~sardana.macroserver.macros.scan.rscan`, `~sardana.macroserver.macros.scan.r2scan`
  and `~sardana.macroserver.macros.scan.r3scan` scan macros (formerly available as examples
  under different names `regscan`, `reg2scan` and `reg3scan`). These macros were enahnced with
  the standard scan *hooks* and *scan data* support and fixed so the `region_nr_intervals`
  macro parameter type is now an `int` and the `integ_time` macro parameter was moved to the end.
* Possibility to disable overshoot correction in continuous scans using the
  :ref:`scanovershootcorrection` environment variable.
* Print in form of a table relevant motion parameters: acceleration, velocity, etc. used during
  continuous scans before the scan starts.
* `macro_start_time` dataset in `NXscan` (HDF5, NeXus) data file which contains the scan macro
  execution start timestamp in addition to already existing `start_time` dataset which contains
  the scan measurement start timestamp.
* Possibility to change *custom data* format e.g.: `#UVAR`, `#C`, etc. in the SPEC data file
* `~sardana.macroserver.macros.lists.lsp` macro to list Pools the MacroServer is connected to
* Improve error handling for state read in `~sardana.macroserver.macros.standard.mv` family macros
  and step scan macros.
* History log of motor attributes (sign, offset and step_per_unit) changes.
* Validate new limit values before applying them in `~sardana.macroserver.macros.standard.set_lim`
  and `~sardana.macroserver.macros.standard.set_lm` macros.

Changed
=======

* Execute `post-scan` hooks also in case an exception occurs during the scan execution.
* Default SPEC recorder *custom data* format: `#C` -> `#UVAR`

Fixed
=====

* *Memory leaks* in scans.
* Deletion of Pool element now checks if dependent elements exists. For example, if you delete 
  a motor it will be checked if any pseudo motor depends on it and eventually it will prevent
  the deletion.
* Several issues with stopping macros:

  * Remove annoying info messages of stopping instruments when stopping macros  
  * Stop motion only once in scans
  * Stop/abort element in `~sardana.macroserver.macros.standard.ct` macro when used directly
    with a channel instead of a measurement group
  * Allow aborting macros without prior stopping of them

* Allow to recreate measurement group with the same name but other channels at runtime.
* :ref:`showscan-offline` widget is again usable.
* Avoid problems with duplicated entries in :ref:`sardana-users-scan-snapshot`
* Spock prompt informs when the Door is offline i.e. MacroServer server is not running.
* Make MeasurementGroup state readout evaluate states of the involved elements
* Prevent start of operation e.g. motion or acquisition when the element is not ready.
* Fix restoring velocity in software (`~sardana.macroserver.macros.scan.ascanc`) continuous scans.
* Ensure controller, element and group state are set to Fault and details are reported in the status
  whenever plugin code i.e. controller library, is missing.  
* Hang of IPython when :ref:`sardana-macro-input` gives timeout
* Allow running Spock without an X-session on Linux.
* `~sardana.macroserver.macros.scan.amultiscan` macro parameters interpretation
* Respect measurement group `enabled` configuration  in `~sardana.macroserver.macros.standard.uct` macro
* `~sardana.macroserver.macros.expconf.set_meas_conf` macro when setting *plot axes* on all channels
* :ref:`sequencer_ui` widget action buttons (new, save and play) state (enabled/disabled)
* Make :ref:`pmtv` relative move combobox accept only positive numbers.
* `post_mortem` Spock's magic command which is useful for debugging problems.


****************************
What's new in Sardana 3.1.3?
****************************

Date: 2021-09-17

Type: hotfix release

Fixed
=====

- Regression introduced in Sardana 3.0.3 affecting grouped move/scan of pseudo
  motors proceeding from the same controller e.g. slit's gap and offset, HKL pseudo motors.
  Such a grouped move was only sending set possition to the first pseudo motor.
- Regression introduced in Sardana 3.1.2 affecting custom continuous scans composed from
  waypoints with non-homogeneous number of points. Such scans were producing erroneuous
  number of points due to an error in the final padding logic.

****************************
What's new in Sardana 3.1.2?
****************************

Date: 2021-08-02

Type: hotfix release

Fixed
=====

- Avoid *memory leak* in continuous scans (``ascanct``, ``meshct``, etc.).
  The MacroServer process memory was growing on each scan execution by the
  amount corresponding to storing in the memory the scan data.

****************************
What's new in Sardana 3.1.1?
****************************

Date: 2021-06-11

Type: hotfix release

Fixed
=====

- Correctly handle stop/abort of macros e.g. ``Ctrl+c`` in Spock in case
  the macro was executing another hooked macros e.g. a scan executing a general
  hook.

**************************
What's new in Sardana 3.1?
**************************

Date: 2021-05-17 (*Jan21* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

.. note::

    This release, in comparison to the previous ones, brings significant
    user experience improvements when used on Windows.

Added
=====

- *HDF5 write session*, in order to avoid the file locking problems and to introduce
  the SWMR mode support. It enables safe introspection e.g.: using data
  analysis tools like PyMCA or silx, custom scripts, etc. of the scan data files
  written in the `HDF5 data format <https://www.hdfgroup.org/solutions/hdf5/>`_
  while scanning.
  You can control the session using e.g.:
  `~sardana.macroserver.macros.h5storage.h5_start_session` and
  `~sardana.macroserver.macros.h5storage.h5_end_session` macros
  or the `~sardana.macroserver.macros.h5storage.h5_write_session`
  context manager.
  More information in the :ref:`NXscanH5_FileRecorder documentation \
  <sardana-users-scan-data-storage-nxscanh5_filerecorder>`
- *scan information* and *scan point* forms to the *showscan online* widget.
  See example in the :ref:`showscan online screenshot \
  <showscan-online-infopanels-figure>`.
- Handle `pre-move` and `post-move` hooks by: `mv`, `mvr`, `umv`, `umvr`,
  `br` and `ubr` macros.
  You may use `~sardana.sardanacustomsettings.PRE_POST_MOVE_HOOK_IN_MV`
  for disabling these hooks.
- Include trigger/gate (synchronizer) elements in the per-measurement preparation.
  This enables possible dead time optimization in hardware synchronized step scans.
  More information in the :ref:`How to write a trigger/gate controller documentation \
  <sardana-TriggerGateController-howto-prepare>`.
- :ref:`scanuser` environment variable.
- Support to `PosFormat` :ref:`ViewOption <sardana-spock-viewoptions>` in `umv` macro.
- Avoid double printing of user units in :ref:`pmtv`: read widget and
  units widget.
- Print of allowed :ref:`sardana-macros-hooks` when :ref:`sardana-spock-gettinghelp`
  on macros in Spock.
- Documentation:

    - :ref:`sardana-1dcontroller-howto` and :ref:`sardana-2dcontroller-howto`
    - :ref:`sardana-countertimercontroller` now contains the `SEP18 \
      <http://www.sardana-controls.org/sep/?SEP18.md>`_ concepts.
    - Properly :ref:`sardana-macro-exception-handling` in macros in order
      to not interfere with macro stopping/aborting
    - :ref:`faq_how_to_access_tango_from_macros_and_controllers`
    - Update :ref:`Installation instructions <sardana-installing>`

Changed
=======

- Experimental channel's shape is now considered as a result of the configuration
  e.g. RoI, binning, etc. and not part of the measurement group configuration:

  - Added :ref:`shape controller axis parameter (plugin) <sardana-2dcontroller-general-guide-shape>`,
    `shape` experimental channel attribute (kernel)
    and `Shape` Tango attribute to the experimental channels
  - **Removed** the *shape* column from the measurement group's configuration panel
    in :ref:`expconf_ui`.

Fixed
=====

- Sardana server (standalone) startup is more robust.
- Storing string values in *datasets*, *pre-scan snapshot* and *custom data*
  in :ref:`sardana-users-scan-data-storage-nxscanh5_filerecorder`.
- Stopping/aborting grouped movement when backlash correction would be applied.
- Randomly swapping target positions in grouped motion when moveables proceed
  from various Device Pool's.
- Enables possible dead time optimization in `mesh` scan macro by executing
  :ref:`per measurement preparation <sardana-macros-scanframework-determscan>`.
- Continuously read experimental channel's value references in hardware
  synchronized acquisition instead of reading only once at the end.
- Problems when :ref:`sardana-controller-howto-change-default-interface` of standard attributes
  in controllers e.g. shape of the pseudo counter's Value attribute.
- :ref:`sequencer_ui` related bugs:

    * Fill Macro's `parent_macro` in case of executing XML hooks in sequencer
    * Problems with macro id's when executing sequences loaded from *plain text* files with spock syntax
    * Loading of sequences using macro functions from *plain text* files with spock syntax
- Apply position formatting (configured with `PosFormat`
  :ref:`ViewOption <sardana-spock-viewoptions>`) to the limits in the `wm` macro.
