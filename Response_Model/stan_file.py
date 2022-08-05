stan_code = '''

functions {
  // the adstock transformation with a vector of weights
  real Adstock(vector t, row_vector weights) {
    return dot_product(t, weights) / sum(weights);
  }
}

data {
  // the total number of observations
  int<lower=1> N;
  // the vector of sales
  real y[N];
  // the maximum duration of lag effect, in weeks
  int<lower=1> max_lag;
  // the number of media channels
  int<lower=0> num_media;
  // matrix of media variables
  matrix[N+max_lag-1, num_media] X_media;
  // matrix of seasonality variables
  matrix[N,12] seasonality;
  // list of mean values of media (raw data)
  vector [num_media] media_mean;

}
parameters {
  // residual variance
  real<lower=0> noise_var;
  // the intercept
  real tau;
  // the coefficients for media variables
  vector<lower=0>[num_media] beta;
  // the coefficients for seasonality variables
  vector[12] beta_seasonality;
  // the decay and peak parameter for the adstock transformation of
  // each media
  vector<lower=0,upper=1>[num_media] decay;
  vector<lower=0,upper=ceil(max_lag/2)>[num_media] peak;
}

transformed parameters {
  // the cumulative media effect after adstock
  real cum_effect;
  // matrix of media variables after adstock
  matrix[N, num_media] X_media_adstocked;

  // adstock, mean-center, log1p transformation
  row_vector[max_lag] lag_weights;
  for (nn in 1:N) {
    for (media in 1 : num_media) {
      for (lag in 1 : max_lag) {
        lag_weights[max_lag-lag+1] <- pow(decay[media], (lag - 1 - peak[media]) ^ 2);
      }
    cum_effect <- Adstock(sub_col(X_media, nn, media, max_lag), lag_weights);
    X_media_adstocked[nn, media] <- log1p(cum_effect/media_mean[media]);
    }
  } 
}

model {
  decay ~ beta(3,3);
  peak ~ uniform(0, ceil(max_lag/2));
  tau ~ normal(0, 5);
  //definition of beta variables - generic for now including media betas
  for (i in 1 : num_media) {
    beta[i] ~ normal(1, 1);
  }
  for (i in 1 : 12) {
    beta_seasonality[i] ~ normal(1, 1);
  }
  noise_var ~ inv_gamma(0.05, 0.05 * 0.01);
  y ~ normal(tau + X_media_adstocked * beta + seasonality*beta_seasonality, sqrt(noise_var));
}

'''