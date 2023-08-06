

""""""# start delvewheel patch
def _delvewheel_init_patch_0_0_22():
    import os
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))
    if sys.version_info[:2] >= (3, 8):
        conda_workaround = os.path.exists(os.path.join(sys.base_prefix, 'conda-meta')) and (sys.version_info[:3] < (3, 8, 13) or (3, 9, 0) <= sys.version_info[:3] < (3, 9, 9))
        if conda_workaround:
            # backup the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            conda_dll_search_modification_enable = os.environ.get('CONDA_DLL_SEARCH_MODIFICATION_ENABLE')
            os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = '1'
        os.add_dll_directory(libs_dir)
        if conda_workaround:
            # restore the state of the environment variable CONDA_DLL_SEARCH_MODIFICATION_ENABLE
            if conda_dll_search_modification_enable is None:
                os.environ.pop('CONDA_DLL_SEARCH_MODIFICATION_ENABLE', None)
            else:
                os.environ['CONDA_DLL_SEARCH_MODIFICATION_ENABLE'] = conda_dll_search_modification_enable
    else:
        from ctypes import WinDLL
        with open(os.path.join(libs_dir, '.load-order-gpytoolbox-0.0.1')) as file:
            load_order = file.read().split()
        for lib in load_order:
            WinDLL(os.path.join(libs_dir, lib))


_delvewheel_init_patch_0_0_22()
del _delvewheel_init_patch_0_0_22
# end delvewheel patch

# This function depends on skimage 
from .png2poly import png2poly

# These functions depend ONLY on numpy, scipy and each other
from .linear_elasticity import linear_elasticity
from .linear_elasticity_stiffness import linear_elasticity_stiffness
from .edge_indices import edge_indices
from .regular_square_mesh import regular_square_mesh
from .regular_cube_mesh import regular_cube_mesh
from .signed_distance_polygon import signed_distance_polygon
from .metropolis_hastings import metropolis_hastings
from .ray_polyline_intersect import ray_polyline_intersect
from .poisson_surface_reconstruction import poisson_surface_reconstruction
from .fd_interpolate import fd_interpolate
from .fd_grad import fd_grad
from .fd_partial_derivative import fd_partial_derivative
from .random_points_on_polyline import random_points_on_polyline
from .normalize_points import normalize_points
from .write_ply import write_ply
from .initialize_quadtree import initialize_quadtree
from .subdivide_quad import subdivide_quad
from .in_quadtree import in_quadtree
from .quadtree_gradient import quadtree_gradient
from .quadtree_laplacian import quadtree_laplacian
from .quadtree_boundary import quadtree_boundary
from .quadtree_children import quadtree_children
from .grad import grad
from .doublearea import doublearea
from .doublearea_intrinsic import doublearea_intrinsic
from .volume import volume
from .massmatrix import massmatrix
from .massmatrix_intrinsic import massmatrix_intrinsic
from .halfedges import halfedges
from .edges import edges
from .boundary_loops import boundary_loops
from .boundary_edges import boundary_edges
from .boundary_vertices import boundary_vertices
from .min_quad_with_fixed import min_quad_with_fixed
from .min_quad_with_fixed import min_quad_with_fixed_precompute
from .fixed_dof_solve import fixed_dof_solve
from .fixed_dof_solve import fixed_dof_solve_precompute
from .halfedge_lengths import halfedge_lengths
from .halfedge_lengths_squared import halfedge_lengths_squared
from .cotangent_laplacian_intrinsic import cotangent_laplacian_intrinsic
from .tip_angles import tip_angles
from .tip_angles_intrinsic import tip_angles_intrinsic
from .cotangent_laplacian import cotangent_laplacian
from .cotangent_weights_intrinsic import cotangent_weights_intrinsic
from .cotangent_weights import cotangent_weights
from .remove_duplicate_vertices import remove_duplicate_vertices
from .bad_quad_mesh_from_quadtree import bad_quad_mesh_from_quadtree
from .per_face_normals import per_face_normals
from .per_vertex_normals import per_vertex_normals
from .triangle_triangle_adjacency import triangle_triangle_adjacency
from .halfedge_edge_map import halfedge_edge_map
from .array_correspondence import array_correspondence
from .subdivide import subdivide
from .read_mesh import read_mesh
from .write_mesh import write_mesh
# from .do_meshes_intersect import do_meshes_intersect
# from .mesh_boolean import mesh_boolean
from .decimate import decimate
from .in_element_aabb import in_element_aabb
from .ray_mesh_intersect import ray_mesh_intersect
from .remesh_botsch import remesh_botsch
from .upper_envelope import upper_envelope
# from .lazy_cage import lazy_cage
from .colormap import colormap
from .apply_colormap import apply_colormap
from .offset_surface import offset_surface