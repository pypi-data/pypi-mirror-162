import pandas as pd
import numpy as np
import argparse
import sys
import os

from .estimate import calculate_interval
from .estimate import calculate_posterior
from .estimate import calculate_expectations

####################################################################################
def load_calibration_data(input_path):
    df = pd.read_csv(input_path, low_memory=False)
    return df

####################################################################################
def run_simulation(df, measure, session, top_left, bot_right, results_path):
    top = top_left.split(",")
    bot = bot_right.split(",")
    if len(top) != 2:
        print("TOP LEFT COORDINATES MUST BE A COMMA SEPARATED PAIR OF INTEGERS")
        exit(1)
    if len(bot) != 2:
        print("BOTTOM RIGHT COORDINATES MUST BE A COMMA SEPARATED PAIR OF INTEGERS")
        exit(1)
    try:
        tlx = int(top[0]) 
        tly = int(top[1])
    except:
        print("TOP LEFT COORDINATES MUST BE A COMMA SEPARATED PAIR OF INTEGERS")
        exit(1)
    try:
        brx = int(bot[0]) 
        bry = int(bot[1])
    except:
        print("BOTTOM RIGHT COORDINATES MUST BE A COMMA SEPARATED PAIR OF INTEGERS")
        exit(1)

    increment = 50
    posterior = calculate_posterior(df, session, increment, tlx, tly, brx, bry)
    np.savetxt(results_path+"/posterior.out", posterior)
    expected = calculate_expectations(session, increment, posterior)
    expected.to_csv(results_path+"/expected_values.csv",index=False, header=True)
    results = calculate_interval(measure, session, increment, posterior)
    results.to_csv(results_path+"/error_bounds.csv",index=False, header=True)


####################################################################################
def main():
    desc = 'Estimate Gaze Duration Error Distribution from Eye Tracking Data'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('calibration_data',
                       metavar='calibration_data',
                       type=str,
                       help='Path to the model calibration data contains targets and gaze coords - Requires columns [target_x, target_y, gaze_x, gaze_y]')

    parser.add_argument('measurement',
                       metavar='measurement',
                       type=float,
                       help='Measured gaze duration (in milliseconds) [for which we want error bounds].')

    parser.add_argument('session_length',
                       metavar='session_length',
                       type=float,
                       help='Length of total viewing session (in milliseconds) [Max in principle gaze duration]')

    parser.add_argument('target_top_left',
                       metavar='target_top_left',
                       type=str,
                       help='X,Y Position for top left of target bounding box.')

    parser.add_argument('target_bottom_right',
                       metavar='target_bottom_right',
                       type=str,
                       help='X,Y Position for bottom right of target bounding box.')

    parser.add_argument('results',
                       metavar='results',
                       type=str,
                       help='Path to directory for results: posterior distribution and expected values.')

    args = parser.parse_args()
    data = args.calibration_data
    measure = args.measurement
    session = args.session_length
    top_left = args.target_top_left
    bottom_right = args.target_bottom_right
    results = args.results

    if measure > session:
        print(" ERROR")
        print('Measured duration cannot be longer than session')
        sys.exit()

    if not os.path.isfile(data):
        print(" ERROR")
        print(" The input file '%s' does not exist" % data)
        sys.exit()

    df = load_calibration_data(data)

    run_simulation(df, measure, session, top_left, bottom_right, results)


##########################################################################################
if __name__ == '__main__':
    main()


