"""
Usage visualization
=============

.. digraph:: G1

   Data [shape=oval, label="Observed values \n (pd.DataFrame)"];
   Shapefile [shape=oval, label="Shapefile data \n (gpd.DataFrame)"];
   API [shape=box, color=blue, label="API's __call__() method"];
   Echelon [shape=oval, color=red, label="Echelon List Object"];
   Shapefile -> API;
   Data -> API -> Echelon;

   API_hotspots [shape=box, color=blue, label="API's hotspots() method"];
   ScoreData [shape=oval, label="Auxiliary data \n for scoring \n (pd.DataFrame)"];
   Hotspots [shape=oval, color=red, label="Hotspot candidates"];
   ScoreData -> API_hotspots; Echelon -> API_hotspots -> Hotspots;

   API_cluster [shape=box, color=blue, label="API's cluster() method"];
   Clusters [shape=oval, color=red, label="Echelon clusters"];
   Echelon -> API_cluster -> Clusters;

   API_dendrogram [shape=box, color=blue, label="API's dendrogram() method"];
   Dendrogram [shape=oval, color=red, label="Dendrogram"];
   Echelon -> API_dendrogram -> Dendrogram;

   print [shape=none]
   Dendrogram -> print;

   API_geoplot_hotspot [shape=box, color=blue, label="API's plot_hotspot() method"];
   Geoplot_hotspot [shape=oval, color=red, label="Hotspot map"];
   Hotspots -> API_geoplot_hotspot -> Geoplot_hotspot;

   API_geoplot_cluster [shape=box, color=blue, label="API's plot_cluster() method"];
   Geoplot_cluster [shape=oval, color=red, label="Cluster coloring map"];
   Clusters -> API_geoplot_cluster -> Geoplot_cluster;
"""
import importlib
import numpy as np
import pandas as pd
import geopandas as gpd  # For reading shapefiles.
import libpysal  # For constructing "Queen" neighborhoods.
from matplotlib.colors import to_rgba
from echelon.api.dataframe_api import DataFrameEchelonAnalysis

# Type hinting
from typing import Optional
from echelon.api.base import Result_EchelonHotspot

required_modules = [gpd, libpysal]


class GISEchelonAnalysis(DataFrameEchelonAnalysis):
    def __call__(self, data, gdf, id_col, name_col, value_col):
        self.id_col = id_col
        self.adjacency = GISAdjacency(gdf, id_col=self.id_col)
        self.gdf = gdf
        self.df = data
        self.name_col = name_col

        _df = self.df.copy()
        _df['__adjacency'] = self.adjacency.to_series()['adjacency']
        return super().__call__(_df, value_col, self.id_col, '__adjacency')

    def dendrogram(self, *args, **kwargs):
        idx_map_dict = self.df.set_index(self.id_col)[self.name_col].to_dict()
        if 'plot_config_dict' in kwargs:
            kwargs['plot_config_dict'].update({'idx_map': idx_map_dict.get})
        else:
            kwargs['plot_config_dict'] = {'idx_map': idx_map_dict.get}
        return super().dendrogram(*args, **kwargs)

    def plot_adjacency(self):
        """Plot adjacency graph with shapes and names."""
        plotter = GISPlotter(self.gdf, name_col=self.name_col)
        return plotter.plot_adjacency(self.adjacency)

    def plot_hotspot(self, hotspots):
        """Plot heatmap (hotspot score) with shapes and names."""
        plotter = GISPlotter(self.gdf, self.name_col)
        return plotter.plot_hotspot(hotspots, label_col=self.name_col, options=dict(nth=1, id_col=self.id_col))

    def plot_column(self, colname, value_transform: Optional[callable]=None):
        """Plot heatmap (specified column) with shapes and names."""
        _merged_gdf = pd.merge(self.gdf, self.df, on=self.id_col)
        return GISPlotter(_merged_gdf).plot_values(colname, value_transform)


class GISAdjacency:
    """Helper class to generate adjacency information from Shapefiles (.shp) or GeoPandas DataFrame."""
    def __init__(self, gdf: gpd.GeoDataFrame, id_col:Optional[str]=None, adjacency_type:str='Queen'):
        """
        Parameters:
            gdf : GeoDataFrame with an ID column indicated by ``id_col``.
            id_col : column name of the ID. The index is used if ``None``.
            adjacency_type : the name of the adjacency type (the name is used to import a submodule from ``libpysal.weights``).
        Notes:
            The default ``adjacency_type='Queen'`` means using "Queen" adjacency graph.
            Two polygons are connected if they share a single point on their boundary
            (analogously to the "Moore" neighborhood).
        """
        self.gdf = gdf
        self.adjacency_type = adjacency_type
        self.adj = self._build_adjacency(gdf)
        self.id_col = id_col
        if self.id_col is not None:
            if self.gdf.duplicated(subset=[self.id_col]).any():
                raise ValueError(f'{id_col} is required to contain unique identifiers.')

    @classmethod
    def from_shapefile(klass, shape_file_path, *args, **kwargs):
        import geopandas as gpd
        gdf = gpd.read_file(shape_file_path)
        return klass(gdf, *args, **kwargs)

    def _build_adjacency(self, gdf):
        from libpysal import weights
        adjacency_mod = getattr(weights, self.adjacency_type)
        return adjacency_mod.from_dataframe(gdf)

    def _build_series(self):
        adj_series = (self.adj.to_adjlist()
                      .groupby('focal')['neighbor']
                      .agg(list).rename('adjacency'))
        if self.id_col:
            adj_series = adj_series.map(lambda l: [self.gdf.iloc[i][self.id_col] for i in l])
        return adj_series

    def to_series(self):
        adj_series = self._build_series()
        if self.id_col is not None:
            id_series = self.gdf[self.id_col]
        else:
            id_series = self.gdf.index.to_series().rename('id')
        return pd.concat([id_series, adj_series], axis=1)

    def to_networkx(self):
        return self.adj.to_networkx()


class GISPlotter:
    """Helper class to plot geographical data.
    Some information can be stored by the class, but the configurations can be overwritten in each plot:
    - Default figure size
    - GeoPandas DataFrame of (ID, Shape) table.
    """
    def __init__(self, gdf: gpd.GeoDataFrame, name_col:Optional[str]=None):
        self.gdf = gdf
        self.name_col = name_col

    def _set_coords(self, c):
        if 'coords' in c:
            return
        c['coords'] = c['geometry'].apply(lambda x: x.representative_point().coords[:])
        c['coords'] = [coords[0] for coords in c['coords']]

    def _plot_labeled_map(self, value_col: str, gdf: Optional[gpd.GeoDataFrame]=None, value_transform: Optional[callable]=None):
        if value_transform is None:
            value_transform = lambda x: x

        c = gdf if gdf is not None else self.gdf

        ## Coloring
        ax = c.plot(
            color=c[value_col].map(value_transform),
            edgecolor='black',
            figsize=(10, 10),
        )

        self._maybe_plot_names(ax, c)
        return ax

    def _maybe_plot_names(self, ax, c=None, name_plot_options={}):
        if self.name_col is None:
            return
        c = c if c is not None else self.gdf
        self._set_coords(c)

        ## Assign names
        for _, row in c.iterrows():
            if isinstance(row[self.name_col], list):
                name = row[self.name_col][0]
            else:
                name = row[self.name_col]
            ax.text(row.coords[0], row.coords[1],
                    s=name,
                    horizontalalignment='center',
                    bbox={
                        'facecolor': name_plot_options.get('facecolor', 'white'),
                        'alpha':1,
                        'pad': 2,
                        'edgecolor':'none'
                    },
                    )

    def plot_values(self, value_col: str,
                    value_transform: Optional[callable]=None,
                    plot_options=dict(figsize=(40,40)),
                    fontsize=28):
        from matplotlib.colors import to_rgba
        import matplotlib.pyplot as plt
        if value_transform is None:
            value_transform = lambda x: x
        if fontsize is not None:
            plt.rcParams.update({'font.size': fontsize})
        color = self.gdf[value_col].map(lambda v: to_rgba('red', alpha=value_transform(v)))
        ax = self.gdf.plot(color=color, edgecolor='black', **plot_options)
        self._maybe_plot_names(ax)
        return ax

    def plot_hotspot(self, hotspots: Result_EchelonHotspot, label_col: str, options:dict={}):
        """
        Parameters:
            options: dict containing the plot configurations.

                Dict keys:

                    * nth: How-many-th hot spot to plot.
                    * id_col: the column containing the IDs that appear in the hot-spot detection results.
        """
        nth: int = options.get('nth', 1)
        id_col: Optional[str] = options.get('id_col', None)
        name_only_hot: bool = options.get('name_only_hot', False)
        # raise NotImplementedError('Implement "name_only_hot" parameter.')
        if id_col is None:
            id_col = self.name_col
        _df = self.gdf.assign(is_hotspot=self.gdf[id_col].isin(hotspots.iloc[nth - 1]['spot']))
        transform = lambda s: {True: to_rgba('black', alpha=0.3), False: to_rgba('white')}[s]
        return self._plot_labeled_map('is_hotspot', _df, transform)

    def plot_adjacency(self, adj:GISAdjacency, config:dict={}):
        import networkx as nx

        #############
        # For some reason, NetworkX plot functionality (nx.draw()) seems to fail with a newer matplotlib:
        # https://stackoverflow.com/questions/63198347/attributeerror-module-matplotlib-cbook-has-no-attribute-iterable
        import matplotlib
        # assert matplotlib.__version__ =='2.2.3'

        default_config = dict(
            node_size=50,
            node_color="red",
            linewidth=2,
            edgecolor="grey",
            facecolor="lightblue",
        )
        default_config.update(config)
        config = default_config

        graph = adj.to_networkx()

        # Extract the centroids for connecting the regions, which is
        # the average of the coordinates that define the polygon's boundary
        centroids = np.column_stack((self.gdf.centroid.x, self.gdf.centroid.y))

        # To plot with networkx, we need to merge the nodes back to
        # their positions in order to plot in networkx
        positions = dict(zip(graph.nodes, centroids))

        # plot with a nice basemap
        ax = self.gdf.plot(linewidth=config['linewidth'],
                           edgecolor=config['edgecolor'],
                           facecolor=config['facecolor'],
                           figsize=(40, 40),
                           )
        nx.draw(graph, positions, ax=ax, node_size=config['node_size'], node_color=config['node_color'])

        return ax
