#include "functions.STAN" // Definition of functions to be used by the model

data {
    int<lower=1> T; // Number of weeks
    }