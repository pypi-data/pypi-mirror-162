from __future__ import annotations

import dataclasses
import sys
from dataclasses import field
from typing import Any

import jax
import jax.numpy as jnp
import jax.tree_util as jtu
import numpy as np


def static_field(**kwargs):
    """ignore from pytree computations"""
    return field(**{**kwargs, **{"metadata": {"static": True}}})


def is_treeclass(model):
    """check if a class is treeclass"""
    return hasattr(model, "__tree_fields__")


def is_treeclass_leaf_bool(node):
    """assert if treeclass leaf is boolean (for boolen indexing)"""
    if isinstance(node, jnp.ndarray):
        return node.dtype == "bool"
    else:
        return isinstance(node, bool)


def is_treeclass_leaf(model):
    """assert if a node is treeclass leaf"""
    if is_treeclass(model):
        fields = model.__dataclass_fields__.values()

        return is_treeclass(model) and not any(
            [is_treeclass(model.__dict__[field.name]) for field in fields]
        )
    else:
        return False


def is_treeclass_equal(lhs, rhs):
    """Assert if two treeclasses are equal"""
    lhs_leaves, lhs_treedef = jtu.tree_flatten(lhs)
    rhs_leaves, rhs_treedef = jtu.tree_flatten(rhs)

    def is_node_equal(lhs_node, rhs_node):
        if isinstance(lhs_node, jnp.ndarray) and isinstance(rhs_node, jnp.ndarray):
            return jnp.array_equal(lhs_node, rhs_node)
        else:
            return lhs_node == rhs_node

    return (lhs_treedef == rhs_treedef) and all(
        [is_node_equal(lhs_leaves[i], rhs_leaves[i]) for i in range(len(lhs_leaves))]
    )


def is_excluded(fld: dataclasses.field, instance: Any) -> bool:
    """Check if a field is excluded

    Returns:
        bool: boolean if the field should be excluded or not.
    """
    val = instance.__dict__[fld.name]
    excluded_types = (str,)  # automatically excluded str from jax computations
    excluded_by_type = isinstance(val, excluded_types)
    excluded_by_meta = ("static" in fld.metadata) and fld.metadata["static"] is True  # fmt: skip
    return excluded_by_type or excluded_by_meta


def sequential_model_shape_eval(model, array):
    """Evaluate shape propagation of assumed sequential modules"""
    leaves = jtu.tree_leaves(model, is_treeclass_leaf)
    shape = [jax.eval_shape(lambda x: x, array)]
    for leave in leaves:
        shape += [jax.eval_shape(leave, shape[-1])]
    return shape


def _node_count_and_size(node):
    """calculate number and size of `trainable` and `non-trainable` parameters"""

    if isinstance(node, (jnp.ndarray, np.ndarray)):
        # inexact(trainable) array
        if jnp.issubdtype(node, jnp.inexact):
            count = complex(int(jnp.array(node.shape).prod()), 0)
            size = complex(int(node.nbytes), 0)

        # exact paramter
        else:
            count = complex(0, int(jnp.array(node.shape).prod()))
            size = complex(0, int(node.nbytes))

    # inexact non-array
    elif isinstance(node, (float, complex)):
        count = complex(1, 0)
        size = complex(sys.getsizeof(node), 0)

    # exact non-array
    elif isinstance(node, int):
        count = complex(0, 1)
        size = complex(sys.getsizeof(node), 0)

    # others
    else:
        count = complex(0, 0)
        size = complex(0, sys.getsizeof(node))

    return (count, size)


def _reduce_count_and_size(leaf):
    """reduce params count and params size of a tree of leaves"""

    def reduce_func(acc, node):
        lhs_count, lhs_size = acc
        rhs_count, rhs_size = _node_count_and_size(node)
        return (lhs_count + rhs_count, lhs_size + rhs_size)

    return jtu.tree_reduce(reduce_func, leaf, (complex(0, 0), complex(0, 0)))


def _freeze_nodes(model):
    """inplace freezing"""
    if is_treeclass(model):
        object.__setattr__(model, "__frozen_treeclass__", True)
        for kw, leaf in model.__dataclass_fields__.items():
            _freeze_nodes(model.__dict__[kw])
    return model


def _unfreeze_nodes(model):
    """inplace unfreezing"""
    if is_treeclass(model):
        object.__setattr__(model, "__frozen_treeclass__", False)
        for kw, leaf in model.__dataclass_fields__.items():
            _unfreeze_nodes(model.__dict__[kw])
    return model
