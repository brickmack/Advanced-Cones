# Advanced-Cones
Blender addon for more complex cone-like shapes.

Mathematical explanations in this readme are adapted from [the Wikipedia article on nosecone geometry](https://en.wikipedia.org/wiki/Nose_cone_design), use it for further reference

## Usage

Advanced Cones adds seven new types of cone shapes, primarily relevant for aerodynamic nosecone design. This image shows them with their default parameters. Left to right they are the tangent ogive, secant ogive, prolate hemispheroid (ellipse), parabolic cone, power series cone, Haack series cone, and n-conic.

<img src="https://i.imgur.com/dpfjrFv.png" align=middle/>

All of the supported cone objects can be accessed through the Add > Mesh menu, or through Blender's search function

<img src="https://i.imgur.com/I6zkrax.png" align=middle/>

For each cone type, click the header to show or hide its information

<details><summary><h3>Tangent Ogive</h3></summary>

<h4>Parameters</h4>

<img src="https://i.imgur.com/1oqTgIW.png" align=middle/>

This cone can be spherically blunted.

<h4>Mathematical basis</h4>

The profile of this shape is formed by a segment of a circle such that the rocket body is tangent to the curve of the nose cone at its base, and the base is on the radius of the circle

The radius of the circle forming the ogive, ρ, is found by

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/969c097b613667654856635f56505c33a2593c2d" align=middle/>

The radius y at any point x, as x varies from 0 to L is:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/3682c253f41bce7dee9e23e6b433bbe0c472f90b" align=middle/>

For a spherically-blunted tangent ogive, the tangency point where the sphere meets the tangent ogive can be found from: 

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/2eee988cfe6178c7c38456862a18f97e052cd633" align=middle/>

where rn is the radius and xo is the center of the spherical nose cap.

The apex point can be found from:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/08d1e5bcefec6ea4c7730fa0e5a60899a75bea12" alighn=middle/>

**Note that, for a spherically-blunted tangent ogive, the apex point is not at the apex length**. The apex length is the point at which the un-blunted ogive would terminate.
</details>

<details><summary><h3>Secant Ogive</h3></summary>

<h4>Parameters</h4>

<img src="https://i.imgur.com/C86yr5e.png" align=middle/>

<h4>Mathematical basis</h4>

Similar to a tangent ogive, except the ogive radius is a parameter, not a derived value, and the the base of the shape is not on the radius of the circle defined by the ogive radius (meaning a cylindrical extension below the ogive will not be tangent to the base of the curve). The ogive radius, ρ, must be at minimum sqrt(L^2 + R^2) / 2. If a smaller ogive radius is set for a fixed base radius and apex length combination, Advanced Cones will automatically reset it to the minimum allowable ogive radius (plus a small constant forced by how floating point numbers are handled). Similarly, if the base radius or apex length are increased beyond the allowable values for a fixed ogive radius, the ogive radius will be recalculated to the minimum.

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/83caab8639031a42fb5e1295b9396dc9f2d8ce9d" align=middle/>

The radius y at any point x as x varies from 0 to L is:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/d75735d81a3192caf10fd54eb4510b1047b21d4a" align=middle/>
</details>

<details><summary><h3>Prolate Hemispheroid (Ellipse)</h3></summary>

<h4>Parameters</h4>

<img src="https://i.imgur.com/nr3t8GY.png" align=middle/>

The Smooth Tip checkbox doubles the number of rings calculated, using an additional n rings in the 1/nth (forward-most) section. Without this, the result is overly pointy

<h4>Mathematical basis</h4>

This is a half-ellipse, rotated about its center line. The radius y at a point x as x varies from 0 to L is:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/6aea3cc391f0e54e7a246ac800ba93dd5e2b3b32" align=middle/>
</details>

<details><summary><h3>Parabolic Cone</h3></summary>

<h4>Parameters</h4>

<img src="https://i.imgur.com/gD7DvxC.png" align=middle/>

<h4>Mathematical basis</h4>

This shape is generated by rotating a segment of a parabola around a line parallel to its latus rectum. The radius y at a point x as x varies from 0 to L is:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/a5625ca045ac69b18cd4a812995b9b42a35d3a00" align=middle/>

Where K' is between 0 and 1, inclusive
</details>

<details><summary><h3>Power Series Cone</h3></summary>

<h4>Parameters</h4>

<img src="https://i.imgur.com/Lh0DMKQ.png" align=middle/>

<h4>Mathematical basis</h4>

The radius y at a point x as x varies from 0 to L is:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/d19693b8d04ed9f57664359b0d368474143a6e61" align=middle/>

where n is between 0 and 1, inclusive. n = 0 produces a cylinder, n = 1/2 produces a parabola, and n = 1 produces a plain cone
</details>

<details><summary><h3>Haack Series Cone</h3></summary>

<h4>Parameters</h4>

<img src="https://i.imgur.com/2qumO3R.png" align=middle/>

<h4>Mathematical basis</h4>

Not geometrically derived, unlike the rest. The radius y at a point x as x varies from 0 to L is given by this pair of equations:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/e5d697fec9f040425b6556e0e67807329f6aeaab" align=middle/>

where C >= 0. The Haack series cone for C = 0 is called the LD-Haack or Von Karman ogive, and gives the minimum drag for the given length and diameter. The Haack series cone for C = 1/3 is called the LV-Haack and gives the minimum drag for a given length and volume.
</details>

<details><summary><h3>N-Conic</h3></summary>
<h4>Parameters</h4>

<img src="https://i.imgur.com/muCs5kz.png" align=middle/>

The n parameter controls the number of frustums that make up the shape. Additional length and radius parameters are added as the n value is changed.

N-conics of n=1 can be spherically blunted. This replaces the previous "Spherically blunted cone" feature. Blunting of n-conics for n>1 is not yet supported

<h4>Mathematical basis</h4>

Just a stack of connected frustums, terminating at a point. Note that currently, Apex Length is the length of the whole object, and the lengths of each frustum are defined as the distance from the apex point, **not** from the base.

For spherically-blunted n-conics, the cap is positioned such that the profile of the cone intersects the sphere at exactly one point, where the two curves are tangent to each other. The tangency point can be found as

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/c18a13450a63ad70c537dacd177ddd3793c7a56b" align=middle/>

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/453bf6fd3bd0e2345311beefdf2b40f5b7487d23" align=middle/>

where rn is the radius of the spherical nose cap. The center of the spherical nose cap, xo, can be found from:

<img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/e797f9219b177e8daa6be9284809f79a547732a7" align=middle/>
</details>

## Compatibility

Advanced Cones v1.3 supports both Blender 2.79 through 2.93. It has been tested and works at least as far back as Blender 2.69, but with some minor issues (see Bugs). If anyone encounters issues with them, please report an issue, I will try to maintain backwards compatibility as long as practical. All screenshots in this readme were taken in Blender 2.80, but the functionality is unchanged in other versions.

## Changelog

### v2.0.2

* Update for Blender 2.93 compatibility

### v2.0.1

* Minor text fix

* Corrected screenshot URLs in readme

### v2.0

* Added n-conic tool

* Removed "Spherically capped cone" tool. Users should instead use the n-conic tool, with n=1 and Blunted enabled. Note that spherical blunting on n-conics is currently *only* supported for n=1

* All Advanced Cones shapes are now found in a submenu, under Add -> Mesh -> Advanced Cones

* Can add cones in edit mode

* Checkbox to enable/disable spherical blunting on cone, tangent ogive

* Spherical blunting is now based on repeated rotations rather than analytical definition. Gives even spacing along the curve instead of along the axis

* Can set rotation of objects at spawn

* Prolate hemispheroid spawns right-side-up

* Added draw() method to each class, allows semi-dynamic control of what parameters are visible to the user

* Moved faces array instantiation to geometry builder

* Added protection for base radius of zero on tangent ogives (previously resulted in a division by zero)

* Delta-qualification for backwards compatibility to at least Blender 2.69

* Updated for API changes in latest Blender 2.80 beta release

* Updated readme for above changes, screenshots now show Blender 2.80 interface

### v1.3

* Restored compatibility with 2.7x, same code now works on 2.7x and 2.8x

* Added spherically blunted cone

* Secant ogive now has correct base radius

* Secant ogive lower bound ogive radius relative to apex length and base radius is now correctly defined, parameters correctly rescale to restore sanity

* Removed unintended limit on Haack Series C value

* All cones now correctly spawn vertically (except prolate hemispheroid, see Known Issues)

* Added all cones to Add Mesh menu

* Reordered parameter layout to be more user friendly

* Text and metadata fixes

* Major overhaul of readme

### v1.2

* Updated for Blender 2.80 API changes

### v1.1.1

* ~~Final version for Blender 2.79 and earlier~~ (Update: v1.3 onwards restore backwards compatibility)

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

* Spherically-blunted n-conics for n>1

* N-conic lengths should be defined by length from the base, not by length from the apex (too confusing!)

* Spherically-blunted secant ogives (and possibly other shapes?)

* Tangent and secant ogives should both be defined as revolutions, not analytically

## Known bugs

* Some unhandled limits of the mathematical definitions of each shape still exist and cause errors. The exception-based handling used in the secant ogive class is the current best solution, but still presents a problem in deriving the minimum offset to not crash the program. Further work needed

* In Blender 2.69 (and possibly newer, probably older) the step size for attribute sliders is too high. Users should manually enter values instead. Sliders work properly in 2.79 and 2.80

* When adding a cone to an existing object, the rotation attribute does not work in Blender 2.80. When adding a cone as a new object, the rotation works correctly
