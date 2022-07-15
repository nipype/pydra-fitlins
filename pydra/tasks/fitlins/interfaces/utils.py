"""
TODO: need IOBase, DynamicTraitedSpec, add_traits, 
"""
from nipype.interfaces.io import IOBase, add_traits
from pydra.engine.specs import File, SpecInfo, BaseSpec
from pydra.engine.task import FunctionTask


class MergeAll(IOBase):
    input_spec = BaseSpec
    output_spec = BaseSpec

    def __init__(self, fields=None, check_lengths=True):
        super(MergeAll, self).__init__()
        self._check_lengths = check_lengths
        self._lengths = None
        if not fields:
            raise ValueError("Fields must be a non-empty list")

        self._fields = fields
        add_traits(self.inputs, fields)

    def _add_output_traits(self, base):
        return add_traits(base, self._fields)

    def _calculate_length(self, val):
        _lengths = list(map(len, val))
        if self._lengths is None:
            self._lengths = _lengths
        elif _lengths != self._lengths:
            raise ValueError("List lengths must be consistent across fields")
        self._lengths = _lengths

    def _list_outputs(self):
        outputs = self._outputs().get()
        for key in self._fields:
            val = getattr(self.inputs, key)
            # Allow for empty inputs
            if val not in [None, attr.NOTHING]:
                if self._check_lengths is True:
                    self._calculate_length(val)
                outputs[key] = [elem for sublist in val for elem in sublist]
        self._lengths = None

        return outputs

    
CollateWithMetadata_input_fields = [
    (
        "metadata",
        list,
        {
            "help_string": "metadata",
        },
    ),
    (
        "field_to_metadata_map",
        dict,
        {
            "help_string": "field to metadata map",
        },
    ),
]
    
CollateWithMetadata_input_spec = SpecInfo(
    name="CollateWithMetadataInputSpec",
    fields=CollateWithMetadata_input_fields,
    bases=(BaseSpec,),
)


CollateWithMetadata_output_fields = [
    (
        "metadata",
        list,
        {
            "help_string": "metadata",
        },
    ),
    (
        "out",
        list,
        {
            "help_string": "output",
        },
    ),
]

CollateWithMetadata_output_spec = SpecInfo(
    name="CollateWithMetadataOutputSpec",
    fields=CollateWithMetadata_output_fields,
    bases=(BaseSpec,),
)


class CollateWithMetadata(FunctionTask):
    input_spec = CollateWithMetadata_input_spec
    output_spec = CollateWithMetadata_output_spec

    def __init__(self, fields=None, **kwargs):
        super(CollateWithMetadata, self).__init__(**kwargs)
        if not fields:
            fields = self.inputs.field_to_metadata_map.keys()
            if not fields:
                raise ValueError("Fields must be a non-empty list")

        self._fields = fields
        add_traits(self.inputs, fields)

    def _run_interface(self, runtime):
        orig_metadata = self.inputs.metadata
        md_map = self.inputs.field_to_metadata_map
        n = len(orig_metadata)

        self._results.update({'metadata': [], 'out': []})
        for key in self._fields:
            val = getattr(self.inputs, key)
            # Allow for missing values
            if val not in [None, attr.NOTHING]:
                if len(val) != n:
                    raise ValueError(f"List lengths must match metadata. Failing list: {key}")
                for md, obj in zip(orig_metadata, val):
                    metadata = md.copy()
                    metadata.update(md_map.get(key, {}))
                    self._results['metadata'].append(metadata)
                    self._results['out'].append(obj)

        return 