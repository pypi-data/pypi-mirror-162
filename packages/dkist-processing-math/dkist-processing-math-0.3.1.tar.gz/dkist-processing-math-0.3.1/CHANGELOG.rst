v0.3.1 (2022-08-04)
===================

Features
--------

- Expose `width` and `func` parameters of `peakutils.interpolate` in the signature of `feature.find_px_angles`. (`#11 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/11>`__)


Bugfixes
--------

- If peak angle interpolation fails return the non-interpolated peak instead of garbage. (`#11 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/11>`__)


v0.3.0 (2022-07-07)
===================

Features
--------

- Changed underlying algorithm in `resize_arrays` to allow for higher-order interpolation methods. Local-mean resizing is still available in the new `resize_arrays_local_mean` function. (`#10 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/10>`__)


v0.2.4 (2022-04-20)
===================

Features
--------

- Add `resize_arrays` function for arbitrary reshaping (`#8 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/8>`__)


Documentation
-------------

- Add CHANGELOG and towncrier machinery (`#9 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/9>`__)


v0.2.3 (2022-02-24)
===================

Documentation
-------------

- Set up Read the Docs documentation builds

v0.2.2 (2022-01-20)
===================

Documentation
-------------

- Remove unneeded RTD git dependency

v0.2.1 (2021-12-19)
===================

Bugfixes
--------

- Fix error in Hough transform caused by `scikit-image >= 0.0.19` (`#7 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/7>`__)

v0.2.0 (2021-10-28)
===================

Bugfixes
--------

- Fix mis-ordering of axis caused by difference between skimage and numpy (`#6 <https://bitbucket.org/dkistdc/dkist-processing-math/pull-requests/6>`__)

v0.1.0 (2021-07-28)
===================

The beginning of history
