"""Abstract interfaces for design matrix creation and estimation
Estimator tools should be subclassed from these interfaces, ensuring
trivial swapping of one tool for another at single points. For example,
if there is interest in comparing the design matrix construction between
tools without changing estimators, a new ``DesignMatrixInterface``
subclass can be written and swapped in without demanding that an estimator
also be written.
"""

from pydra.engine.specs import File, MultiOutputFile, SpecInfo, BaseSpec
from pydra.engine.task import FunctionTask
from typing import Union
try:
    from typing import Literal  # raises a mypy error for <3.8, doesn't for >=3.8
except ImportError:
    try:
        from typing_extensions import Literal
    except ImportError:
        Literal = None

DesignMatrix_input_fields = [
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
        dict, 
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
        Union[str, None],
        {
            "help_string": "Optional drift model to apply to design matrix"
        }
    )
]

DesignMatrix_input_spec = SpecInfo(
    name="DesignMatrixInputSpec",
    fields=DesignMatrix_input_fields,
    bases=(BaseSpec,),
)


DesignMatrix_output_fields = [
    (
        "design_matrix",
        File,
        {
            "help_string": "design matrix",
        },
    )
]

DesignMatrix_output_spec = SpecInfo(
    name="DesignMatrixOutputSpec",
    fields=DesignMatrix_output_fields,
    bases=(BaseSpec,),
)


class DesignMatrixInterface(FunctionTask):
    input_spec = DesignMatrix_input_spec
    output_spec = DesignMatrix_output_spec
    
    
FirstLevelEstimator_input_fields = [
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
        Union[File, None],
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
        dict, 
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
        Literal["iso", "isoblurto"], 
        {
            "help_string": "Type of smoothing (iso or isoblurto)'",
        }
        
    )
]


FirstLevelEstimator_input_spec = SpecInfo(
    name="FirstLevelEstimatorInputSpec",
    fields=FirstLevelEstimator_input_fields,
    bases=(BaseSpec,),
)

    
Estimator_output_spec = [
    (
        "effect_maps",
        MultiOutputFile, 
        {
            "help_string": "effect maps",
        },
    ),
    (
        "variance_maps",
        MultiOutputFile, 
        {
            "help_string": "variance maps",
        },
    ),
    (
        "stat_maps",
        MultiOutputFile, 
        {
            "help_string": "stat maps",
        },
    ),
    (
        "zscore_maps",
        MultiOutputFile, 
        {
            "help_string": "zscore maps",
        },
    ),
    (
        "pvalue_maps",
        MultiOutputFile, 
        {
            "help_string": "pvalue maps",
        },
    ),
    (
        "contrast_metadata",
        list[dict], 
        {
            "help_string": "contrast metadata",
        },
    ),
    (
        "model_maps",
        MultiOutputFile, 
        {
            "help_string": "model maps",
        },
    ),
    (
        "model_metadata",
        list[dict], 
        {
            "help_string": "model metadata",
        },
    ),
]

Estimator_output_spec = SpecInfo(
    name="EstimatorOutputSpec",
    fields=Estimator_output_spec,
    bases=(BaseSpec,),
)


    
class FirstLevelEstimatorInterface(FunctionTask):
    input_spec = FirstLevelEstimator_input_spec
    output_spec = Estimator_output_spec


SecondLevelEstimator_input_fields = [
    (
        "effect_maps",
        list(list(File)),
        {
            "help_string": "effect maps",
            "mandatory": True,
        },
    ),
    (
        "variance_maps",
        list(list(File)), 
        {
            "help_string": "variance maps",
        },
    ),
    (
        "stat_metadata",
        list(list(dict)), 
        {
            "help_string": "stat metadata",
            "mandatory": True
        },
    ),
    (
        "spec",
        dict, 
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
        ty.Literal("iso", "isoblurto"), 
        {
            "help_string": "Type of smoothing (iso or isoblurto)'",
        }
        
    )
]
    
SecondLevelEstimator_input_spec = SpecInfo(
    name="SecondLevelEstimatorInputSpec",
    fields=SecondLevelEstimator_input_fields,
    bases=(BaseSpec,),
)



SecondLevelEstimator_output_fields = [
    (
        "contrast_metadata",
        list(dict), 
        {
            "help_string": "contrast metadata"
        }
    )
]
    
SecondLevelEstimator_output_spec = SpecInfo(
    name="SecondLevelEstimatorOutputSpec",
    fields=SecondLevelEstimator_output_fields,
    bases=(BaseSpec,),
)


class SecondLevelEstimatorInterface(FunctionTask):
    input_spec = SecondLevelEstimator_input_spec
    output_spec = SecondLevelEstimator_output_spec