"""Abstract interfaces for design matrix creation and estimation
Estimator tools should be subclassed from these interfaces, ensuring
trivial swapping of one tool for another at single points. For example,
if there is interest in comparing the design matrix construction between
tools without changing estimators, a new ``DesignMatrixInterface``
subclass can be written and swapped in without demanding that an estimator
also be written.
"""

from pydra.engine.specs import File, SpecInfo, BaseSpec
from pydra.engine.task import FunctionTask
import typing as ty

designmtx_input_fields = [
    (
        "bold_file",
        File,
        {
            "help_string": "bold file",
            "mandatory": True,
        },
    ),
    (
        "design_info",
        dict, #trait.api.Dict()
        {
            "help_string": "design info",
        },
    ),
    (
        "drop_missing",
        bool,
        {
            "help_string": "Drop columns in design matrix with all missing values"
        },
    ),
    (
        "drift_model",
        str, #trait.api.Either(trait.api.String(), None)
        {
            "help_string": "Optional drift model to apply to design matrix"
        }
    )
]

designmtx_input_spec = SpecInfo(
    name="DesignMatrixInputSpec",
    fields=designmtx_input_fields,
    bases=(BaseSpec,),
)


designmtx_output_fields = [
    (
        "design_matrix",
        File,
        {
            "help_string": "design matrix",
        },
    )
]

designmtx_output_spec = SpecInfo(
    name="DesignMatrixOutputSpec",
    fields=designmtx_output_fields,
    bases=(BaseSpec,),
)


class DesignMatrixInterface(FunctionTask):
    input_spec = designmtx_input_spec
    output_spec = designmtx_output_spec
    
    
firstlevel_estimator_input_fields = [
    (
        "bold_file",
        File,
        {
            "help_string": "bold file",
            "mandatory": True,
        },
    ),
    (
        "mask_file",
        File,
        {
            "help_string": "mask file",
        },
    ),
    (
        "design_matrix",
        File,
        {
            "help_string": "design matrix",
            "mandatory": True
        },
    ),
    (
        "spec",
        dict, #trait.api.Dict()
        {
            "help_string": "spec",
        },
    ),
    (
        "smoothing_fwhm",
        float,
        {
            "help_string": "Full-width half max (FWHM) in mm for smoothing in mask",
        },
    ),
    (
        "smoothing_type",
        str, #trait.api.Enum('iso', 'isoblurto')
        {
            "allowed_values": ["iso", "isoblurto"],
            "help_string": "Type of smoothing (iso or isoblurto)'",
        }
        
    )
]


firstlevel_estimator_input_spec = SpecInfo(
    name="FirstLevelEstimatorInputSpec",
    fields=firstlevel_estimator_input_fields,
    bases=(BaseSpec,),
)

    
estimator_output_spec = [
    (
        "effect_maps",
        list, #trait.api.List(File)
        {
            "help_string": "effect maps",
        },
    ),
    (
        "variance_maps",
        list, #trait.api.List(File)
        {
            "help_string": "variance maps",
        },
    ),
    (
        "stat_maps",
        list, #trait.api.List(File)
        {
            "help_string": "stat maps",
        },
    ),
    (
        "zscore_maps",
        list, #trait.api.List(File)
        {
            "help_string": "zscore maps",
        },
    ),
    (
        "pvalue_maps",
        list, #trait.api.List(File)
        {
            "help_string": "pvalue maps",
        },
    ),
    (
        "contrast_metadata",
        list, #trait.api.List(Dict)
        {
            "help_string": "contrast metadata",
        },
    ),
    (
        "model_maps",
        list, #trait.api.List(File)
        {
            "help_string": "model maps",
        },
    ),
    (
        "model_metadata",
        list, #trait.api.List(Dict)
        {
            "help_string": "model metadata",
        },
    ),
]

estimator_output_spec = SpecInfo(
    name="EstimatorOutputSpec",
    fields=estimator_output_spec,
    bases=(BaseSpec,),
)


    
class FirstLevelEstimatorInterface(FunctionTask):
    input_spec = firstlevel_estimator_input_spec
    output_spec = estimator_output_spec


secondlevel_estimator_input_fields = [
    (
        "effect_maps",
        list, #trait.api.List(File)
        {
            "help_string": "effect maps",
            "mandatory": True,
        },
    ),
    (
        "variance_maps",
        list, #trait.api.List(File)
        {
            "help_string": "variance maps",
        },
    ),
    (
        "stat_metadata",
        list, #trait.api.List(File)
        {
            "help_string": "stat metadata",
            "mandatory": True
        },
    ),
    (
        "spec",
        dict, #trait.api.Dict()
        {
            "help_string": "spec",
        },
    ),
    (
        "smoothing_fwhm",
        float,
        {
            "help_string": "Full-width half max (FWHM) in mm for smoothing in mask",
        },
    ),
    (
        "smoothing_type",
        str, # trait.api.Enum('iso', 'isoblurto')
        {
            "allowed_values": ["iso", "isoblurto"],
            "help_string": "Type of smoothing (iso or isoblurto)'",
        }
        
    )
]
    
secondlevel_estimator_input_spec = SpecInfo(
    name="SecondLevelEstimatorInputSpec",
    fields=secondlevel_estimator_input_fields,
    bases=(BaseSpec,),
)



secondlevel_estimator_output_fields = [
    (
        "contrast_metadata",
        list, #trait.api.List(Dict)
        {
            "help_string": "contrast metadata"
        }
    )
]
    
secondlevel_estimator_output_spec = SpecInfo(
    name="SecondLevelEstimatoroutputSpec",
    fields=secondlevel_estimator_output_fields,
    bases=(BaseSpec,),
)



class SecondLevelEstimatorInterface(FunctionTask):
    input_spec = secondlevel_estimator_input_spec
    output_spec = secondlevel_estimator_output_spec