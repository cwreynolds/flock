# flock

### new flock experiments

This is Yet Another implementation of the [boids](https://dl.acm.org/doi/10.1145/37402.37406) model of flocking and related group motions. It was meant just to be a workbench for thinking about new approaches to that old idea.

It is written in Python and Open3D. I started to use c++ and OpenGL, then thought better of it. That earlier start, now unused, is in the `cpp/` subdirectory.

I am not publicizing this very WIP code, but if you happen upon it and have any interest in using it, feel free to [email](mailto:cwr@red3d.com) me.

### Run simulation

After installation (below) simply invoke Python on the main file:

```
python flock.py
```

You can control the view using Open3D's standard gestures. There are also several single key commands to change modes. One is “h” which prints this mini-help on the shell:

```
  flock single key commands:
    space: toggle simulation run/pause
    1:     single simulation step, then pause
    c:     toggle camera between static and boid tracking
    s:     select next boid for camera tracking
    a:     toggle drawing of steering annotation
    w:     toggle between sphere wrap-around or avoidance
    h:     print this message
    esc:   exit simulation.

  mouse view controls:
    Left button + drag         : Rotate.
    Ctrl + left button + drag  : Translate.
    Wheel button + drag        : Translate.
    Shift + left button + drag : Roll.
    Wheel                      : Zoom in/out.
```

### Known bugs (as of May 14, 2023)

Lots, since it is so preliminary, but for example:

- The Boid/Agent class does not actively control its “roll” axis — rotation about its “forward” basis vector — so it is essentially random. Two boids flying next to each other might be upside-down relative to each other.
- Similarly because they ignore global orientation, they are just as happy to move vertically as horizontally.

### Installation

Clone this repository from GitHub to your local machine.

I have been using Python 3.10.10 with Open3D 0.17.0. I created a new Python enviroment like this:

```
conda create -n flock_open3d python=3.10
conda activate flock_open3d
pip install open3d
```

On my laptop (macOS 12.6.4 MacBook Pro M1) this complained that I was missing `libomp` so I did:

```
brew install libomp
```

(Not sure if this is relevant but I had previously installed recent versions of `GLFW` and `GLEW` for the earlier c++/OpenGL branch. I assume Open3D installs what it needs.)
