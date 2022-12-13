import math
import numpy as np
import torch
import plotly
from typing import Dict, List, Optional
from sklearn.decomposition import PCA
import umap
import plotly.express as px
from eXNN.InnerNeuralViz.hook import get_hook


def _plot(embedding, labels):
    if labels is not None:
        return px.scatter(x=embedding[:, 0], y=embedding[:, 1], color=labels)
    else:
        return px.scatter(x=embedding[:, 0], y=embedding[:, 1])


def ReduceDim(data: torch.Tensor,
              mode: str) -> np.ndarray:
    """This function reduces data dimensionality to 2 dimensions.

    Args:
        data (torch.Tensor): input data of shape NxC1x...xCk, where N is the number of data points, C1,...,Ck are dimensions of each data point
        mode (str): dimensionality reduction mode (`umap` or `pca`)

    Raises:
        ValueError: returned if unsupported mode is provided

    Returns:
        np.ndarray: data projected on a 2d space, of shape Nx2
    """

    data = data.detach().cpu().numpy().reshape((len(data), -1))
    if mode == 'pca':
        return PCA(n_components=2).fit_transform(data)
    elif mode == 'umap':
        return umap.UMAP().fit_transform(data)
    else:
        raise ValueError(f'Unsupported mode: `{mode}`')


def VisualizeNetSpace(model: torch.nn.Module,
                      mode: str,
                      data: torch.Tensor,
                      layers: Optional[List[str]] = None,
                      labels: Optional[torch.Tensor] = None,
                      chunk_size: Optional[int] = None) -> Dict[str, plotly.graph_objs._figure.Figure]:
    """This function visulizes data latent representations on neural network layers.

    Args:
        model (torch.nn.Module): neural network
        mode (str): dimensionality reduction mode (`umap` or `pca`)
        data (torch.Tensor): input data of shape NxC1x...xCk, where N is the number of data points, C1,...,Ck are dimensions of each data point
        layers (Optional[List[str]], optional): list of layers for visualization. Defaults to None. If None, visualization for all layers is performed
        labels (Optional[torch.Tensor], optional): data labels (colors). Defaults to None. If None, all points are visualized with the same color
        chunk_size (Optional[int], optional): batch size for data processing. Defaults to None. If None, all data is processed in one batch

    Returns:
        Dict[str, plotly.graph_objs._figure.Figure]: dictionary with latent representations visualization for each layer
    """

    if layers is None:
        layers = [_[0] for _ in model.named_children()]
    if labels is not None:
        labels = list(map(str, labels.detach().cpu().numpy().tolist()))
    hooks = {layer: get_hook(model, layer) for layer in layers}
    if chunk_size is None:
        with torch.no_grad():
            out = model(data)
        visualizations = {'input': _plot(ReduceDim(data, mode), labels)}
        for layer in layers:
            visualizations[layer] = _plot(ReduceDim(hooks[layer].fwd, mode), labels)
        return visualizations
    else:
        representations = {layer: [] for layer in layers}
        for i in range(math.ceil(len(data) / chunk_size)):
            with torch.no_grad():
                out = model(data[i*chunk_size:(i+1)*chunk_size])
            for layer in layers:
                representations[layer].append(hooks[layer].fwd.detach().cpu())
        visualizations = {'input': _plot(ReduceDim(data, mode), labels)}
        for layer in layers:
            layer_reprs = torch.cat(representations[layer], dim=0)
            visualizations[layer] = _plot(ReduceDim(layer_reprs, mode), labels)
        return visualizations


def get_random_input(dims: List[int]) -> torch.Tensor:
    """This function generates uniformly distributed tensor of given shape.

    Args:
        dims (List[int]): required data shape

    Returns:
        torch.Tensor: uniformly distributed tensor of given shape
    """
    return torch.rand(size=dims)
