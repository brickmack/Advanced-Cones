# Advanced-Cones
Blender addon for more complex cone-like shapes (tangent and secant ogives, prolate spheroids, parabolic cones, power series and Haack series). See https://en.wikipedia.org/wiki/Nose_cone_design for mathematical explanation

## Usage

Coming soon

## Compatibility

**Versions for Blender 2.80 onwards and 2.79 previously are mutually incompatible**. If you are still using Blender 2.79, you must use Advanced Cones v1.1.1, commit [7725f908080646654eb91eb55f7bd2942ee6ee48](https://github.com/brickmack/Advanced-Cones/commit/7725f908080646654eb91eb55f7bd2942ee6ee48). Likewise, users of Blender 2.80 or later must use Advanced Cones v1.2 or later

## Changelog

### v1.2

* **Updated for Blender 2.80 API changes**

### v1.1.1

* **Final version for Blender 2.79 and earlier**

* Correct step sizes on float parameters

* Minor text and metadata fixes

### v1.1

* Correct name of prolate hemispheroid

* Add "smooth tip" option to prolate hemispheroid, correct bug where final vertex was not added

* Fix bug in secant ogive with minimum ogive radius relative to base radius and apex length

* Corrected default parameters for secant ogive to actually fit the secant ogive definition

* Objects now spawn at 3d cursor location, not scene center


### v1.0

* Initial release

## Planned features

* Set rotation at spawn

* New shapes: biconics, spherically-blunted cone

* More useful readme instructions