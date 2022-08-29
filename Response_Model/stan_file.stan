functions {
  // the adstock transformation with a vector of weights
  real Adstock(vector t, row_vector weights) {
    return dot_product(t, weights) / sum(weights);
  }
  real Shape(real t, real H, real S) {
    return ((t^S) / (H^S+t^S));
  }
}
data {
  // the total number of observations
  int<lower=1> N;
  // the vector of sales
  array [N] real y;
  // the maximum duration of lag effect, in weeks
  int<lower=1> max_lag;
  // the number of media channels
  int<lower=0> num_touchpoints;
  // matrix of media variables
  matrix[N+max_lag-1, num_touchpoints] touchpoint_spendings;
  // matrix of seasonality variables
  int<lower=0> num_seasons;
  matrix[N,num_seasons] seasonality;
  // list of mean values of media (raw data)
  vector [num_touchpoints] touchpoint_norms;
}
parameters {
  // residual variance
  real<lower=0> noise_var;
  // the intercept
  real tau;
  // the coefficients for media variables
  vector<lower=0>[num_touchpoints] beta;
  // the coefficients for seasonality variables
  vector[num_seasons] beta_seasonality;
  // the decay and peak parameter for the adstock transformation of
  // each media
  vector<lower=0,upper=1>[num_touchpoints] decay;
  vector<lower=0,upper=ceil(max_lag/2)>[num_touchpoints] peak;
  //Shape parameter
  vector<lower=0,upper=10>[num_touchpoints] H; //Half saturation point
  vector<lower=0,upper=10>[num_touchpoints] S; //slope parameter
}
transformed parameters {
  // the cumulative media effect after adstock
  real cum_effect;
  // the shape effect after cumulation of adstock
  real shape_effect;
  real normalized_data;
  real coefficient;
  real touchpoint_shaped;
  // matrix of media variables after adstock
  matrix[N, num_touchpoints] X_media_adstocked;
  // adstock, mean-center, log1p transformation
  row_vector[max_lag] lag_weights;
  for (nn in 1:N) {
    for (media in 1 : num_touchpoints) {
      for (lag in 1 : max_lag) {
        lag_weights[max_lag-lag+1] = pow(decay[media], (lag - 1 - peak[media]) ^ 2);
      }
      cum_effect = Adstock(sub_col(touchpoint_spendings, nn, media, max_lag), lag_weights);

      normalized_data = cum_effect/touchpoint_norms[media];
      shape_effect = Shape((normalized_data)*5,H[media], S[media]);

      //avoid division by zero
      if (shape_effect ==0)
        coefficient = 0;
      else if (shape_effect !=0)
        coefficient = shape_effect/(normalized_data);
      touchpoint_shaped = coefficient*cum_effect;

      X_media_adstocked[nn, media] = log1p(touchpoint_shaped/touchpoint_norms[media]);
    }
  } 
}
model {
  decay ~ beta(3,3);
  peak ~ uniform(0, ceil(max_lag/2));
  tau ~ normal(0, 5);
  //definition of beta variables - generic for now including media betas
  for (i in 1 : num_touchpoints) {
    beta[i] ~ normal(1, 1);
  }
  for (i in 1 : num_seasons) {
    beta_seasonality[i] ~ normal(1, 1);
  }
  noise_var ~ inv_gamma(0.05, 0.05 * 0.01);
  y ~ normal(tau + X_media_adstocked * beta + seasonality*beta_seasonality, sqrt(noise_var));
}