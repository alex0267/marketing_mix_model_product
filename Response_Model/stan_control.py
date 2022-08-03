stan_control = '''
data {
  int N; // number of observations
  int K1; // number of seasons
  matrix[N, K1] X1; //seasonality matrix
  vector[N] y; //mean centered sales
  real max_intercept; // restrict the intercept to be less than the minimum y
}

parameters {
  vector<lower=0>[K1] beta1; // regression coefficients for X1 (positive)
  real<lower=0, upper=max_intercept> alpha; // intercept
  real<lower=0> noise_var; // residual variance
}

model {
  // Define the priors
  beta1 ~ normal(0, 1); 
  noise_var ~ inv_gamma(0.05, 0.05 * 0.01);
  // The likelihood
  y ~ normal(X1*beta1 + alpha, sqrt(noise_var));
}
'''