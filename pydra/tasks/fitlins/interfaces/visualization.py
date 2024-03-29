from pkg_resources import resource_filename
try:
    from typing import Literal  # raises a mypy error for <3.8, doesn't for >=3.8
except ImportError:
    try:
        from typing_extensions import Literal
    except ImportError:
        Literal = None
import numpy as np
import pandas as pd
import nibabel as nb
from nilearn import plotting as nlp
from collections import namedtuple

from pydra.engine.helpers_file import fname_presuffix, split_filename
from pydra.engine.specs import File, SpecInfo, BaseSpec
from pydra.engine.task import FunctionTask

from ..viz import plot_and_save, plot_corr_matrix, plot_contrast_matrix

Visualization_input_fields = [
    (
        "data",
        File,
        {
            "help_string":"Data file to visualize",
            "mandatory": True,
        },
    ),
    (
        "image_type",
        Literal["svg", "png"],
        {
            "help_string": "image type",
            "mandatory": True,
        }
    )
]


Visualization_input_spec = SpecInfo(
    name="VisualizationInputSpec",
    fields=Visualization_input_fields,
    bases=(BaseSpec,),
)

Visualization_output_fields = [
    (
        "figure",
        File,
        {
            "help_string": "Visualization"
        }
    )
]


Visualization_output_spec = SpecInfo(
    name="VisualizationOutputSpec",
    fields=Visualization_output_fields,
    bases=(BaseSpec,),
)

class Visualization(FunctionTask):
    input_spec = Visualization_input_spec
    output_spec = Visualization_output_spec

    def _run_interface(self, runtime):
        import matplotlib

        matplotlib.use('Agg')
        import seaborn as sns
        from matplotlib import pyplot as plt

        sns.set_style('white')
        plt.rcParams['svg.fonttype'] = 'none'
        plt.rcParams['image.interpolation'] = 'nearest'

        data = self._load_data(self.inputs.data)
        out_name = fname_presuffix(
            self.inputs.data,
            suffix='.' + self.inputs.image_type,
            newpath=runtime.cwd,
            use_ext=False,
        )
        self._visualize(data, out_name)
        self._results['figure'] = out_name
        return runtime

    def _load_data(self, fname):
        _, _, ext = split_filename(fname)
        if ext == '.tsv':
            return pd.read_table(fname, index_col=0)
        elif ext in ('.nii', '.nii.gz', '.gii'):
            return nb.load(fname)
        raise ValueError("Unknown file type!")


class DesignPlot(Visualization):
    def _visualize(self, data, out_name):
        from matplotlib import pyplot as plt

        plt.set_cmap('viridis')
        plot_and_save(out_name, nlp.plot_design_matrix, data)


        
DesignCorrelationPlot_input_fields = [
    (
        "contrast_info",
        list,
        {
            "help_string": "contrast information"
        }
    )
]

DesignCorrelationPlot_input_spec = SpecInfo(
    name="DesignCorrelationPlotInputSpec",
    fields=DesignCorrelationPlot_input_fields,
    bases=(BaseSpec,),
)


class DesignCorrelationPlot(Visualization):
    input_spec = DesignCorrelationPlot_input_spec

    def _visualize(self, data, out_name):
        columns = []
        names = []
        contrast_info = self.inputs.contrast_info

        for c in contrast_info:
            columns = list(set(c['conditions']) | set(columns))
            # split f-tests with 2d weights into 2 rows and append
            # the condition to the name to create a unique name
            if len(np.array(c['weights']).shape) > 1:
                for cond in c['conditions']:
                    names.append(c['name'] + '_' + cond)
            else:
                names.append(c['name'])

        contrast_matrix = pd.DataFrame(
            np.zeros((len(names), len(columns))), columns=columns, index=names
        )

        for i, c in enumerate(contrast_info):
            if len(np.array(c['weights']).shape) > 1:
                for cond in c['conditions']:
                    name = c['name'] + '_' + cond
                    contrast_matrix.loc[name][c['conditions']] = c['weights'][
                        c['conditions'].index(cond)
                    ]
            else:
                contrast_matrix.loc[c['name']][c['conditions']] = c['weights']

        all_cols = list(data.columns)
        evs = set(contrast_matrix.index)
        if set(contrast_matrix.index) != all_cols[: len(evs)]:
            ev_cols = [col for col in all_cols if col in evs]
            confound_cols = [col for col in all_cols if col not in evs]
            data = data[ev_cols + confound_cols]
        plot_and_save(
            out_name,
            plot_corr_matrix,
            data.drop(columns='constant', errors='ignore').corr(),
            len(evs),
        )



ContrastMatrixPlot_input_fields = [
    (
        "contrast_info",
        list,
        {
            "help_string": "contrast information",
            "mandatory": True,
            
        },
    ),
    (
        "orientation",
        str,
        {
            "allowed_values": ["vertical", "horizontal"], #need to set a default value
            "help_string": "Display orientation of contrast matrix",
            "mandatory": True,
            
        },
    ),
]
        
ContrastMatrixPlot_input_spec = SpecInfo(
    name="ContrastMatrixPlotInputSpec",
    fields=ContrastMatrixPlot_input_fields,
    bases=(BaseSpec,),
)


class ContrastMatrixPlot(Visualization):
    input_spec = ContrastMatrixPlot_input_spec

    def _visualize(self, data, out_name):
        columns = []
        names = []
        contrast_info = self.inputs.contrast_info

        for c in contrast_info:
            columns = list(set(c['conditions']) | set(columns))
            # split f-tests with a 2d weights into 2 rows
            if len(np.array(c['weights']).shape) > 1:
                for cond in c['conditions']:
                    names.append(c['name'] + '_' + cond)
            else:
                names.append(c['name'])

        contrast_matrix = pd.DataFrame(
            np.zeros((len(names), len(columns))), columns=columns, index=names
        )

        for i, c in enumerate(contrast_info):
            if len(np.array(c['weights']).shape) > 1:
                for cond in c['conditions']:
                    name = c['name'] + '_' + cond
                    contrast_matrix.loc[name][c['conditions']] = c['weights'][
                        c['conditions'].index(cond)
                    ]
            else:
                contrast_matrix.loc[c['name']][c['conditions']] = c['weights']

        if 'constant' in contrast_matrix.index:
            contrast_matrix = contrast_matrix.drop(index='constant')
        plot_and_save(
            out_name, plot_contrast_matrix, contrast_matrix, ornt=self.inputs.orientation
        )


GlassBrainPlot_input_fields = [
    (
        "threshold",
        float, #traits.Enum('auto', None, traits.Float(), usedefault=True)
        {
            "help_string": "threshold",
            "default": "auto"
        },
    ),
    (
        "vmax",
        float,
        {
            "help_string": "vmax",
        },
    ),
    (
        "colormap",
        str,
        {
            "help_string": "color map",
            "default": "bwr",
        }
    )
]        

        
GlassBrainPlot_input_spec = SpecInfo(
    name="GlassBrainPlotInputSpec",
    fields=GlassBrainPlot_input_fields,
    bases=(BaseSpec,),
)


class GlassBrainPlot(Visualization):
    input_spec = GlassBrainPlot_input_spec

    def _visualize(self, data, out_name):
        import numpy as np

        vmax = self.inputs.vmax
        if vmax in [None, attr.NOTHING]:
            vmax = None
            abs_data = np.abs(data.get_fdata(dtype=np.float32))
            pctile99 = np.percentile(abs_data, 99.99)
            if abs_data.max() - pctile99 > 10:
                vmax = pctile99
        if isinstance(data, nb.Cifti2Image):
            plot_dscalar(
                data,
                vmax=vmax,
                threshold=self.inputs.threshold,
                cmap=self.inputs.colormap,
                output_file=out_name,
            )
        else:
            nlp.plot_glass_brain(
                data,
                colorbar=True,
                plot_abs=False,
                display_mode='lyrz',
                axes=None,
                vmax=vmax,
                threshold=self.inputs.threshold,
                cmap=self.inputs.colormap,
                output_file=out_name,
            )


def plot_dscalar(
    img,
    colorbar=True,
    plot_abs=False,
    vmax=None,
    threshold=None,
    cmap='cold_hot',
    output_file=None,
):
    import matplotlib as mpl
    from matplotlib import pyplot as plt

    subcort, ltexture, rtexture = decompose_dscalar(img)
    fig = plt.figure(figsize=(11, 9))
    ax1 = plt.subplot2grid((3, 2), (0, 0), projection='3d')
    ax2 = plt.subplot2grid((3, 2), (0, 1), projection='3d')
    ax3 = plt.subplot2grid((3, 2), (1, 0), projection='3d')
    ax4 = plt.subplot2grid((3, 2), (1, 1), projection='3d')
    ax5 = plt.subplot2grid((3, 2), (2, 0), colspan=2)
    surf_fmt = 'data/conte69/tpl-conte69_hemi-{hemi}_space-fsLR_den-32k_inflated.surf.gii'.format
    lsurf = nb.load(resource_filename('fitlins', surf_fmt(hemi='L'))).agg_data()
    rsurf = nb.load(resource_filename('fitlins', surf_fmt(hemi='R'))).agg_data()
    kwargs = {
        'threshold': None if threshold == 'auto' else threshold,
        'colorbar': False,
        'plot_abs': plot_abs,
        'cmap': cmap,
        'vmax': vmax,
    }
    nlp.plot_surf_stat_map(lsurf, ltexture, view='lateral', axes=ax1, **kwargs)
    nlp.plot_surf_stat_map(rsurf, rtexture, view='medial', axes=ax2, **kwargs)
    nlp.plot_surf_stat_map(lsurf, ltexture, view='medial', axes=ax3, **kwargs)
    nlp.plot_surf_stat_map(rsurf, rtexture, view='lateral', axes=ax4, **kwargs)
    nlp.plot_glass_brain(subcort, display_mode='lyrz', axes=ax5, **kwargs)
    if colorbar:
        data = img.get_fdata(dtype=np.float32)
        if vmax is None:
            vmax = max(-data.min(), data.max())
        norm = mpl.colors.Normalize(vmin=-vmax if data.min() < 0 else 0, vmax=vmax)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        fig.colorbar(sm, ax=fig.axes, location='right', aspect=50)
    if output_file:
        fig.savefig(output_file)
        plt.close(fig)


def decompose_dscalar(img):
    data = img.get_fdata(dtype=np.float32)
    ax = img.header.get_axis(1)
    vol = np.zeros(ax.volume_shape, dtype=np.float32)
    vox_indices = tuple(ax.voxel[ax.volume_mask].T)
    vol[vox_indices] = data[:, ax.volume_mask]
    subcort = nb.Nifti1Image(vol, ax.affine)

    surfs = {}
    for name, indices, brainmodel in ax.iter_structures():
        if not name.startswith('CIFTI_STRUCTURE_CORTEX_'):
            continue
        hemi = name.split('_')[3].lower()
        texture = np.zeros(brainmodel.vertex.max() + 1, dtype=np.float32)
        texture[brainmodel.vertex] = data[:, indices]
        surfs[hemi] = texture

    return subcort, surfs['left'], surfs['right']