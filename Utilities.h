//------------------------------------------------------------------------------
//
// Utilities.h -- new flock experiments
//
// Utility functions
//
// MIT License -- Copyright © 2023 Craig Reynolds
//
//------------------------------------------------------------------------------


#pragma once
//#include <cmath>

// Square a float
inline float sq(float f) { return f * f; }

// Constrain a given value "x" to be between two bounds: "bound0" and "bound1"
// (without regard to order). Returns x if it is between the bounds, otherwise
// returns the nearer bound.
inline float clip(float x, float bound0, float bound1)
{
    float clipped = x;
    float min = std::min(bound0, bound1);
    float max = std::max(bound0, bound1);
    if (clipped < min) clipped = min;
    if (clipped > max) clipped = max;
    return clipped;
}

inline float clip01 (const float x)
{
    return clip(x, 0, 1);
}
