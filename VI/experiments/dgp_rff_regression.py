import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import sys
sys.path.append(".")
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

from datasets import DataSet
import utils
import likelihoods
from dgp_rff import DgpRff
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import numpy as np
import losses

def import_dataset(dataset, fold):

    train_X = np.loadtxt('../FOLDS/' + dataset + '_ARD_Xtrain__FOLD_' + fold, delimiter=' ')
    train_Y = np.loadtxt('../FOLDS/' + dataset + '_ARD_ytrain__FOLD_' + fold, delimiter=' ')
    train_Y = np.reshape(train_Y, (-1, 1))
    test_X = np.loadtxt('../FOLDS/' + dataset + '_ARD_Xtest__FOLD_' + fold, delimiter=' ')
    test_Y = np.loadtxt('../FOLDS/' + dataset + '_ARD_ytest__FOLD_' + fold, delimiter=' ')
    test_Y = np.reshape(test_Y, (-1, 1))

    data = DataSet(train_X, train_Y)
    test = DataSet(test_X, test_Y)

    return data, test


if __name__ == '__main__':
    FLAGS = utils.get_flags()

    ## Set random seed for tensorflow and numpy operations
    tf.set_random_seed(FLAGS.seed)
    np.random.seed(FLAGS.seed)

    data, test = import_dataset(FLAGS.dataset, FLAGS.fold)

    ## Here we define a custom loss for dgp to show
    error_rate = losses.RootMeanSqError(data.Dout)

    ## Likelihood
    like = likelihoods.Gaussian()

    ## Optimizer
    optimizer = utils.get_optimizer(FLAGS.optimizer, FLAGS.learning_rate)

    ## Main dgp object
    dgp = DgpRff(like, data.num_examples, data.X.shape[1], data.Y.shape[1], FLAGS.nl, FLAGS.n_rff, FLAGS.df, FLAGS.kernel_type, FLAGS.kernel_arccosine_degree, FLAGS.is_ard, FLAGS.local_reparam, FLAGS.feed_forward, FLAGS.q_Omega_fixed, FLAGS.theta_fixed, FLAGS.learn_Omega)

    ## Learning
    dgp.learn(data, FLAGS.learning_rate, FLAGS.mc_train, FLAGS.batch_size, FLAGS.n_iterations, optimizer,
                 FLAGS.display_step, test, FLAGS.mc_test, error_rate, FLAGS.duration, FLAGS.less_prints, FLAGS.dataset)
