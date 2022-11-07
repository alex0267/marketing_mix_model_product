stanCode = '''
// -----------------------------------    FUNCTIONS    -----------------------------------
functions {
    // the adstock transformation with a vector of weights
    real Adstock(row_vector t, row_vector weights) {
        return dot_product(t, weights);
    }
    real shape_with_threshold(
                real feature_value,
                real shape_param,
                real scale_param,
                real threshold
                
            ){
                real returned_value;
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
    real Shape(real t, real H, real S) {
        return ((t^S) / (H^S+t^S));
    }
    real transform(row_vector spendings, int N,int nn, int max_lag, real decay, real shape, real scale, real threshold, real touchpointNorm){
        real shaped_touchoint;
        real adstocked_spendings;
        real shaped_touchpoint;
        real touchpoint_transformed;
        row_vector[max_lag] lag_weights;
        
            
        //calculate weights for adstock function (max_lag-1 because iteration is inclusive of iteration limitor)
        for (lag in 0 : max_lag-1) {
            lag_weights[max_lag-lag] = pow(decay, lag);
        }
        adstocked_spendings = Adstock(spendings[nn:nn+max_lag-1], lag_weights);
        shaped_touchpoint = shape_with_threshold(adstocked_spendings,shape, scale, threshold/touchpointNorm);
        touchpoint_transformed = log1p(shaped_touchpoint);
        
        
        return touchpoint_transformed;
    
    }
}
// -----------------------------------    DATA    -----------------------------------
data {
  // the total number of observations
  int<lower=1> N;
  //number of brands in scope
  int<lower=1> B;
  // matrix of seasonality variables
  int<lower=0> num_seasons;
  int<lower=0> num_control;
  // the maximum duration of lag effect, in weeks
  int<lower=1> max_lag;
  // the number of touchpoints
  int<lower=0> num_touchpoints;
  // matrices of touchpoints variables
  matrix[B,N+max_lag-1] tom;
  matrix[B,N+max_lag-1] laura;
  matrix[B,N+max_lag-1] lisa;
  matrix[B,N+max_lag-1] mary;
  matrix[B,N+max_lag-1] fiona;
  matrix[B,N+max_lag-1] marc;
  matrix[B,N+max_lag-1] alex;
  //matrices of control variables
  matrix[B,N] epros;
  matrix[B,N] distribution;
  matrix[B,N] promotion;
  matrix[B,N] off_trade_visibility;
  matrix[B,N] covid;
  // the vector of sales
  matrix [B,N] volume;
  matrix [N,num_seasons] seasonality;
  real control [B,N,num_control] ;
  // threshold values
  vector [num_touchpoints] touchpointThresholds;
  // list of mean values of touchpoints (raw data)
  vector [num_touchpoints] touchpointNorms;
}
// -----------------------------------    PARAMETERS    -----------------------------------
parameters {
  // residual variance
  vector<lower=0>[B] sigma;
  // the intercept
  vector [B] intercept;
  
  // the beta coefficients
  vector[num_seasons] beta_seasonality;
  
  vector<lower=0>[B] beta_tom;
  vector<lower=0>[B]beta_laura;
  vector<lower=0>[B] beta_lisa;
  vector<lower=0>[B] beta_mary;
  vector<lower=0>[B] beta_fiona;
  vector<lower=0>[B] beta_marc;
  vector<lower=0>[B] beta_alex;
  vector<lower=0> [B] beta_epros;
  vector[B] beta_promotion;
  vector<lower=0>[B] beta_distribution;
  vector<lower=0>[B] beta_off_trade_visibility;
  vector[B] beta_covid;
  // the decay and peak parameter for the adstock transformation of
  // each touchpoints - (peak only relevant for specific adstock type)
  vector<lower=0,upper=1>[num_touchpoints] decay;
  vector<lower=0,upper=ceil(max_lag/2)>[num_touchpoints] peak;
  //Shape parameters - distributed, impression-oriented spendings
  vector<lower=0>[num_touchpoints] shape;
  vector<lower=0, upper=1> [num_touchpoints] scale ;
}
// -----------------------------------    TRANSFORMATION    -----------------------------------
transformed parameters {
    matrix[1,N] tom_transformed;
    matrix[1,N] laura_transformed;
    matrix[1,N] lisa_transformed;
    matrix[1,N] mary_transformed;
    matrix[1,N] fiona_transformed;
    matrix[1,N] marc_transformed;
    matrix[1,N] alex_transformed;
    
    for (nn in 1:N) {
        tom_transformed[1,nn] = transform(tom[1], N,nn, max_lag,decay[1], shape[1],scale[1],touchpointThresholds[1],touchpointNorms[1]);
        laura_transformed[1,nn] = transform(laura[1], N,nn, max_lag,decay[2], shape[2],scale[2],touchpointThresholds[2],touchpointNorms[2]);
        lisa_transformed[1,nn] = transform(lisa[1], N,nn, max_lag,decay[3], shape[3],scale[3],touchpointThresholds[3],touchpointNorms[3]);
        mary_transformed[1,nn] = transform(mary[1], N,nn, max_lag,decay[4], shape[4],scale[4],touchpointThresholds[4],touchpointNorms[4]);
        fiona_transformed[1,nn] = transform(fiona[1], N,nn, max_lag,decay[5], shape[5],scale[5],touchpointThresholds[5],touchpointNorms[5]);
        marc_transformed[1,nn] = transform(marc[1], N,nn, max_lag,decay[6], shape[6],scale[6],touchpointThresholds[6],touchpointNorms[6]);
        alex_transformed[1,nn] = transform(alex[1], N,nn, max_lag,decay[7], shape[7],scale[7],touchpointThresholds[7],touchpointNorms[7]);
    }
    
}
// -----------------------------------    MODEL    -----------------------------------
model {
  decay ~ normal(0.5,0.3);
  peak ~ uniform(0, ceil(max_lag/2));
  intercept ~ normal(0, 10);
  beta_tom ~ normal(0, 1);
  beta_laura ~ normal(0, 1);
  beta_lisa ~ normal(0, 1);
  beta_mary ~ normal(0, 1);
  beta_fiona ~ normal(0, 1);
  beta_marc ~ normal(0, 1);
  beta_alex ~ normal(0, 1);

  beta_epros ~ normal(0, 1);
  beta_distribution ~ normal(0, 1);
  beta_promotion ~ normal(0, 1);
  beta_off_trade_visibility ~ normal(0, 1);
  beta_covid ~ normal(0, 1);

  for (i in 1 : num_touchpoints) {
    shape[i] ~ gamma(4,4);
    scale[i] ~ beta(2, 2);
  }
  for (i in 1 : num_seasons) {
    beta_seasonality[i] ~ normal(0, 1);
  }
  
  sigma ~ normal(0, 1);
  volume[1] ~ normal(intercept[1] + 
                to_vector(tom_transformed[1]) * beta_tom[1] +
                to_vector(laura_transformed[1]) * beta_laura[1] +
                to_vector(lisa_transformed[1]) * beta_lisa[1] +
                to_vector(mary_transformed[1]) * beta_mary[1] +
                to_vector(fiona_transformed[1]) * beta_fiona[1] +
                to_vector(marc_transformed[1]) * beta_marc[1] +
                to_vector(alex_transformed[1]) * beta_alex[1] +
                to_vector(epros[1]) * beta_epros[1] +
                to_vector(distribution[1]) * beta_distribution[1] +
                to_vector(promotion[1]) * beta_promotion[1] +
                to_vector(off_trade_visibility[1]) * beta_off_trade_visibility[1] +
                to_vector(covid[1]) * beta_covid[1] +
                seasonality*beta_seasonality,
                sigma[1]);
}



'''
