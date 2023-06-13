"""Test the io module."""
import tempfile
import os
import json

import numpy as np
from numpy.random import randint, randn
from scipy.sparse import random as sparse_random
from scipy.sparse import csr_matrix

import gli
import gli.io
from gli.io import Attribute


def test_save_single_homograph():
    """Test saving and loading a homograph.

    Create a temporary dir and save a homograph to it.
    Then load it back and compare the data.
    """
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a graph with 6 nodes and 5 edges
        edge = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])
        # Create attributes of the nodes.
        dense_node_feats = Attribute(
            name="DenseNodeFeature",
            data=randn(6, 5),  # 6 nodes, 5 features
            description="Dense node features.")
        sparse_node_feats = Attribute(
            name="SparseNodeFeature",
            data=sparse_random(6, 500),  # 6 nodes, 500 features
            description="Sparse node features.")
        node_labels = Attribute(
            name="NodeLabel",
            data=randint(0, 4, 6),  # 6 nodes, 4 classes
            description="Node labels.")
        edge_feats = Attribute(
            name="EdgeAttribute",
            data=randn(5, 3),  # 5 edges, 3 features
            description="Dense edge features.")
        sparse_edge_feats = Attribute(
            name="SparseEdgeAttribute",
            data=sparse_random(5, 500),  # 5 edges, 500 features
            description="Sparse edge features.")
        edge_labels = Attribute(
            name="EdgeLabel",
            data=randint(0, 4, 5),  # 5 edges, 4 classes
            description="Edge labels.")

        # Save the graph dataset.
        gli.io.save_homograph(
            name="example_dataset",
            edge=edge,
            node_attrs=[dense_node_feats, sparse_node_feats, node_labels],
            edge_attrs=[edge_feats, sparse_edge_feats, edge_labels],
            description="An exampmle dataset.",
            citation="some bibtex citation",
            save_dir=tmpdir)

        # Load the graph dataset.
        metadata_path = os.path.join(tmpdir, "metadata.json")
        _ = gli.graph.read_gli_graph(metadata_path)


def test_save_multi_homograph():
    """Test saving and loading a homograph.

    The data to be saved contains a node_graph_list.
    """
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a graph with 6 nodes and 5 edges (2 connected components)
        edge = np.array([[0, 1], [1, 2], [0, 2], [3, 4], [4, 5]])
        # Create attributes of the nodes.
        dense_node_feats = Attribute(
            name="DenseNodeFeature",
            data=randn(6, 5),  # 6 nodes, 5 features
            description="Dense node features.")
        sparse_node_feats = Attribute(
            name="SparseNodeFeature",
            data=sparse_random(6, 500),  # 6 nodes, 500 features
            description="Sparse node features.")
        node_labels = Attribute(
            name="NodeLabel",
            data=randint(0, 4, 6),  # 6 nodes, 4 classes
            description="Node labels.")
        edge_feats = Attribute(
            name="EdgeAttribute",
            data=randn(5, 3),  # 5 edges, 3 features
            description="Dense edge features.")
        sparse_edge_feats = Attribute(
            name="SparseEdgeAttribute",
            data=sparse_random(5, 500),  # 5 edges, 500 features
            description="Sparse edge features.")
        edge_labels = Attribute(
            name="EdgeLabel",
            data=randint(0, 4, 5),  # 5 edges, 4 classes
            description="Edge labels.")
        graph_node_list = np.array([
            [1, 1, 1, 0, 0, 0],  # 3 nodes in the first graph
            [0, 0, 0, 1, 1, 1]  # 3 nodes in the second graph
        ]).astype(np.int64)
        # transform graph_node_list to a scipy sparse matrix
        graph_node_list = csr_matrix(graph_node_list)

        # Save the graph dataset.
        gli.io.save_homograph(
            name="example_dataset",
            edge=edge,
            graph_node_list=graph_node_list,
            node_attrs=[dense_node_feats, sparse_node_feats, node_labels],
            edge_attrs=[edge_feats, sparse_edge_feats, edge_labels],
            description="An exampmle dataset.",
            citation="some bibtex citation",
            save_dir=tmpdir)

        # Load the graph dataset.
        metadata_path = os.path.join(tmpdir, "metadata.json")
        g = gli.graph.read_gli_graph(metadata_path)
        assert len(g) == 2, "The number of graphs should be 2."


def test_save_single_heterograph():
    """Save a single heterograph and load it back."""
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        node_groups = ["user", "item"]
        edge_groups = [("user", "click", "item"), ("user", "purchase", "item"),
                       ("user", "is_friend", "user")]
        # Create a sample graph with 3 user nodes and 4+1 item nodes.
        edge = {
            edge_groups[0]: np.array([[0, 0], [0, 1], [1, 2], [2, 3]]),
            edge_groups[1]: np.array([[0, 1], [1, 2]]),
            edge_groups[2]: np.array([[0, 1], [2, 1]])
        }

        node_attrs = {
            node_groups[0]: [
                Attribute("UserDenseFeature", randn(3, 5),
                          "Dense user features."),
                Attribute("UserSparseFeature", sparse_random(3, 500),
                          "Sparse user features."),
            ],
            node_groups[1]: [
                Attribute("ItemDenseFeature", randn(5, 5),
                          "Dense item features.")
            ]
        }

        edge_attrs = {
            edge_groups[0]: [
                Attribute("ClickTime", randn(4, 1), "Click time.")
            ],
            edge_groups[1]: [
                Attribute("PurchaseTime", randn(2, 1), "Purchase time.")
            ],
            edge_groups[2]: [
                Attribute("SparseFriendFeature", sparse_random(2, 500),
                          "Sparse friend features."),
                Attribute("DenseFriendFeature", randn(2, 5),
                          "Dense friend features.")
            ]
        }

        num_nodes_dict = {
            node_groups[0]: 3,
            node_groups[1]:
                5  # more than the actual number of items in the edges
        }

        # Save the graph dataset.
        gli.io.save_heterograph(name="example_hetero_dataset",
                                edge=edge,
                                num_nodes_dict=num_nodes_dict,
                                node_attrs=node_attrs,
                                edge_attrs=edge_attrs,
                                description="An example heterograph dataset.",
                                save_dir=tmpdir)

        # Load the graph dataset.
        metadata_path = os.path.join(tmpdir, "metadata.json")
        g = gli.graph.read_gli_graph(metadata_path)

        print(g)
        assert g.num_nodes() == 8, "The number of nodes should be 8."
        assert g.num_nodes("user") == 3, \
            "The number of user nodes should be 3."
        assert g.num_nodes("item") == 5, \
            "The number of item nodes should be 5."
        assert g.num_edges() == 8, \
            "The number of edges should be 8."
        assert g.num_edges("user_click_item") == 4, \
            "The number of click edges should be 4."
        assert g.num_edges("user_is_friend_user") == 2, \
            "The number of friend edges should be 2."


def test_save_task_graph_regression():
    """Save a single graph regression task and load it back."""
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        _description = "A graph regression task for the example dataset."
        _feature = ["Node/DenseNodeFeature", "Node/SparseNodeFeature"]
        _target = "Graph/GraphLabel"
        train_set = [0, 1]
        val_set = [2, 3]
        test_set = [4, 5]

        # Save the task information.
        d = gli.io.save_task_graph_regression(
            name="example_dataset",
            description=_description,
            feature=_feature,
            target=_target,
            train_set=train_set,
            val_set=val_set,
            test_set=test_set,
            task_id=1,
            save_dir=tmpdir)
        
        # Load the task dataset.
        task_path = os.path.join(tmpdir, "task_graph_regression_1.json")
        t = gli.task.read_gli_task(task_path)

        assert t.description == _description, \
            "description should be %s" % _description
        assert t.features == _feature, "features should be %s" % _feature
        assert t.target == _target, "target should be %s" % _target
        assert t.split.get("train_set").tolist() == train_set, \
            "train set should be %s" % train_set
        assert t.split.get("val_set").tolist() == val_set, \
            "val set should be %s" % val_set
        assert t.split.get("test_set").tolist() == test_set, \
            "test set should be %s" % test_set


def test_save_task_graph_classification():
    """Save a single graph classification task and load it back."""
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        _description = "A graph classification task for the example dataset."
        _feature = ["Node/DenseNodeFeature", "Node/SparseNodeFeature"]
        _target = "Graph/GraphLabel"
        _num_classes = 4
        train_set = [0, 1]
        val_set = [2, 3]
        test_set = [4, 5]

        # Save the task information.
        d = gli.io.save_task_graph_classification(
            name="example_dataset",
            description=_description,
            feature=_feature,
            target=_target,
            num_classes=_num_classes,
            train_set=train_set,
            val_set=val_set,
            test_set=test_set,
            task_id=1,
            save_dir=tmpdir)

        # Load the task dataset.
        task_path = os.path.join(tmpdir, "task_graph_classification_1.json")
        t = gli.task.read_gli_task(task_path)

        assert t.description == _description, \
            "description should be %s" % _description
        assert t.features == _feature, "features should be %s" % _feature
        assert t.target == _target, "target should be %s" % _target
        assert t.num_classes == _num_classes, \
            "number of classes should be %s" % _num_classes
        assert t.split.get("train_set").tolist() == train_set, \
            "train set should be %s" % train_set
        assert t.split.get("val_set").tolist() == val_set, \
            "val set should be %s" % val_set
        assert t.split.get("test_set").tolist() == test_set, \
            "test set should be %s" % test_set


def test_save_task_link_prediction():
    """Save a single link prediction task and load it back."""
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        _description = "A link prediction task for the example dataset."
        _feature = ["Node/DenseNodeFeature", "Node/SparseNodeFeature"]
        train_set = [0, 1]
        val_set = [2, 3]
        test_set = [4, 5]

        # Save the task information.
        d = gli.io.save_task_link_prediction(
            name="example_dataset",
            description=_description,
            feature=_feature,
            train_set=train_set,
            val_set=val_set,
            test_set=test_set,
            task_id=1,
            save_dir=tmpdir)

        # Load the task dataset.
        task_path = os.path.join(tmpdir, "task_link_prediction_1.json")
        t = gli.task.read_gli_task(task_path)

        assert t.description == _description, \
            "description should be %s" % _description
        assert t.features == _feature, "features should be %s" % _feature
        assert t.split.get("train_set").tolist() == train_set, \
            "train set should be %s" % train_set
        assert t.split.get("val_set").tolist() == val_set, \
            "val set should be %s" % val_set
        assert t.split.get("test_set").tolist() == test_set, \
            "test set should be %s" % test_set


def test_save_task_time_dependent_link_prediction():
    """Save a single time dependent link prediction task and load it back."""
    # Create a temporary dir.
    _description = "A time dependent link prediction task for the \
                example dataset."
    _feature = ["Node/DenseNodeFeature", "Node/SparseNodeFeature"]
    _time = time="Edge/EdgeYear"
    with tempfile.TemporaryDirectory() as tmpdir:
        d = gli.io.save_task_time_dependent_link_prediction(
            name="example_dataset",
            description=_description,
            feature=_feature,
            time="Edge/EdgeYear",
            task_id=1,
            save_dir=tmpdir)

        # Load the task dataset.
        task_path = os.path.join(tmpdir, \
                                 "task_time_dependent_link_prediction_1.json")
        t = gli.task.read_gli_task(task_path)

        assert t.description == _description, \
            "description should be %s" % _description
        assert t.features == _feature, "features should be %s" % _feature
        assert t.time == _time, "time should be %s" % _time


def test_save_task_kg_entity_prediction():
    """Save a kg entity prediction task and load it back."""
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        _description = "A kg entity prediction task for the example dataset."
        _feature = ["Node/DenseNodeFeature", "Node/SparseNodeFeature"]
        train_triplet_set = [0, 1]
        val_triplet_set = [2, 3]
        test_triplet_set = [4, 5]

        # Save the task information.
        d = gli.io.save_task_kg_entity_prediction(
            name="example_dataset",
            description=_description,
            feature=_feature,
            train_triplet_set=train_triplet_set,
            val_triplet_set=val_triplet_set,
            test_triplet_set=test_triplet_set,
            task_id=1,
            save_dir=tmpdir)
        
        # Load the task dataset.
        task_path = os.path.join(tmpdir, "task_kg_entity_prediction_1.json")
        t = gli.task.read_gli_task(task_path)

        assert t.description == _description, \
            "description should be %s" % _description
        assert t.features == _feature, "features should be %s" % _feature
        assert t.split.get("train_set").tolist() == train_triplet_set, \
            "train set should be %s" % train_triplet_set
        assert t.split.get("val_set").tolist() == val_triplet_set, \
            "val set should be %s" % val_triplet_set
        assert t.split.get("test_set").tolist() == test_triplet_set, \
            "test set should be %s" % test_triplet_set


def test_save_task_kg_relation_prediction():
    """Save a kg relation prediction task and load it back."""
    # Create a temporary dir.
    with tempfile.TemporaryDirectory() as tmpdir:
        _description = "A kg entity prediction task for the example dataset."
        _feature = ["Node/DenseNodeFeature", "Node/SparseNodeFeature"]
        _target = "Edge/EdgeClass"
        train_triplet_set = [0, 1]
        val_triplet_set = [2, 3]
        test_triplet_set = [4, 5]

        # Save the task information.
        d = gli.io.save_task_kg_relation_prediction(
            name="example_dataset",
            description=_description,
            feature=_feature,
            target=_target,
            train_triplet_set=train_triplet_set,
            val_triplet_set=val_triplet_set,
            test_triplet_set=test_triplet_set,
            task_id=1,
            save_dir=tmpdir)

        # Load the task dataset.
        task_path = os.path.join(tmpdir, "task_kg_relation_prediction_1.json")
        t = gli.task.read_gli_task(task_path)

        assert t.description == _description, \
            "description should be %s" % _description
        assert t.features == _feature, "features should be %s" % _feature
        assert t.target == _target, "target should be %s" % _target
        assert t.split.get("train_set").tolist() == train_triplet_set, \
            "train set should be %s" % train_triplet_set
        assert t.split.get("val_set").tolist() == val_triplet_set, \
            "val set should be %s" % val_triplet_set
        assert t.split.get("test_set").tolist() == test_triplet_set, \
            "test set should be %s" % test_triplet_set

if __name__ == '__main__':
    test_save_task_kg_relation_prediction()