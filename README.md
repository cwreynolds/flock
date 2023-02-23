# flock

**new flock experiments**

### Build instructions:
- Clone repository, cd to flock directory:
    - `cd [parent_directory]`
    - `git clone https://github.com/cwreynolds/flock.git`
    - `cd flock/`
- add `build` directory cd there:
    - `mkdir build`
    - `cd build/`
- Generally only needed once:
    - `cmake ..`
- For each edit:
    - `cmake --build .`
    - `./flock`

### macOS hints:
    - Install “Command Line Tools” if needed: `xcode-select –install`
    - Use Homebrew to install CMake, GLEW, and GLFW.
