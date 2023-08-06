import pandas as pd
import numpy as np
import random
import math
 
#################################################################################
def calculate_interval( measure, session, increment, posterior):
    """
    Take the posterior distribution and extract the section for a specific measurement.
    This function depends on the output of ``calculate_posterior``
    """
    measure = round(float(measure))
    session = round(float(session))
    D = math.floor(session / increment) + 1
    G = math.floor(measure / increment) 
    if measure > session:
        raise Exception('InvalidRequest', 'Measured duration cannot be longer than session')
    # Return distrubution for Measurement G
    result = extract_intervals(posterior[G,:], [0.99, 0.95,0.90,0.80], increment=increment )
    measurements = [x * increment for x in range(0,D)]
    print("Posterior\n", posterior[G,:])
    print("Total Probability: ", posterior[G,:].sum())
    expected_value = (posterior[G,:]*measurements).sum()
    print("Expected Value: ", expected_value)
    return result

#################################################################################
def calculate_expectations(session, increment, posterior):
    """
    Take a posterior distribution calculated by ``calculate_posterior`` and iterate
    over the quantised measurements to calculate the expected true gaze duration
    for each. Return results in a data frame.
    """
    session = round(float(session))
    D = math.floor(session / increment) + 1
    measurements = [x * increment for x in range(0,D)]
    results = pd.DataFrame(columns=["Measured","Expected"])
    for d in range(0,D):
        expected_value = (posterior[d,:]*measurements).sum()
        print("Measured:", measurements[d], " Expected Value: ", expected_value)
        results = results.append({
            "Measured":measurements[d],
            "Expected":expected_value
        }, ignore_index=True)

    return results

#################################################################################
def calculate_posterior(df, session, increment, top_l_x, top_l_y, bot_r_x, bot_r_y, max_x=None, max_y=None):
    """
    Calculate the posterior distributions for actual gaze duration over all possible measurements
    For a given session length, and granuality specified by interval.
    Params
    * df: A dataframe of eye tracking calibration data
    * session: The eye tracking session length (in milliseconds)
    * interval: The discrete step size for possible measurements (in milliseconds)
    * top_l_x, top_l_y, bot_r_x, bot_r_y : Top left and bottom right coordinates of target.
    * max_x, max_y  : Screen dimensions (Optional) Will take max values in the validation file as default

    Returns: A 2 dimensions array containing posterior distributions over reall gaze duration for measurments.
    * Dimension 1: Index of measured duration.
    * Dimension 2: Index of actual duration.
    * Cell Value : Probability of that specific combination. 
               
    Note: If you fix the first dimension the the values over the second dimensions sum to 1
    """

    if not (df.columns == ['target_x','target_y','gaze_x','gaze_y']).all():
        msg = 'Calibration data must consist of columns: target_x, target_y, gaze_x, gaze_y'
        raise Exception('InvalidRequest', msg)

    # Force session to be rounded integers
    session = round(float(session))
    N = 1000
    inc = 1/N
    D = math.floor(session / increment) + 1
    prior = 1/D
    P = np.zeros([D,D])
    top_l = (top_l_x, top_l_y)
    bot_r = (bot_r_x, bot_r_y)

    if max_x==None:
        max_x, max_y = extract_screen_limits(df, bot_r_x, bot_r_y)

    def euclidean(point, ref):
        dist = [(a - b)**2 for a, b in zip(point, ref)]
        dist = math.sqrt(sum(dist))
        return dist

    df['err_x'] = df['gaze_x'] - df['target_x']
    df['err_y'] = df['gaze_y'] - df['target_y']

    df['ref'] = df.apply(lambda x: (x['target_x'],x['target_y']), axis=1)

    x_err = df.groupby('ref')['err_x'].apply(list).reset_index()
    y_err = df.groupby('ref')['err_y'].apply(list).reset_index()

    noise = x_err.copy()
    noise['err_y'] = y_err['err_y']

    def apply_measurement_noise(point):
       """ Use the calibration data to add noise to the path point """
       temp = noise.copy()
       temp['distance'] = temp['ref'].apply(lambda r: euclidean(point, r))
       temp.sort_values('distance', inplace=True)
       top1 = temp.loc[0,:]['distance']
       top2 = temp.loc[1,:]['distance']
       top3 = temp.loc[2,:]['distance']
       threshold1 = (top2+top3)/(top1+top2+top3)
       threshold2 = threshold1 + (1-threshold1)*(top3)/(top2+top3)
       randy = random.uniform(0,1)
       if randy < threshold1:
           noise_set = temp.loc[0,:]
       elif randy < threshold2:
           noise_set = temp.loc[1,:]
       else:
           noise_set = temp.loc[2,:]
       recs = len(noise_set['err_x'])
       rn = random.randrange(0,recs)
       return (point[0] + noise_set['err_x'][rn], point[1] + noise_set['err_y'][rn])


    for d in range(0,D):
        for n in range(0,N):
            in_path = get_path(d, top_l_x, top_l_y, bot_r_x, bot_r_y)
            out_path = get_path(D-d-1, 0, 0, max_x, max_y, top_l_x, top_l_y, bot_r_x, bot_r_y)
            path = in_path + out_path
            measured_path = [apply_measurement_noise(point) for point in path] 
            insiders = [int(inside(p,top_l,bot_r)) for p in measured_path]
            dhat = sum(insiders)
            P[d,dhat] += inc    

    # ########################################################################
    # At this point we have a set of probability distributions over
    # the measured duration (dhat) for a range of potential values 
    # of true gaze duration (d). This is the distribution p(dhat|d)
    # We invert this to get p(d|dhat) using Bayes rule. 
    posterior = invert_distribution(prior, P)

    return posterior


################################################################################################
def invert_distribution(prior, likelihood):
    """
    We want to generate a posterior probability distribution using Bayes Rule
    Provided we get a prior probability and a liklihood (conditional probabilities)
    Likelihood should be a two dimensional array.
    * First dimension is the actual value
    * Second dimension is the measured value
    So by holding the first dimension fixed, 
    The second dimension contains the distribution P(measured|actual)
    We invert this to return P(actual|measured)
    """
    dim_actual, dim_measured = likelihood.shape
    rez = np.zeros([dim_measured,dim_actual])
    for dhat in range(0,dim_measured):
        # Extract those measurements as a vector
        vec = likelihood[:,dhat]
        numera = np.nan_to_num(prior * vec)
        denom = numera.sum()
        if denom > 0.0:
           posterior = numera/denom
        else:
           posterior = np.zeros(len(numera))
        rez[dhat,:] = posterior
    return rez

###########################################################
def extract_intervals(dist, intervals, increment):
    cumulative = 0
    upper_bound = increment * (len(dist)-1)
    lowers = np.zeros(len(intervals)) 
    uppers = [upper_bound for x in lowers] 
    time = 0
    for t in range(dist.shape[0]):
        cumulative = cumulative + dist[t]
        for i in range(len(intervals)):
            if cumulative < (1 - intervals[i]):
                lowers[i] = time
        time = time + increment
    time = upper_bound
    cumulative = 0
    for t in range(dist.shape[0]):
        cumulative = cumulative + dist[len(dist)-t-1]
        for i in range(len(intervals)):
            if cumulative < (1 - intervals[i]):
                uppers[i] = time
        time = time - increment

    result = pd.DataFrame({"Level":intervals, "Lower":lowers, "Upper":uppers})
    return result

###########################################################
def extract_screen_limits(df, bot_r_x, bot_r_y):
    """
    Take the calibration data and determine the maximum screen size 
    target_x,target_y,gaze_x,gaze_y
    """
    max_x = df['target_x'].max()
    if max_x < bot_r_x:
        max_x = bot_r_x
    max_y = df['target_y'].max()
    if max_y < bot_r_y:
        max_y = bot_r_y
    return max_x, max_y

###########################################################
def get_path(n, l_x, l_y, r_x, r_y, exc_l_x=-1,exc_l_y=-1,exc_r_x=-1,exc_r_y=-1):
    """
    Get a path of points of length n
    Within the specified bounds.
    Optional parameters to define a space of exclusion
    """
    result = []
    for i in range(0,n):
        valid = False
        while not valid:
            temp_x = random.randrange(l_x, r_x) 
            temp_y = random.randrange(l_y, r_y) 
            if not point_inside(temp_x, temp_y, exc_l_x, exc_l_y, exc_r_x, exc_r_y):
                valid = True
        result.append( (temp_x, temp_y) )

    return result
 
###########################################################
def point_inside(temp_x, temp_y, exc_l_x, exc_l_y, exc_r_x, exc_r_y):
    if (temp_x >= exc_l_x) & (temp_x <= exc_r_x) & (temp_y >= exc_l_y) & (temp_y <= exc_r_y):
        return True
    else:
        return False


###########################################################
def inside(point, top_l, bot_r):
    return point_inside( point[0], point[1], top_l[0], top_l[1], bot_r[0], bot_r[1])




