import stan
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.plot([1,2,3])
plt.savefig('test.png')
# print(np.array([1,2,3]))

print(pd.DataFrame([1,2]))

# print(pd.DataFrame([1,2,3]))
schools_code = """
    data {
      int<lower=0> J;         // number of schools
      real y[J];              // estimated treatment effects
      real<lower=0> sigma[J]; // standard error of effect estimates
    }
    parameters {
      real mu;                // population treatment effect
      real<lower=0> tau;      // standard deviation in treatment effects
      vector[J] eta;          // unscaled deviation from mu by school
    }
    transformed parameters {
      vector[J] theta = mu + tau * eta;        // school treatment effects
    }
    model {
      target += normal_lpdf(eta | 0, 1);       // prior log-density
      target += normal_lpdf(y | theta, sigma); // log-likelihood
    }
    """

schools_data = {"J": 8,
                "y": [28, 8, -3, 7, -1, 1, 18, 12],
                "sigma": [15, 10, 16, 11, 9, 11, 10, 18]}


posterior = stan.build(schools_code, data=schools_data)
fit = posterior.sample(num_chains=4, num_samples=1000)
# print(fit)
extractFrame = fit.to_frame()

print(extractFrame)





'''
// Online C++ compiler to run C++ program online
#include <iostream>
#include <cmath>


float Adstock(float v1[], float v2[]) {
    float dot_product = 0;
    int size = sizeof(v1);
    std::cout << size;
    for(int i=0;i<sizeof(v1);i++){
        dot_product += v1[i] * v2[i];
    }
    return dot_product;
}


float shape_with_threshold(
            float feature_value,
            float shape_param,
            float scale_param,
            float threshold
            
        ){
            float returned_value;
            if (feature_value < threshold)
                returned_value = 0;
            else
                returned_value = 1 - exp(
                    - 1 * pow(
                        ((feature_value - threshold) / scale_param),
                        shape_param
                    )
                );
            return returned_value;
        }


float transform(float spendings[], int N,int nn, int max_lag, float decay, float shape, float scale, float threshold, float touchpointNorm){
    float shaped_touchoint;
    float adstocked_spendings;
    float shaped_touchpoint;
    float touchpoint_transformed;
    float lag_weights[max_lag] ;
    
        
    //calculate weights for adstock function (max_lag-1 because iteration is inclusive of iteration limitor)
    for (lag in 0 : max_lag-1) {
        lag_weights[max_lag-lag] = pow(decay, lag);
    }
    adstocked_spendings = Adstock(spendings, lag_weights);
    shaped_touchpoint = shape_with_threshold(adstocked_spendings,shape, scale, threshold/touchpointNorm);
    touchpoint_transformed = log1p(shaped_touchpoint);
    
    
    return touchpoint_transformed;

}

int main() {
    float tom[10] = [0.0,0.0,0.0,0.3,0.15,0.85,0.65,0.15,0.05,0.05];
    int N = 1;
    int max_lag = 4;
    int nn = 0;
    float decay = 0.4;
    float shape = 1.5;
    float scale = 1.5;
    float touchpointThresholds = 7000;
    float touchpointNorms = 40000;
    float tom_transformed;
    
    tom_transformed = transform(tom, N,nn, max_lag,decay, shape,scale,touchpointThresholds,touchpointNorms);
    // Write C++ code here
    std::cout << "Hello world!";

    return 0;
}


'''