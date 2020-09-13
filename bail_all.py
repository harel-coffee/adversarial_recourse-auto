from data_utils import *
from train_utils import *
from small_model import *
from big_model import *
from utils import *

delta_max = 0.75

bail_X, bail_y, bail_actionable_indices, bail_categorical_features, bail_categorical_names = process_bail_data()
bail_experiment_dir = 'new_results/0910_experiments/0910_bail_' + str(delta_max) + '/'

#bail_data = get_data(bail_X, bail_y)
#write_data(bail_data, bail_experiment_dir)
bail_data = read_data(bail_experiment_dir)

weights = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
#run(bail_data, bail_actionable_indices, bail_categorical_features, bail_experiment_dir, weights, delta_max, do_train = True)

data = bail_data
experiment_dir = bail_experiment_dir
actionable_indices = bail_actionable_indices
categorical_features = bail_categorical_features
white_feature_name = "WHITE"
data_indices = range(0, 500)

for w in weights:
    print("minority WEIGHT: ", w)    
    weight_dir = experiment_dir + str(w) + "/"
    model = load_torch_model(weight_dir, w)    
    # Runs wachter + our evaluation for every threshold in the 'WEIGHT_val_thresholds_info.csv' file output by the train function
    run_minority_evaluate(model, data, w, delta_max, actionable_indices, experiment_dir, white_feature_name, lam_init = 0.001, data_indices = data_indices)

for w in weights:
    print("lime WEIGHT: ", w)    
    weight_dir = experiment_dir + str(w) + "/"
    model = load_torch_model(weight_dir, w)   

    threshold_df = get_threshold_info(weight_dir, w)
    thresholds = list(threshold_df['thresholds'])

    f1s = threshold_df['f1s'] 

    # only evaluate at the threshold that maximizes f1 score on val data
    eval_thresholds = [thresholds[np.argmax(f1s)]]

    threshold = eval_thresholds[0]
    assert len(eval_thresholds) == 1    

    for kernel_width in [0.5, 1, 1.5, 2.0]:
        lime_berk_evaluate(model, data['X_train'], data['X_test'], data['y_test'], w, threshold, data_indices, actionable_indices, categorical_features, weight_dir, kernel_width)