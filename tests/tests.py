import matplotlib
import numpy as np
import torch

import eXNN.bayes as bayes_api
import eXNN.topology as topology_api
import eXNN.visualization as viz_api
import tests.test_utils as utils


def test_check_random_input():
    shape = [5, 17, 81, 37]
    data = viz_api.get_random_input(shape)
    utils.compare_values(type(data), torch.Tensor, "Wrong result type")
    utils.compare_values(torch.Size(shape), data.shape, "Wrong result shape")


def _check_reduce_dim(mode):
    N, dim, data = utils.create_testing_data()
    reduced_data = viz_api.reduce_dim(data, mode)
    utils.compare_values(np.ndarray, type(reduced_data), "Wrong result type")
    utils.compare_values((N, 2), reduced_data.shape, "Wrong result shape")


def test_reduce_dim_umap():
    _check_reduce_dim("umap")


def test_reduce_dim_pca():
    _check_reduce_dim("pca")


def test_visualization():
    N, dim, data = utils.create_testing_data()
    model = utils.create_testing_model()
    layers = ["second_layer", "third_layer"]
    res = viz_api.visualize_layer_manifolds(model, "umap", data, layers=layers)

    utils.compare_values(dict, type(res), "Wrong result type")
    utils.compare_values(3, len(res), "Wrong dictionary length")
    utils.compare_values(
        set(["input"] + layers),
        set(res.keys()),
        "Wrong dictionary keys",
    )
    for key, plot in res.items():
        utils.compare_values(
            matplotlib.figure.Figure,
            type(plot),
            f"Wrong value type for key {key}",
        )


def _test_bayes_prediction(mode: str):
    params = {"basic": dict(mode="basic", p=0.5), "beta": dict(mode="beta", a=0.9, b=0.2)}

    N, dim, data = utils.create_testing_data()
    model = utils.create_testing_model()
    n_iter = 10
    res = bayes_api.DropoutBayesianWrapper(model, **(params[mode])).predict(data, n_iter=n_iter)

    utils.compare_values(dict, type(res), "Wrong result type")
    utils.compare_values(2, len(res), "Wrong dictionary length")
    utils.compare_values(set(["mean", "std"]), set(res.keys()), "Wrong dictionary keys")
    utils.compare_values(torch.Size([N, n_iter]), res["mean"].shape, "Wrong mean shape")
    utils.compare_values(torch.Size([N, n_iter]), res["std"].shape, "Wrong mean std")


def test_basic_bayes_wrapper():
    _test_bayes_prediction("basic")


def test_beta_bayes_wrapper():
    _test_bayes_prediction("beta")


def test_data_barcode():
    N, dim, data = utils.create_testing_data()
    res = topology_api.get_data_barcode(data, "standard", "3")
    utils.compare_values(dict, type(res), "Wrong result type")


def test_nn_barcodes():
    N, dim, data = utils.create_testing_data()
    model = utils.create_testing_model()
    layers = ["second_layer", "third_layer"]
    res = topology_api.get_nn_barcodes(model, data, layers, "standard", "3")
    utils.compare_values(dict, type(res), "Wrong result type")
    utils.compare_values(2, len(res), "Wrong dictionary length")
    utils.compare_values(set(layers), set(res.keys()), "Wrong dictionary keys")
    for layer, barcode in res.items():
        utils.compare_values(
            dict,
            type(barcode),
            f"Wrong result type for key {layer}",
        )


def test_barcode_plot():
    N, dim, data = utils.create_testing_data()
    barcode = topology_api.get_data_barcode(data, "standard", "3")
    plot = topology_api.plot_barcode(barcode)
    utils.compare_values(matplotlib.figure.Figure, type(plot), "Wrong result type")
