import math
import os
import time
from datetime import datetime
from math import inf
from heapq import heappop, heappush
import collections
import functools
from collections import defaultdict
import heapq
import random
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import *
from shapely.geometry import Point,LineString
import geopandas as gpd
import osmnx as ox


class World:
    """
    一个类
    """
    Observation = collections.namedtuple('Observation', 'traveltime origin destination')  # 起点位置的集合

    def __init__(self, type=0, num=100, sigma=0, reg=0, time_limit=0.6):
        """
        nodeUrl: 图对象的点的标识信息和位置信息
        edgeUrl: 图对象的弧的标识信息、位置信息以及连接信息
        type: 选择图对象的类型，0为small，1为normal
        超参数num,sigma,reg
        """
        self.type = type
        self.num = num
        self.sigma = sigma
        self.reg = reg
        self.time_limit = time_limit

    def True_Graph(self):
        """
        如果type=0时，加载small_model的真实图。如果type=1时，加载normal_model的真实图。如果其他情况，加载manhattan的真实图。
        :return: 返回一个加载好的的图G对象
        """
        if self.type == 0:
            # <载入文件模块>
            df_nodelist = pd.read_csv("../train_dataset/smallnodelist.csv")
            df_edgelist = pd.read_csv("../train_dataset/smalledgelist.csv")

            # 创建多重有向图，add_edge(1,2), add_edge(2,1)
            T = nx.MultiDiGraph()  # 初始化图并载入点和边模块
            T.add_nodes_from(df_nodelist['node'])  # 添加点auto
            T.add_edges_from(zip(df_edgelist['node1'], df_edgelist['node2']))  # 添加边auto

            # <设置人工网络arcTime和distance模块>
            for u, v, d in T.edges(data=True):
                T.edges[u, v, 0]['distance'] = 1

            for u, v, d in T.edges(data=True):  # 设置outside的行程时间
                T.edges[u, v, 0]['arcTime'] = 1

            T.edges[7, 8, 0]['arcTime'] = 4
            T.edges[8, 7, 0]['arcTime'] = 4
            T.edges[8, 9, 0]['arcTime'] = 4
            T.edges[9, 8, 0]['arcTime'] = 4

            T.edges[12, 13, 0]['arcTime'] = 4
            T.edges[13, 12, 0]['arcTime'] = 4
            T.edges[13, 14, 0]['arcTime'] = 4
            T.edges[14, 13, 0]['arcTime'] = 4

            T.edges[17, 18, 0]['arcTime'] = 4
            T.edges[18, 17, 0]['arcTime'] = 4
            T.edges[18, 19, 0]['arcTime'] = 4
            T.edges[19, 18, 0]['arcTime'] = 4

            T.edges[7, 12, 0]['arcTime'] = 4
            T.edges[12, 7, 0]['arcTime'] = 4
            T.edges[12, 17, 0]['arcTime'] = 4
            T.edges[17, 12, 0]['arcTime'] = 4

            T.edges[8, 13, 0]['arcTime'] = 4
            T.edges[13, 8, 0]['arcTime'] = 4
            T.edges[13, 18, 0]['arcTime'] = 4
            T.edges[18, 13, 0]['arcTime'] = 4

            T.edges[9, 14, 0]['arcTime'] = 4
            T.edges[14, 9, 0]['arcTime'] = 4
            T.edges[14, 19, 0]['arcTime'] = 4
            T.edges[19, 14, 0]['arcTime'] = 4

            return T


        elif self.type == 1:
            # <载入文件模块>
            df_nodelist = pd.read_csv('../train_dataset/normalnodelist.csv')
            df_edgelist = pd.read_csv('../train_dataset/normaledgelist.csv')

            # 创建多重有向图，add_edge(1,2), add_edge(2,1)
            T = nx.MultiDiGraph()  # 初始化图并载入点和边模块
            T.add_nodes_from(df_nodelist['node'])  # 添加点auto
            T.add_edges_from(zip(df_edgelist['node1'], df_edgelist['node2']))  # 添加边auto

            # <设置人工网络arcTime和distance模块>
            for u, v, d in T.edges(data=True):
                T.edges[u, v, 0]['distance'] = 1

            for u, v, d in T.edges(data=True):  # 设置outside的行程时间
                T.edges[u, v, 0]['arcTime'] = 1

            T.edges[31, 32, 0]['arcTime'] = 4  # 设置upper-left的行程时间
            T.edges[32, 31, 0]['arcTime'] = 4
            T.edges[31, 51, 0]['arcTime'] = 4  # 设置第2row的weight
            T.edges[51, 31, 0]['arcTime'] = 4
            for i in range(32, 39):
                T.edges[i, i - 1, 0]['arcTime'] = 4
                T.edges[i - 1, i, 0]['arcTime'] = 4
                T.edges[i, i + 1, 0]['arcTime'] = 4
                T.edges[i + 1, i, 0]['arcTime'] = 4
                T.edges[i, i + 20, 0]['arcTime'] = 4
                T.edges[i + 20, i, 0]['arcTime'] = 4
            T.edges[39, 38, 0]['arcTime'] = 4
            T.edges[38, 39, 0]['arcTime'] = 4
            T.edges[39, 59, 0]['arcTime'] = 4
            T.edges[59, 39, 0]['arcTime'] = 4

            for j in range(51, 191, 20):  # 设置第3row到第9row的weight
                T.edges[j, j + 1, 0]['arcTime'] = 4
                T.edges[j + 1, j, 0]['arcTime'] = 4
                T.edges[j, j - 20, 0]['arcTime'] = 4
                T.edges[j - 20, j, 0]['arcTime'] = 4
                T.edges[j, j + 20, 0]['arcTime'] = 4
                T.edges[j + 20, j, 0]['arcTime'] = 4
                for i in range(j + 1, j + 8):
                    T.edges[i, i - 1, 0]['arcTime'] = 4
                    T.edges[i - 1, i, 0]['arcTime'] = 4
                    T.edges[i, i + 1, 0]['arcTime'] = 4
                    T.edges[i + 1, i, 0]['arcTime'] = 4
                    T.edges[i, i - 20, 0]['arcTime'] = 4
                    T.edges[i - 20, i, 0]['arcTIme'] = 4
                    T.edges[i, i + 20, 0]['arcTime'] = 4
                    T.edges[i + 20, i, 0]['arcTime'] = 4
                T.edges[j + 8, j + 8 - 1, 0]['arcTime'] = 4
                T.edges[j + 8 - 1, j + 8, 0]['arcTime'] = 4
                T.edges[j + 8, j + 8 - 20, 0]['arcTime'] = 4
                T.edges[j + 8 - 20, j + 8, 0]['arcTime'] = 4
                T.edges[j + 8, j + 8 + 20, 0]['arcTime'] = 4
                T.edges[j + 8 + 20, j + 8, 0]['arcTime'] = 4

            T.edges[191, 192, 0]['arcTime'] = 4  # 设置第10row的weight
            T.edges[192, 191, 0]['arcTime'] = 4
            T.edges[191, 171, 0]['arcTime'] = 4
            T.edges[171, 191, 0]['arcTime'] = 4
            for i in range(192, 199):
                T.edges[i, i - 1, 0]['arcTime'] = 4
                T.edges[i - 1, i, 0]['arcTime'] = 4
                T.edges[i, i + 1, 0]['arcTime'] = 4
                T.edges[i + 1, i, 0]['arcTime'] = 4
                T.edges[i, i - 20, 0]['arcTime'] = 4
                T.edges[i - 20, i, 0]['arcTime'] = 4
            T.edges[199, 198, 0]['arcTime'] = 4
            T.edges[198, 199, 0]['arcTime'] = 4
            T.edges[199, 179, 0]['arcTime'] = 4
            T.edges[179, 199, 0]['arcTime'] = 4

            T.edges[202, 203, 0]['arcTime'] = 2  # 设置lower-right的行程时间
            T.edges[203, 202, 0]['arcTime'] = 2
            T.edges[202, 222, 0]['arcTime'] = 2  # 设置第11row的weight
            T.edges[222, 202, 0]['arcTime'] = 2
            for i in range(203, 210):
                T.edges[i, i - 1, 0]['arcTime'] = 2
                T.edges[i - 1, i, 0]['arcTime'] = 2
                T.edges[i, i + 1, 0]['arcTime'] = 2
                T.edges[i + 1, i, 0]['arcTime'] = 2
                T.edges[i, i + 20, 0]['arcTime'] = 2
                T.edges[i + 20, i, 0]['arcTime'] = 2
            T.edges[210, 209, 0]['arcTime'] = 2
            T.edges[209, 210, 0]['arcTime'] = 2
            T.edges[210, 230, 0]['arcTime'] = 2
            T.edges[230, 210, 0]['arcTime'] = 2

            for j in range(222, 362, 20):  # 设置第12row到第18row的weight
                T.edges[j, j + 1, 0]['arcTime'] = 2
                T.edges[j + 1, j, 0]['arcTime'] = 2
                T.edges[j, j - 20, 0]['arcTime'] = 2
                T.edges[j - 20, j, 0]['arcTime'] = 2
                T.edges[j, j + 20, 0]['arcTime'] = 2
                T.edges[j + 20, j, 0]['arcTime'] = 2
                for i in range(j + 1, j + 8):
                    T.edges[i, i - 1, 0]['arcTime'] = 2
                    T.edges[i - 1, i, 0]['arcTime'] = 2
                    T.edges[i, i + 1, 0]['arcTime'] = 2
                    T.edges[i + 1, i, 0]['arcTime'] = 2
                    T.edges[i, i - 20, 0]['arcTime'] = 2
                    T.edges[i - 20, i, 0]['arcTime'] = 2
                    T.edges[i, i + 20, 0]['arcTime'] = 2
                    T.edges[i + 20, i, 0]['arcTIme'] = 2
                T.edges[j + 8, j + 8 - 1, 0]['arcTime'] = 2
                T.edges[j + 8 - 1, j + 8, 0]['arcTIme'] = 2
                T.edges[j + 8, j + 8 - 1, 0]['arcTime'] = 2
                T.edges[j + 8 - 1, j + 8, 0]['arcTime'] = 2
                T.edges[j + 8, j + 8 - 20, 0]['arcTime'] = 2
                T.edges[j + 8 - 20, j + 8, 0]['arcTime'] = 2

            T.edges[362, 363, 0]['arcTime'] = 2  # 设置第19row的weight
            T.edges[363, 362, 0]['arcTime'] = 2
            T.edges[362, 342, 0]['arcTime'] = 2
            T.edges[342, 362, 0]['arcTime'] = 2
            for i in range(363, 370):
                T.edges[i, i - 1, 0]['arcTime'] = 2
                T.edges[i - 1, i, 0]['arcTime'] = 2
                T.edges[i, i + 1, 0]['arcTime'] = 2
                T.edges[i + 1, i, 0]['arcTime'] = 2
                T.edges[i, i - 20, 0]['arcTime'] = 2
                T.edges[i - 20, i, 0]['arcTime'] = 2
            T.edges[370, 369, 0]['arcTime'] = 2
            T.edges[369, 370, 0]['arcTime'] = 2
            T.edges[370, 350, 0]['arcTime'] = 2
            T.edges[350, 370, 0]['arcTime'] = 2

            return T

        else:
            # manhattan的图对象小弧数据未知
            pass

    def generate_distribution(self):
        """
        对origin和destination进行均匀分布采样
        :para num: 产生的观察样本的数量
        :return: 返回origin和destination的均匀列表
        """
        if self.type == 0:
            # <随机分布模块>
            origin_observations = []  # 产生均匀分布的origin
            for i in range(self.num):
                origin_observations.append(round(random.uniform(1, 25)))
            destination_observations = []  # 产生均匀分布的destination
            for i in range(self.num):
                destination_observations.append(round(random.uniform(1, 25)))
            origin_destination_observations = []  # 产生均匀分布的origin和destination
            for i in range(self.num):
                if origin_observations[i] != destination_observations[i]:
                    origin_destination_observations.append([origin_observations[i], destination_observations[i]])
            return origin_destination_observations
        elif self.type == 1:
            # <随机分布模块>
            origin_observations = []  # 产生均匀分布的origin
            for i in range(self.num):
                origin_observations.append(round(random.uniform(1, 400)))
            destination_observations = []  # 产生均匀分布的destination
            for i in range(self.num):
                destination_observations.append(round(random.uniform(1, 400)))
            origin_destination_observations = []  # 产生均匀分布的origin和destination
            for i in range(self.num):
                if origin_observations[i] != destination_observations[i]:
                    origin_destination_observations.append([origin_observations[i], destination_observations[i]])
            return origin_destination_observations
        else:
            # 真实数据不需要生成仿真数据
            pass

    def lognormal_distribution(self, origin, destination):
        T = self.True_Graph()
        travelTime, path = self.modified_dijkstras(T, origin, destination)
        mu = math.log(travelTime)
        return random.lognormvariate(mu, self.sigma)

    def get_observations(self):  # get_observations是一个生成器
        """Return a generator that yields observation objects"""
        origin_destination_observations = self.generate_distribution()
        for i in range(len(origin_destination_observations)):
            traveltime = self.lognormal_distribution(origin_destination_observations[i][0],
                                                     origin_destination_observations[i][1])
            yield World.Observation(traveltime, origin_destination_observations[i][0],
                                    origin_destination_observations[i][1])

    def project(self, G, lng, lat):
        """
        将某个点的坐标按照欧式距离映射到网络中最近的拓扑点上
        :Param G: 拓扑图
        :Param lng: 经度
        :Param lat: 纬度
        :Return: 返回最近的点的OSMid
        """
        nearest_node = None
        shortest_distance = inf
        for n, d in G.nodes(data=True):
            # d['x']是经度，d['y']是纬度
            new_shortest_distance = ox.distance.euclidean_dist_vec(lng, lat, d['x'], d['y'])
            if new_shortest_distance < shortest_distance:
                nearest_node = n
                shortest_distance = new_shortest_distance
        return nearest_node, shortest_distance

    def get_df_observations(self):
        """
        将观察的样本数据存到同级文件夹data中的observed_data.csv文件中，并读取成dataframe格式
        :return: 返回观察的样本数据的dataframe格式
        """
        if self.type == 0:
            os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建一个人工数据集，并存储在csv(逗号分隔值)文件
            data_file = os.path.join('..', 'train_dataset', 'small_synthetic_observed_data.csv')
            with open(data_file, 'w') as f:
                f.write('traveltime,origin,destination\n')
                for item in self.get_observations():
                    if item[1] != item[2]:
                        f.write('{0},{1},{2}\n'.format(item[0], item[1], item[2]))
            df_observed_data = pd.read_csv("../train_dataset/small_synthetic_observed_data.csv")
            return df_observed_data
        elif self.type == 1:
            os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建一个人工数据集，并存储在csv(逗号分隔值)文件
            data_file = os.path.join('..', 'train_dataset', 'normal_synthetic_observed_data.csv')
            with open(data_file, 'w') as f:
                f.write('traveltime,origin,destination\n')
                for item in self.get_observations():
                    if item[1] != item[2]:
                        f.write('{0},{1},{2}\n'.format(item[0], item[1], item[2]))
            df_observed_data = pd.read_csv("../train_dataset/normal_synthetic_observed_data.csv")
            return df_observed_data
        else:
            # 获取manhattan的networkx对象
            G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')
            # 将network对象转换成geodatafram对象
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
            # observe convert to get_nearest_node路网点,转换成路网点的观察数据dataframe
            df_dataset = pd.read_csv("../train_dataset/dataset.csv")
            df_dataset['dist'] = df_dataset.apply(
                lambda row: self.project(G, row['pickup_longitude'], row['pickup_latitude'])[1] +
                            self.project(G, row['dropoff_longitude'], row['dropoff_latitude'])[1], axis=1)
            df_dataset = df_dataset[df_dataset['dist'] <= 0.002]
            df_dataset.to_csv("../train_dataset/processed_dataset.csv")
            # observe convert to get_nearest_node路网点,转换成路网点的观察数据dataframe
            df_dataset = pd.read_csv("../train_dataset/processed_dataset.csv")
            # 注意axis=1的使用
            df_dataset['pickup_osmid'] = df_dataset.apply(
                lambda row: self.project(G, row['pickup_longitude'], row['pickup_latitude'])[0], axis=1)
            df_dataset['dropoff_osmid'] = df_dataset.apply(
                lambda row: self.project(G, row['dropoff_longitude'], row['dropoff_latitude'])[0], axis=1)
            # d['x']是经度, d['y']是纬度
            df_dataset['projected_pickup_longitude'] = df_dataset.apply(lambda row: G.nodes[row['pickup_osmid']]['x'],
                                                                        axis=1)
            df_dataset['projected_pickup_latitude'] = df_dataset.apply(lambda row: G.nodes[row['pickup_osmid']]['y'],
                                                                       axis=1)
            df_dataset['geometry'] = df_dataset.apply(
                lambda row: Point(float(row['projected_pickup_longitude']), float(row['projected_pickup_latitude'])),
                axis=1)
            # 转换dataframe成goedataframe
            df_dataset_geo = gpd.GeoDataFrame(df_dataset, crs=gdf_edges.crs, geometry=df_dataset.geometry)

            os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建一个人工数据集，并存储在csv(逗号分隔值)文件
            data_file = os.path.join('..', 'train_dataset', 'real_observed_data.csv')
            with open(data_file, 'w') as f:
                f.write('traveltime,origin_osmid,destination_osmid\n')
                for i in range(len(df_dataset_geo)):
                    if df_dataset_geo.iloc[i, 11] != df_dataset_geo.iloc[i, 12] and df_dataset_geo.iloc[
                        i, 11] / 60 >= 1 and df_dataset_geo.iloc[i, 11] / 60 <= 60:
                        f.write('{0},{1},{2}\n'.format(df_dataset_geo.iloc[i, 11] / 60, df_dataset_geo.iloc[i, 13],
                                                       df_dataset_geo.iloc[i, 14]))
            df_observed_data = pd.read_csv("../train_dataset/real_observed_data.csv")
            return df_observed_data

    def get_train_dataset(self):
        """
        将观察的样本数据存到同级文件夹data中的observed_data.csv文件中，并读取成dataframe格式
        :return: 返回观察的样本数据的dataframe格式
        """
        if self.type == 0:
            os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建一个人工数据集，并存储在csv(逗号分隔值)文件
            data_file = os.path.join('..', 'train_dataset', 'small_train_data.csv')
            with open(data_file, 'w') as f:
                f.write('traveltime,origin,destination\n')
                for item in self.get_observations():
                    if item[1] != item[2]:
                        f.write('{0},{1},{2}\n'.format(item[0], item[1], item[2]))
            df_train_data = pd.read_csv("../train_dataset/small_train_data.csv")
            return df_train_data
        elif self.type == 1:
            os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建一个人工数据集，并存储在csv(逗号分隔值)文件
            data_file = os.path.join('..', 'train_dataset', 'normal_train_data.csv')
            with open(data_file, 'w') as f:
                f.write('traveltime,origin,destination\n')
                for item in self.get_observations():
                    if item[1] != item[2]:
                        f.write('{0},{1},{2}\n'.format(item[0], item[1], item[2]))
            df_train_data = pd.read_csv("../train_dataset/normal_train_data.csv")
            return df_train_data
        else:
            # 获取manhattan的networkx对象
            G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')
            # 将network对象转换成geodatafram对象
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
            # observe convert to get_nearest_node路网点,转换成路网点的观察数据dataframe
            df_dataset = pd.read_csv("../train_dataset/train_dataset.csv")
            df_dataset['dist'] = df_dataset.apply(
                lambda row: self.project(G, row['pickup_longitude'], row['pickup_latitude'])[1] +
                            self.project(G, row['dropoff_longitude'], row['dropoff_latitude'])[1], axis=1)
            df_dataset = df_dataset[df_dataset['dist'] <= 0.002]
            df_dataset.to_csv("../train_dataset/processed_dataset.csv")
            # observe convert to get_nearest_node路网点,转换成路网点的观察数据dataframe
            df_dataset = pd.read_csv("../train_dataset/processed_dataset.csv")
            # 注意axis=1的使用
            df_dataset['pickup_osmid'] = df_dataset.apply(
                lambda row: self.project(G, row['pickup_longitude'], row['pickup_latitude'])[0], axis=1)
            df_dataset['dropoff_osmid'] = df_dataset.apply(
                lambda row: self.project(G, row['dropoff_longitude'], row['dropoff_latitude'])[0], axis=1)
            # d['x']是经度, d['y']是纬度
            df_dataset['projected_pickup_longitude'] = df_dataset.apply(lambda row: G.nodes[row['pickup_osmid']]['x'],
                                                                        axis=1)
            df_dataset['projected_pickup_latitude'] = df_dataset.apply(lambda row: G.nodes[row['pickup_osmid']]['y'],
                                                                       axis=1)
            df_dataset['geometry'] = df_dataset.apply(
                lambda row: Point(float(row['projected_pickup_longitude']), float(row['projected_pickup_latitude'])),
                axis=1)
            # 转换dataframe成goedataframe
            df_dataset_geo = gpd.GeoDataFrame(df_dataset, crs=gdf_edges.crs, geometry=df_dataset.geometry)

            os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建一个人工数据集，并存储在csv(逗号分隔值)文件
            data_file = os.path.join('..', 'train_dataset', 'real_train_data.csv')
            with open(data_file, 'w') as f:
                f.write('traveltime,origin_osmid,destination_osmid\n')
                for i in range(len(df_dataset_geo)):
                    if df_dataset_geo.iloc[i, 11] != df_dataset_geo.iloc[i, 12] and df_dataset_geo.iloc[
                        i, 11] / 60 >= 1 and df_dataset_geo.iloc[i, 11] / 60 <= 60:
                        f.write('{0},{1},{2}\n'.format(df_dataset_geo.iloc[i, 11] / 60, df_dataset_geo.iloc[i, 13],
                                                       df_dataset_geo.iloc[i, 14]))
            df_train_data = pd.read_csv("../train_dataset/real_train_data.csv")
            return df_train_data

    def modified_dijkstras(self, G, origin, destination):
        """
        最短路算法
        :return: 返回一个traveltime和path
        """
        count = 0
        paths_and_distances = {}
        for node in G.nodes():
            paths_and_distances[node] = [inf, [origin]]

        paths_and_distances[origin][0] = 0
        vertices_to_explore = [(0, origin)]

        while vertices_to_explore:
            current_distance, current_vertex = heappop(vertices_to_explore)
            for neighbor in G.neighbors(current_vertex):
                edge_weight = G.get_edge_data(current_vertex, neighbor, 0)['arcTime']
                new_distance = current_distance + edge_weight
                new_path = paths_and_distances[current_vertex][1] + [neighbor]
                if new_distance < paths_and_distances[neighbor][0]:
                    paths_and_distances[neighbor][0] = new_distance
                    paths_and_distances[neighbor][1] = new_path
                    heappush(vertices_to_explore, (new_distance, neighbor))
                    count += 1
        return paths_and_distances[destination]

    def Graph(self):
        """
        加载初始化人工网络
        :return: 返回一个加载好的的图G对象
        """
        if self.type == 0:
            # <载入文件模块>
            df_nodelist = pd.read_csv('../train_dataset/smallnodelist.csv')
            df_edgelist = pd.read_csv('../train_dataset/smalledgelist.csv')
            G = nx.MultiDiGraph()  # 初始化图并载入点和边模块
            G.add_nodes_from(df_nodelist['node'])  # 添加点auto
            G.add_edges_from(zip(df_edgelist['node1'], df_edgelist['node2']))  # 添加边auto

            # <设置人工网络weight模块>
            # 搜索nodes和edges一个是一个key，另一个是两个key

            # 设置点对象的x和y坐标，方便自动生成geometry
            for u, d in G.nodes(data=True):
                u_lng = df_nodelist[df_nodelist.node == u].values.squeeze()[1]
                u_lat = df_nodelist[df_nodelist.node == u].values.squeeze()[2]
                d['y'] = u_lat
                d['x'] = u_lng
            #                 d['y'] = 0
            #                 d['x'] = 0

            # 双向车道,因此这是一个多重图
            for u, v, d in G.edges(data=True):  # 设置outside的行程时间
                G.edges[u, v, 0]['arcTime'] = 1
            for u, v, d in G.edges(data=True):
                G.edges[u, v, 0]['distance'] = 1
            # 设置图对象的crs
            G.graph['crs'] = "epsg:4326"
            return G

        elif self.type == 1:
            # <载入文件模块>
            df_nodelist = pd.read_csv('../train_dataset/normalnodelist.csv')
            df_edgelist = pd.read_csv('../train_dataset/normaledgelist.csv')
            G = nx.MultiDiGraph()  # 初始化图并载入点和边模块
            G.add_nodes_from(df_nodelist['node'])  # 添加点auto
            G.add_edges_from(zip(df_edgelist['node1'], df_edgelist['node2']))  # 添加边auto

            # <设置人工网络weight模块>
            # 搜索nodes和edges一个是一个key，另一个是两个key

            # 设置点对象的x和y坐标，方便自动生成geometry
            for u, d in G.nodes(data=True):
                u_lng = df_nodelist[df_nodelist.node == u].values.squeeze()[1]
                u_lat = df_nodelist[df_nodelist.node == u].values.squeeze()[2]
                d['y'] = u_lat
                d['x'] = u_lng
            #                 d['y'] = 0
            #                 d['x'] = 0

            # 双向车道,因此这是一个多重图
            for u, v, d in G.edges(data=True):  # 设置outside的行程时间
                G.edges[u, v, 0]['arcTime'] = 1
            for u, v, d in G.edges(data=True):
                G.edges[u, v, 0]['distance'] = 1
            # 设置图对象的crs
            G.graph['crs'] = "epsg:4326"
            return G

        else:
            # <载入文件模块>
            # 获取manhattan的networkx对象
            G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')

            # <设置人工网络weight模块>

            # 多重无向图与无向图添加权重的方式不同,d就是属性字典,无向图中G.edges[u,v]是字典而多重无向图G.edges[u,v]不是
            for u, v, d in G.edges(data=True):  # 设置outside的行程时间
                G.edges[u, v, 0]['arcTime'] = 1
            for u, v, d in G.edges(data=True):
                G.edges[u, v, 0]['distance'] = 1
            return G

    def optimization_method(self, G, K):
        """
        SOCP优化算法
        :para G: 初始化得到的或上一次迭代计算得到的网络图
        :para K: path set
        :return: 更新过弧行程时间的网络图
        """
        if self.type == 0:
            # <读取数据>
            df_observed_data = pd.read_csv('../train_dataset/small_synthetic_observed_data.csv')
            W = df_observed_data  # 有旅行时间数据的origin，destination集合：观察集合W
            E = G.edges  # 所有的小弧的集合：arc集合E

            # <help函数>
            def geometric_mean(data):  # 计算几何平均数T_od
                total = 1
                for i in data:
                    total *= i  # 等同于total=total*i
                return pow(total, 1 / len(data))

            # <定义模型>
            m = Model("SOCP model")

            # <定义参数>
            time_limit = self.time_limit
            reg = self.reg  # 需要针对问题规模灵活选择

            # <定义自变量>
            names = locals()
            # 变量1:t_ij
            for node1, node2, temp in E:  # 定义小弧的行程时间估计变量t_ij
                names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                          name='arc_' + 'node1_' + str(
                                                                                              node1) + '_node2_' + str(
                                                                                              node2))
                # 变量2:T_hat
            for i in range(W.shape[0]):  # 定义旅行的行程时间估计变量T^hat
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                names['trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                           name='trip_' + 'node1_' + str(
                                                                                               node1) + '_node2_' + str(
                                                                                               node2))
                # 变量3:x_od
            for i in range(W.shape[0]):  # 定义行程时间估计的误差x_od
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                            name='error_' + 'node1_' + str(
                                                                                                node1) + '_node2_' + str(
                                                                                                node2))
            for node1, node2, temp in E:  # 定义绝对值线性化
                names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                          name='abs_' + 'node1_' + str(
                                                                                              node1) + '_node2_' + str(
                                                                                              node2))
                names['abs_' + 'node1_' + str(node2) + '_node2_' + str(node1)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                          name='abs_' + 'node1_' + str(
                                                                                              node2) + '_node2_' + str(
                                                                                              node1))

                # <定义数据结构>
            # 数据结构1:P
            P = defaultdict(list)  # 使用上一次迭代产生的路段行程时间计算本次迭代优化模型的最短路向量
            for i in range(W.shape[0]):
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                P['node1_' + str(origin) + '_node2_' + str(destination)] = \
                self.modified_dijkstras(G, origin, destination)[1]
            # 数据结构2:K
            for key, val in P.items():  # W中观察点的路径集合
                string = key.split('_')
                origin = int(string[1])
                destination = int(string[3])
                K['node1_' + str(origin) + '_node2_' + str(destination)].append(val)

            # 数据结构3:所有观察样本
            O = defaultdict(list)  # origin和destination的行程时间列表
            for i in range(df_observed_data.shape[0]):
                origin = int(df_observed_data.iloc[i][1])
                destination = int(df_observed_data.iloc[i][2])
                O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)].append(
                    df_observed_data.iloc[i][0])
            # 数据结构4:所有观察样本时间的几何平均
            M = defaultdict(int)  # origin和destination的行程时间几何平均值
            for i in range(df_observed_data.shape[0]):
                origin = int(df_observed_data.iloc[i][1])
                destination = int(df_observed_data.iloc[i][2])
                M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)] = geometric_mean(
                    O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)])

            # <定义约束>
            # 11b约束
            for i in range(df_observed_data.shape[0]):  # 添加最短路约束
                origin = int(df_observed_data.iloc[i][1])
                destination = int(df_observed_data.iloc[i][2])
                traveltime, path = self.modified_dijkstras(G, origin, destination)
                arcSum = 0
                for i in range(len(path) - 1):
                    node1 = int(path[i])
                    node2 = int(path[i + 1])
                    arcSum += names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                m.addConstr(names['trip_' + 'node1_' + str(origin) + '_node2_' + str(
                    destination)] == arcSum)  # 添加最短路径行程时间等于旅行的行程时间估计变量的线性约束
            # 11c约束
            if K:
                for key, val in K.items():
                    string = key.split('_')
                    origin = int(string[1])
                    destination = int(string[3])
                    for path in val:
                        othertime = 0
                        for i in range(len(path) - 1):
                            node1 = path[i]
                            node2 = path[i + 1]
                            othertime += names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                        m.addConstr(
                            othertime >= names['trip_' + 'node1_' + str(origin) + '_node2_' + str(destination)])  # 符号反了
            # 11d约束
            for i in range(W.shape[0]):  # 添加误差最小的线性约束
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                m.addConstr(names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= names[
                    'trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] / M[
                                'observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                # 11e约束
            for i in range(W.shape[0]):  # # 添加误差最小的范数约束
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                qexpr1 = names['trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] - names[
                    'error_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                qexpr2 = 2 * np.sqrt(M['observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                qexpr3 = names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] + names[
                    'trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                m.addQConstr(qexpr1 * qexpr1 + qexpr2 * qexpr2 <= qexpr3 * qexpr3)
            # 11f约束
            for node1, node2, temp in E:  # 加速度限制的线性约束
                m.addConstr(names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= time_limit)

                # <定义目标函数>
            obj = 0
            # 添加loss项
            for i in range(W.shape[0]):
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                n_od = len(O['observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                obj += names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] * n_od
            # 添加惩罚项
            for node1, node2, temp in E:
                for node3, node4, temp in E:
                    # 列表求交集,判断连续弧
                    arc1 = [node1, node2]
                    arc2 = [node3, node4]
                    intersection = list(set(arc1) & set(arc2))
                    if intersection:
                        arc1 = names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                        arc2 = names['arc_' + 'node1_' + str(node3) + '_node2_' + str(node4)]
                        dis1 = G.edges[node1, node2, 0]['distance']
                        dis2 = G.edges[node3, node4, 0]['distance']
                        m.addConstr(
                            names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= arc1 / dis1 - arc2 / dis2)
                        m.addConstr(names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= -(
                                    arc1 / dis1 - arc2 / dis2))
                        obj += reg * names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] * 2 / (dis1 + dis2)
            # 添加目标函数
            m.setObjective(obj)

            # <求解模型>
            m.optimize()
            #         print('最优值:',m.objVal)
            #         for v in m.getVars():
            #             print("参数", v.varName,'=',v.x)

            # <更新结果>
            for v in m.getVars():
                string = v.varName.split('_')
                node1 = int(string[2])
                node2 = int(string[4])
                if 'arc' in v.varName:  # 将arc_node1_num_node2_num的weight更新
                    G.edges[node1, node2, 0]['arcTime'] = v.x

            return G, K, P

        elif self.type == 1:
            # <读取数据>
            df_observed_data = pd.read_csv('../train_dataset/normal_synthetic_observed_data.csv')
            W = df_observed_data  # 有旅行时间数据的origin，destination集合：观察集合W
            E = G.edges  # 所有的小弧的集合：arc集合E

            # <help函数>
            def geometric_mean(data):  # 计算几何平均数T_od
                total = 1
                for i in data:
                    total *= i  # 等同于total=total*i
                return pow(total, 1 / len(data))

            # <定义模型>
            m = Model("SOCP model")

            # <定义参数>
            time_limit = self.time_limit
            reg = self.reg  # 需要针对问题规模灵活选择

            # <定义自变量>
            names = locals()
            # 变量1:t_ij
            for node1, node2, temp in E:  # 定义小弧的行程时间估计变量t_ij
                names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                          name='arc_' + 'node1_' + str(
                                                                                              node1) + '_node2_' + str(
                                                                                              node2))
                # 变量2:T_hat
            for i in range(W.shape[0]):  # 定义旅行的行程时间估计变量T^hat
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                names['trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                           name='trip_' + 'node1_' + str(
                                                                                               node1) + '_node2_' + str(
                                                                                               node2))
                # 变量3:x_od
            for i in range(W.shape[0]):  # 定义行程时间估计的误差x_od
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                            name='error_' + 'node1_' + str(
                                                                                                node1) + '_node2_' + str(
                                                                                                node2))
            for node1, node2, temp in E:  # 定义绝对值线性化
                names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                          name='abs_' + 'node1_' + str(
                                                                                              node1) + '_node2_' + str(
                                                                                              node2))

            # <定义数据结构>
            # 数据结构1:P
            P = defaultdict(list)  # 使用上一次迭代产生的路段行程时间计算本次迭代优化模型的最短路向量
            for i in range(W.shape[0]):
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                P['node1_' + str(origin) + '_node2_' + str(destination)] = \
                self.modified_dijkstras(G, origin, destination)[1]
                # 数据结构2:K
            for i in range(W.shape[0]):  # W中观察点的路径集合
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                K['node1_' + str(origin) + '_node2_' + str(destination)].append(
                    self.modified_dijkstras(G, origin, destination)[1])

            # 数据结构3:所有观察样本
            O = defaultdict(list)  # origin和destination的行程时间列表
            for i in range(df_observed_data.shape[0]):
                origin = int(df_observed_data.iloc[i][1])
                destination = int(df_observed_data.iloc[i][2])
                O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)].append(
                    df_observed_data.iloc[i][0])
            # 数据结构4:所有观察样本时间的几何平均
            M = defaultdict(int)  # origin和destination的行程时间几何平均值
            for i in range(df_observed_data.shape[0]):
                origin = int(df_observed_data.iloc[i][1])
                destination = int(df_observed_data.iloc[i][2])
                M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)] = geometric_mean(
                    O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)])

            # <定义约束>
            # 11b约束
            for i in range(df_observed_data.shape[0]):  # 添加最短路约束
                origin = int(df_observed_data.iloc[i][1])
                destination = int(df_observed_data.iloc[i][2])
                traveltime, path = self.modified_dijkstras(G, origin, destination)
                arcSum = 0
                for i in range(len(path) - 1):
                    node1 = int(path[i])
                    node2 = int(path[i + 1])
                    arcSum += names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                m.addConstr(names['trip_' + 'node1_' + str(origin) + '_node2_' + str(
                    destination)] == arcSum)  # 添加最短路径行程时间等于旅行的行程时间估计变量的线性约束
            # 11c约束
            if K:
                for key, val in K.items():
                    string = key.split('_')
                    origin = int(string[1])
                    destination = int(string[3])
                    for path in val:
                        othertime = 0
                        for i in range(len(path) - 1):
                            node1 = path[i]
                            node2 = path[i + 1]
                            othertime += names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                        m.addConstr(
                            othertime >= names['trip_' + 'node1_' + str(origin) + '_node2_' + str(destination)])  # 符号反了
            # 11d约束
            for i in range(W.shape[0]):  # 添加误差最小的线性约束
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                m.addConstr(names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= names[
                    'trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] / M[
                                'observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                # 11e约束
            for i in range(W.shape[0]):  # # 添加误差最小的范数约束
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                qexpr1 = names['trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] - names[
                    'error_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                qexpr2 = 2 * np.sqrt(M['observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                qexpr3 = names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] + names[
                    'trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                m.addQConstr(qexpr1 * qexpr1 + qexpr2 * qexpr2 <= qexpr3 * qexpr3)
            # 11f约束
            for node1, node2, temp in E:  # 加速度限制的线性约束
                m.addConstr(names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= time_limit)

                # <定义目标函数>
            obj = 0
            # 添加loss项
            for i in range(W.shape[0]):
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                n_od = len(O['observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                obj += names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] * n_od
            # 添加惩罚项
            for node1, node2, temp in E:
                for node3, node4, temp in E:
                    # 列表求交集,判断连续弧
                    arc1 = [node1, node2]
                    arc2 = [node3, node4]
                    intersection = list(set(arc1) & set(arc2))
                    if intersection:
                        arc1 = names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                        arc2 = names['arc_' + 'node1_' + str(node3) + '_node2_' + str(node4)]
                        dis1 = G.edges[node1, node2, 0]['distance']
                        dis2 = G.edges[node3, node4, 0]['distance']
                        obj += reg * names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] * 2 / (dis1 + dis2)
                        m.addConstr(
                            names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= arc1 / dis1 - arc2 / dis2)
                        m.addConstr(names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= -(
                                    arc1 / dis1 - arc2 / dis2))
            # 添加目标函数
            m.setObjective(obj, gurobipy.GRB.MINIMIZE)

            # <求解模型>
            m.optimize()
            #         print('最优值:',m.objVal)
            #         for v in m.getVars():
            #             print("参数", v.varName,'=',v.x)

            # <更新结果>
            for v in m.getVars():
                string = v.varName.split('_')
                node1 = int(string[2])
                node2 = int(string[4])
                if 'arc' in v.varName:  # 将arc_node1_num_node2_num的weight更新
                    G.edges[node1, node2, 0]['arcTime'] = v.x

            return G, K, P

        else:
            # <读取数据>
            df_observed_data = pd.read_csv('../train_dataset/real_observed_data.csv')
            W = df_observed_data  # 有旅行时间数据的origin，destination集合：观察集合W
            E = G.edges  # 所有的小弧的集合：arc集合E

            # <help函数>
            def geometric_mean(data):  # 计算几何平均数T_od
                total = 1
                for i in data:
                    total *= i  # 等同于total=total*i
                return pow(total, 1 / len(data))

            # <定义模型>
            m = Model("SOCP model")

            # <定义参数>
            time_limit = self.time_limit
            reg = self.reg  # 需要针对问题规模灵活选择

            # <定义自变量>
            names = locals()
            # 变量1:t_ij
            for node1, node2, temp in E:  # 定义小弧的行程时间估计变量t_ij
                if temp == 0:
                    names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                              name='arc_' + 'node1_' + str(
                                                                                                  node1) + '_node2_' + str(
                                                                                                  node2))
            # 变量2:T_hat
            for i in range(W.shape[0]):  # 定义旅行的行程时间估计变量T^hat
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                names['trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                           name='trip_' + 'node1_' + str(
                                                                                               node1) + '_node2_' + str(
                                                                                               node2))
                # 变量3:x_od
            for i in range(W.shape[0]):  # 定义行程时间估计的误差x_od
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                            name='error_' + 'node1_' + str(
                                                                                                node1) + '_node2_' + str(
                                                                                                node2))
            for node1, node2, temp in E:  # 定义绝对值线性化
                names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                          name='abs_' + 'node1_' + str(
                                                                                              node1) + '_node2_' + str(
                                                                                              node2))

            # <定义数据结构>
            # 数据结构1:P
            P = defaultdict(list)  # 使用上一次迭代产生的路段行程时间计算本次迭代优化模型的最短路向量
            for i in range(W.shape[0]):
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                P['node1_' + str(origin) + '_node2_' + str(destination)] = \
                self.modified_dijkstras(G, origin, destination)[1]
                # 数据结构2:K
            for i in range(W.shape[0]):  # W中观察点的路径集合
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                K['node1_' + str(origin) + '_node2_' + str(destination)].append(
                    self.modified_dijkstras(G, origin, destination)[1])

                # 数据结构3:所有观察样本
            O = defaultdict(list)  # origin和destination的行程时间列表
            for i in range(W.shape[0]):
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)].append(int(W.iloc[i][0]))
            # 数据结构4:所有观察样本时间的几何平均
            M = defaultdict(int)  # origin和destination的行程时间几何平均值
            for i in range(W.shape[0]):
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)] = geometric_mean(
                    O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)])

            # <定义约束>
            # 11b约束
            for i in range(W.shape[0]):  # 添加最短路约束
                origin = int(W.iloc[i][1])
                destination = int(W.iloc[i][2])
                traveltime, path = self.modified_dijkstras(G, origin, destination)
                arcSum = 0
                for i in range(len(path) - 1):
                    node1 = int(path[i])
                    node2 = int(path[i + 1])
                    arcSum += names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                m.addConstr(names['trip_' + 'node1_' + str(origin) + '_node2_' + str(
                    destination)] == arcSum)  # 添加最短路径行程时间等于旅行的行程时间估计变量的线性约束
            # 11c约束
            if K:
                for key, val in K.items():
                    string = key.split('_')
                    origin = int(string[1])
                    destination = int(string[3])
                    for path in val:
                        othertime = 0
                        for i in range(len(path) - 1):
                            node1 = path[i]
                            node2 = path[i + 1]
                            othertime += names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                        m.addConstr(
                            othertime >= names['trip_' + 'node1_' + str(origin) + '_node2_' + str(destination)])  # 符号反了
            # 11d约束
            for i in range(W.shape[0]):  # 添加误差最小的线性约束
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                m.addConstr(names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= names[
                    'trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] / M[
                                'observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                # 11e约束
            for i in range(W.shape[0]):  # # 添加误差最小的范数约束
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                qexpr1 = names['trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)] - names[
                    'error_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                qexpr2 = 2 * np.sqrt(M['observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                qexpr3 = names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] + names[
                    'trip_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                m.addQConstr(qexpr1 * qexpr1 + qexpr2 * qexpr2 <= qexpr3 * qexpr3)
            #             # 11f约束
            #             for node1,node2,temp in E:                 # 加速度限制的线性约束,无解有可能是time_limit的问题
            #                 m.addConstr(names['arc_'+ 'node1_'+str(node1) +'_node2_'+ str(node2)] >= time_limit)

            # <定义目标函数>
            obj = 0
            # 添加loss项
            for i in range(W.shape[0]):
                node1 = int(W.iloc[i][1])
                node2 = int(W.iloc[i][2])
                n_od = len(O['observe_' + 'node1_' + str(node1) + '_node2_' + str(node2)])
                obj += names['error_' + 'node1_' + str(node1) + '_node2_' + str(node2)] * n_od
            # 添加惩罚项
            for node1, node2, temp in E:
                for node3, node4, temp in E:
                    # 列表求交集,判断连续弧
                    arc1 = [node1, node2]
                    arc2 = [node3, node4]
                    intersection = list(set(arc1) & set(arc2))
                    if intersection:
                        arc1 = names['arc_' + 'node1_' + str(node1) + '_node2_' + str(node2)]
                        arc2 = names['arc_' + 'node1_' + str(node3) + '_node2_' + str(node4)]
                        dis1 = G.edges[node1, node2, 0]['distance']
                        dis2 = G.edges[node3, node4, 0]['distance']
                        obj += reg * names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] * 2 / (dis1 + dis2)
                        m.addConstr(
                            names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= arc1 / dis1 - arc2 / dis2)
                        m.addConstr(names['abs_' + 'node1_' + str(node1) + '_node2_' + str(node2)] >= -(
                                    arc1 / dis1 - arc2 / dis2))
            # 添加目标函数
            m.setObjective(obj, gurobipy.GRB.MINIMIZE)

            # <求解模型>
            m.optimize()
            #         print('最优值:',m.objVal)
            #         for v in m.getVars():
            #             print("参数", v.varName,'=',v.x)

            # <更新结果>
            for v in m.getVars():
                string = v.varName.split('_')
                node1 = int(string[2])
                node2 = int(string[4])
                if 'arc' in v.varName:  # 将arc_node1_num_node2_num的weight更新
                    G.edges[node1, node2, 0]['arcTime'] = v.x

            return G, K, P

    def diff(self, lastP, P):
        count = 0
        G = self.Graph()
        arc_lastP = defaultdict(list)
        for key, val in lastP.items():  # lastP   {'node1_num_node2_num':[node1,node2]}
            for i in range(len(val) - 1):
                origin = val[i]
                destination = val[i + 1]
                arc_lastP[key].append(str(origin) + str(destination))  # {"node1_num_node2_num": [arc1,arc2]}

        arc_P = defaultdict(list)
        for key, val in P.items():
            for i in range(len(val) - 1):
                origin = val[i]
                destination = val[i + 1]
                arc_P[key].append(str(origin) + str(destination))

        for key, val in arc_lastP.items():  # {'origin,destination':[arc1,arc2]}
            for arc in val:
                if arc not in arc_P[key]:
                    count += 1
        for key, val in arc_P.items():
            for arc in val:
                if arc not in arc_lastP[key]:
                    count += 1
        return count / len(lastP)

    def RMLSB(self, G):
        """
        定义一个评价函数，对比小弧之间的误差,仿真数据有真实弧数据，而真实数据中通过与其他算法对比获取gap
        G: 训练好的图对象
        test_dataset: 输入测试集，测试集的数据是没有经过训练过的
        """
        RMLSB = 0
        if self.type == 0:
            train_dataset = "../train_dataset/small_synthetic_observed_data.csv"
        elif self.type == 1:
            train_dataset = "../train_dataset/normal_synthetic_observed_data.csv"
        else:
            train_dataset = "../train_dataset/real_observed_data"

        # <help函数>
        def geometric_mean(data):  # 计算几何平均数T_od
            total = 1
            for i in data:
                total *= i  # 等同于total=total*i
            return pow(total, 1 / len(data))

        df_observed_data = pd.read_csv(train_dataset)
        # 数据结构3:所有观察样本
        O = defaultdict(list)  # origin和destination的行程时间列表
        for i in range(df_observed_data.shape[0]):
            origin = int(df_observed_data.iloc[i][1])
            destination = int(df_observed_data.iloc[i][2])
            O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)].append(df_observed_data.iloc[i][0])
        # 数据结构4:所有观察样本时间的几何平均
        M = defaultdict(int)  # origin和destination的行程时间几何平均值
        for i in range(df_observed_data.shape[0]):
            origin = int(df_observed_data.iloc[i][1])
            destination = int(df_observed_data.iloc[i][2])
            M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)] = geometric_mean(
                O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)])
        for origin in G.nodes():
            for destination in G.nodes():
                if origin != destination and int(
                        M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)]) != 0:
                    observe = M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)]
                    trip = self.modified_dijkstras(G, origin, destination)[0]
                    print(observe, trip)
                    RMLSB += math.pow((math.log(trip) - math.log(observe)), 2)

        return np.sqrt(RMLSB)

    def geo(self, G):
        if self.type == 0:
            # 载入文件模块
            df_nodelist = pd.read_csv('../train_dataset/smallnodelist.csv')
            edgelist = []

            for u, v, d in G.edges(data=True):
                u_lng = df_nodelist[df_nodelist.node == u].values.squeeze()[1]
                u_lat = df_nodelist[df_nodelist.node == u].values.squeeze()[2]
                v_lng = df_nodelist[df_nodelist.node == v].values.squeeze()[1]
                v_lat = df_nodelist[df_nodelist.node == v].values.squeeze()[2]
                G.edges[u, v, 0]['geometry'] = LineString([(u_lng, u_lat), (v_lng, v_lat)])
                edge_data = dict()
                edge_data['node1'] = u
                edge_data['node2'] = v
                edge_data.update(d)
                edgelist.append(edge_data)

            df_edgelist = pd.DataFrame(edgelist)

            edgelist_crs = {'init': 'epsg:4326'}

            df_edgelist_geo = gpd.GeoDataFrame(df_edgelist, crs=edgelist_crs, geometry=df_edgelist.geometry)

            return df_edgelist_geo

        elif self.type == 1:
            # 载入文件模块
            df_nodelist = pd.read_csv('../train_dataset/normalnodelist.csv')

            edgelist = []

            for u, v, d in G.edges(data=True):
                u_lng = df_nodelist[df_nodelist.node == u].values.squeeze()[1]
                u_lat = df_nodelist[df_nodelist.node == u].values.squeeze()[2]
                v_lng = df_nodelist[df_nodelist.node == v].values.squeeze()[1]
                v_lat = df_nodelist[df_nodelist.node == v].values.squeeze()[2]
                G.edges[u, v, 0]['geometry'] = LineString([(u_lng, u_lat), (v_lng, v_lat)])
                edge_data = dict()
                edge_data['node1'] = u
                edge_data['node2'] = v
                edge_data.update(d)
                edgelist.append(edge_data)

            df_edgelist = pd.DataFrame(edgelist)

            edgelist_crs = {'init': 'epsg:4326'}

            df_edgelist_geo = gpd.GeoDataFrame(df_edgelist, crs=edgelist_crs, geometry=df_edgelist.geometry)

            return df_edgelist_geo

        else:
            # 绘图模块
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
            return gdf_edges

    def train(self):
        if self.type == 0:
            start_time = time.time()
            # 程序起始
            # a tracktable algorithm
            K = defaultdict(list)
            self.get_df_observations()
            difference = inf
            G = self.Graph()
            T = self.True_Graph()
            count = 0
            while difference >= 0.5:
                self.geo(G).plot(column='arcTime', cmap='RdYlGn')
                G, K, P = self.optimization_method(G, K)
                if count % 2 == 0:
                    lastP1 = P
                else:
                    lastP2 = P
                if count != 0:
                    difference = self.diff(lastP1, lastP2)
                count += 1
                gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
                gdf_nodes.to_file("../smalldata/gdf_nodes" + str(count) + ".geojson", driver="GeoJSON")
                gdf_edges.to_file("../smalldata/gdf_edges" + str(count) + ".geojson", driver="GeoJSON")
                print(f'正在进行第{count}次迭代，误差为{difference}.')
                RMLSB = self.RMLSB(G)
                print(f'优化模型当前的RMLSB为{RMLSB}')

            # 程序结束
            elapsed_time = time.time() - start_time
            hour = elapsed_time // 3600
            minute = (elapsed_time - hour * 3600) // 60
            second = elapsed_time % 60
            print(f'inference time cost: {hour} hours, {minute} minutes,{second} seconds')

        elif self.type == 1:
            start_time = time.time()
            # 程序起始
            # a tracktable algorithm
            K = defaultdict(list)
            self.get_df_observations()
            difference = inf
            G = self.Graph()
            T = self.True_Graph()
            count = 0
            while difference >= 0.5:
                self.geo(G).plot(column='arcTime', cmap='RdYlGn')
                G, K, P = self.optimization_method(G, K)
                if count % 2 == 0:
                    lastP1 = P
                else:
                    lastP2 = P
                if count != 0:
                    difference = self.diff(lastP1, lastP2)
                count += 1
                gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
                gdf_nodes.to_file("../normaldata/gdf_nodes" + str(count) + ".geojson", driver="GeoJSON")
                gdf_edges.to_file("../normaldata/gdf_edges" + str(count) + ".geojson", driver="GeoJSON")
                print(f'正在进行第{count}次迭代，误差为{difference}.')
                RMLSB = self.RMLSB(G)
                print(f'优化模型当前的RMLSB为{RMLSB}')

            # 程序结束
            elapsed_time = time.time() - start_time
            hour = elapsed_time // 3600
            minute = (elapsed_time - hour * 3600) // 60
            second = elapsed_time % 60
            print(f'inference time cost: {hour} hours, {minute} minutes,{second} seconds')


        else:
            start_time = time.time()
            # 程序起始

            # a tracktable algorithm
            K = defaultdict(list)
            self.get_df_observations()
            difference = inf
            G = self.Graph()
            count = 0
            while difference >= 0.5:
                # 第k次迭代
                fig, ax = plt.subplots(figsize=(30, 30))
                self.geo(G).plot(ax=ax, column='arcTime', cmap='Paired', categorical=True)
                ax.set_axis_off()
                plt.show()
                G, K, P = self.optimization_method(G, K)
                if count % 2 == 0:
                    lastP1 = P
                else:
                    lastP2 = P
                if count != 0:
                    difference = self.diff(lastP1, lastP2)
                count += 1
                gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
                # 使用apply函数清洗不同的数据类型的列
                gdf_edges['osmid'] = gdf_edges.apply(lambda row: 0 if type(row['osmid']) == list else row['osmid'],
                                                     axis=1)
                gdf_edges = gdf_edges[gdf_edges['osmid'] > 0]
                gdf_nodes.to_file("../realdata/gdf_nodes" + str(count) + ".geojson", driver="GeoJSON")
                gdf_edges.to_file("../realdata/gdf_edges" + str(count) + ".geojson", driver="GeoJSON")
                print(f'正在进行第{count}次迭代，误差为{difference}.')

            # 程序结束
            elapsed_time = time.time() - start_time
            hour = elapsed_time // 3600
            minute = (elapsed_time - hour * 3600) // 60
            second = elapsed_time % 60
            print(f'inference time cost: {hour} hours, {minute} minutes,{second} seconds')

    def test(self, G):
        """
        G: 输入训练好的图模型
        test_dataset: 输入测试集，与训练集不同
        """
        if self.type == 0:
            test_dataset = "../test_dataset/small_train_data.csv"
        elif self.type == 1:
            test_dataset = "../test_dataset/normal_train_data.csv"
        else:
            test_dataset = "../test_dataset/real_train_data.csv"
        RMLSB = 0

        # <help函数>
        def geometric_mean(data):  # 计算几何平均数T_od
            total = 1
            for i in data:
                total *= i  # 等同于total=total*i
            return pow(total, 1 / len(data))

        df_observed_data = pd.read_csv(test_dataset)
        # 数据结构3:所有观察样本
        O = defaultdict(list)  # origin和destination的行程时间列表
        for i in range(df_observed_data.shape[0]):
            origin = int(df_observed_data.iloc[i][1])
            destination = int(df_observed_data.iloc[i][2])
            O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)].append(df_observed_data.iloc[i][0])
        # 数据结构4:所有观察样本时间的几何平均
        M = defaultdict(int)  # origin和destination的行程时间几何平均值
        for i in range(df_observed_data.shape[0]):
            origin = int(df_observed_data.iloc[i][1])
            destination = int(df_observed_data.iloc[i][2])
            M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)] = geometric_mean(
                O['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)])
        for origin in G.nodes():
            for destination in G.nodes():
                if origin != destination and int(
                        M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)]) != 0:
                    observe = M['observe_' + 'node1_' + str(origin) + '_node2_' + str(destination)]
                    trip = self.modified_dijkstras(G, origin, destination)[0]
                    RMLSB += math.pow((math.log(trip) - math.log(observe)), 2)

        return np.sqrt(RMLSB)


class Visualization:

    def __init__(self, G, type=0, manual=True):

        self.G = G
        self.type = type
        self.manual = manual

    def Graph(self):
        """
        加载初始化人工网络
        :return: 返回一个加载好的的图G对象
        """
        # <设置人工网络weight模块>

        # 多重无向图与无向图添加权重的方式不同,d就是属性字典,无向图中G.edges[u,v]是字典而多重无向图G.edges[u,v]不是
        for u, v, d in self.G.edges(data=True):  # 设置outside的行程时间
            self.G.edges[u, v, 0]['arcTime'] = 1
        for u, v, d in self.G.edges(data=True):
            self.G.edges[u, v, 0]['distance'] = 1

        return self.G

    def project(self, G, lng, lat):
        """
        将某个点的坐标按照欧式距离映射到网络中最近的拓扑点上
        :Param G: 拓扑图
        :Param lng: 经度
        :Param lat: 纬度
        :Return: 返回最近的点的OSMid
        """
        nearest_node = None
        shortest_distance = inf
        for n, d in G.nodes(data=True):
            # d['x']是经度，d['y']是纬度
            new_shortest_distance = ox.distance.euclidean_dist_vec(lng, lat, d['x'], d['y'])
            if new_shortest_distance < shortest_distance:
                nearest_node = n
                shortest_distance = new_shortest_distance
        return nearest_node, shortest_distance

    def modified_dijkstras(self, origin, destination):
        """
        最短路算法
        :return: 返回一个traveltime和path
        """
        count = 0
        paths_and_distances = {}
        for node in self.G.nodes():
            paths_and_distances[node] = [inf, [origin]]

        paths_and_distances[origin][0] = 0
        vertices_to_explore = [(0, origin)]

        while vertices_to_explore:
            current_distance, current_vertex = heappop(vertices_to_explore)
            for neighbor in self.G.neighbors(current_vertex):
                # get_edge_data得到的是嵌套字典
                edge_weight = self.G.get_edge_data(current_vertex, neighbor)[0]['arcTime']
                new_distance = current_distance + edge_weight
                new_path = paths_and_distances[current_vertex][1] + [neighbor]
                if new_distance < paths_and_distances[neighbor][0]:
                    paths_and_distances[neighbor][0] = new_distance
                    paths_and_distances[neighbor][1] = new_path
                    heappush(vertices_to_explore, (new_distance, neighbor))
                    count += 1
        return paths_and_distances[destination]

    def plot_path_evolution(G):

        plt.show()

    def plot_taxi_position(self, map=True, kind=0):

        if map == False:
            # 获取manhattan的networkx对象
            G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
            df_dataset = pd.read_csv("../train_dataset/dataset.csv")
            df_dataset['geometry'] = df_dataset.apply(
                lambda row: Point(float(row['pickup_longitude']), float(row['pickup_latitude'])), axis=1)
            df_dataset_geo = gpd.GeoDataFrame(df_dataset, crs=gdf_edges.crs, geometry=df_dataset.geometry)
            fig, ax = plt.subplots(figsize=(30, 30))
            df_dataset_geo.plot(ax=ax, color='green', markersize=1)
            gdf_edges.plot(ax=ax, cmap='Reds')
            ax.set_axis_off()
            plt.show()
        else:
            # 获取manhattan的networkx对象
            G = ox.graph_from_place('Manhattan, New York City, New York, USA', network_type='drive')
            # 将network对象转换成geodatafram对象
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
            df_dataset = pd.read_csv("../train_dataset/dataset.csv")
            if kind == 0:
                df_dataset['dist'] = df_dataset.apply(
                    lambda row: self.project(G, row['pickup_longitude'], row['pickup_latitude'])[1], axis=1)
                df_dataset = df_dataset[df_dataset['dist'] <= 0.001]
                df_dataset.to_csv("../train_dataset/processdataset.csv")
                # 绘制没映射之前的多层图
                df_dataset = pd.read_csv("../train_dataset/processdataset.csv")
                df_dataset['geometry'] = df_dataset.apply(
                    lambda row: Point(float(row['pickup_longitude']), float(row['pickup_latitude'])), axis=1)
                df_dataset_geo = gpd.GeoDataFrame(df_dataset, crs=gdf_edges.crs, geometry=df_dataset.geometry)
                fig, ax = plt.subplots(figsize=(30, 30))
                df_dataset_geo.plot(ax=ax, color='green', markersize=1)
                gdf_edges.plot(ax=ax, cmap='Reds')
                ax.set_axis_off()
                plt.show()
            elif kind == 1:
                df_dataset['dist'] = df_dataset.apply(
                    lambda row: self.project(G, row['dropoff_longitude'], row['dropoff_latitude'])[1], axis=1)
                df_dataset = df_dataset[df_dataset['dist'] <= 0.001]
                df_dataset.to_csv("../train_dataset/processdataset.csv")
                # 绘制没映射之前的多层图
                df_dataset = pd.read_csv("../train_dataset/processdataset.csv")
                df_dataset['geometry'] = df_dataset.apply(
                    lambda row: Point(float(row['dropoff_longitude']), float(row['dropoff_latitude'])), axis=1)
                df_dataset_geo = gpd.GeoDataFrame(df_dataset, crs=gdf_edges.crs, geometry=df_dataset.geometry)
                fig, ax = plt.subplots(figsize=(30, 30))
                df_dataset_geo.plot(ax=ax, color='green', markersize=1)
                gdf_edges.plot(ax=ax, cmap='Reds')
                ax.set_axis_off()
                plt.show()
            else:
                df_dataset['dist1'] = df_dataset.apply(
                    lambda row: self.project(G, row['pickup_longitude'], row['pickup_latitude'])[1], axis=1)
                df_dataset['dist2'] = df_dataset.apply(
                    lambda row: self.project(G, row['dropoff_longitude'], row['dropoff_latitude'])[1], axis=1)
                df_dataset = df_dataset[df_dataset['dist1'] <= 0.001 and df_dataset['dist2'] <= 0.001]
                df_dataset.to_csv("../train_dataset/processdataset.csv")
                # 绘制没映射之前的多层图
                df_dataset = pd.read_csv("../train_dataset/processdataset.csv")
                df_dataset['geometry'] = df_dataset.apply(lambda row: LineString(
                    [(float(row['pickup_longitude']), float(row['pickup_latitude'])),
                     (float(row['dropoff_longitude']), float(row['dropoff_latitude']))]), axis=1)
                df_dataset_geo = gpd.GeoDataFrame(df_dataset, crs=gdf_edges.crs, geometry=df_dataset.geometry)
                fig, ax = plt.subplots(figsize=(30, 30))
                df_dataset_geo.plot(ax=ax, color='green', markersize=1)
                gdf_edges.plot(ax=ax, cmap='Reds')
                ax.set_axis_off()
                plt.show()

    def plot_normal_path(self, origin, destination):

        # 载入文件模块
        df_nodelist = pd.read_csv('../train_dataset/normalnodelist.csv')

        # 使用Dijsktra算法求出最短路径的列表
        traveltime, path = self.modified_dijkstras(origin, destination)
        print(f'起点:{origin},终点:{destination},行程时间:{traveltime}')

        # 将network对象转换成geodatafram对象
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.G)

        os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建人工目录
        path_file = os.path.join('..', 'train_dataset', 'normal_path.csv')

        # 将点的经度和纬度更新到点的属性字典中
        for u, d in G.nodes(data=True):
            u_lng = df_nodelist[df_nodelist.node == u].values.squeeze()[1]
            u_lat = df_nodelist[df_nodelist.node == u].values.squeeze()[2]
            d['longitude'] = u_lng
            d['latitude'] = u_lat

        # dataframe只能存储纯文本
        with open(path_file, 'w') as f:
            f.write('index,node1_x,node1_y,node2_x,node2_y\n')
            for i in range(len(path) - 1):
                f.write('{0},{1},{2},{3},{4}\n'.format(i, self.G.nodes[path[i]]['longitude'],
                                                       self.G.nodes[path[i]]['latitude'],
                                                       self.G.nodes[path[i + 1]]['longitude'],
                                                       self.G.nodes[path[i + 1]]['latitude']))
                # 创建dataframe对象
        path_edges = pd.read_csv("../train_dataset/normal_path.csv")
        path_edges['geometry'] = path_edges.apply(
            lambda row: LineString([(row.node1_x, row.node1_y), (row.node2_x, row.node2_y)]), axis=1)
        # 创建geodataframe对象
        path_crs = {'init': 'epsg:4326'}
        gdf_path_edges = gpd.GeoDataFrame(path_edges, crs=path_crs, geometry=path_edges.geometry)

        # 绘制多层图
        fig, ax = plt.subplots(figsize=(10, 10))
        # column = 'arcTime' cmap = 'Reds
        gdf_edges.plot(ax=ax, column='arcTime', cmap='RdYlGn')
        # 按照类别绘制颜色，一个颜色一个类别
        gdf_path_edges.plot(ax=ax, color='black', categorical=True)
        ax.set_axis_off()
        plt.show()

    def plot_real_path(self, o_lng, o_lat, d_lng, d_lat):

        if self.manual == True:
            self.G = self.Graph()

        pickup_longitude = o_lng
        pickup_latitude = o_lat
        dropoff_longitude = d_lng
        dropoff_latitude = d_lat

        pickup_osmid = self.project(self.G, pickup_longitude, pickup_latitude)[0]
        projected_pickup_longitude = self.G.nodes[pickup_osmid]['x']
        projected_pickup_latitude = self.G.nodes[pickup_osmid]['y']
        dropoff_osmid = self.project(self.G, dropoff_longitude, dropoff_latitude)[0]
        projected_dropoff_longitude = self.G.nodes[dropoff_osmid]['x']
        projected_dropoff_latitude = self.G.nodes[dropoff_osmid]['y']

        pickup_tuple = (projected_pickup_longitude, projected_pickup_latitude)
        dropoff_tuple = (projected_dropoff_longitude, projected_dropoff_latitude)

        # 使用Dijsktra算法求出最短路径的列表
        traveltime, path = self.modified_dijkstras(pickup_osmid, dropoff_osmid)
        print(f'起点:{o_lng},{o_lat},终点:{d_lng},{d_lat},行程时间:{traveltime}')

        # 将network对象转换成geodatafram对象
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(self.G)

        os.makedirs(os.path.join('..', 'train_dataset'), exist_ok=True)  # 创建人工目录
        path_file = os.path.join('..', 'train_dataset', 'real_path.csv')
        # 创建路线的linesring对象
        # dataframe只能存储纯文本
        with open(path_file, 'w') as f:
            f.write('index,node1_x,node1_y,node2_x,node2_y\n')
            for i in range(len(path) - 1):
                f.write('{0},{1},{2},{3},{4}\n'.format(i, self.G.nodes[path[i]]['x'], self.G.nodes[path[i]]['y'],
                                                       self.G.nodes[path[i + 1]]['x'], self.G.nodes[path[i + 1]]['y']))
                # 创建dataframe对象
        path_edges = pd.read_csv("../train_dataset/real_path.csv")
        path_edges['geometry'] = path_edges.apply(
            lambda row: LineString([(row.node1_x, row.node1_y), (row.node2_x, row.node2_y)]), axis=1)
        # 创建geodataframe对象
        path_crs = {'init': 'epsg:4326'}
        gdf_path_edges = gpd.GeoDataFrame(path_edges, crs=path_crs, geometry=path_edges.geometry)

        # 绘制多层图
        fig, ax = plt.subplots(figsize=(20, 20))
        # column = 'arcTime' cmap = 'Reds
        gdf_edges.plot(ax=ax, color="red", categorical=True)
        # 按照类别绘制颜色，一个颜色一个类别
        gdf_path_edges.plot(ax=ax, color='black', categorical=True)
        ax.set_axis_off()
        plt.show()