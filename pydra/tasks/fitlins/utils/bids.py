import os
import json
import warnings
import copy
from itertools import chain

class BIDSError(ValueError):
    def __init__(self, message, bids_root):
        indent = 10
        header = '{sep} BIDS root folder: "{bids_root}" {sep}'.format(
            bids_root=bids_root, sep=''.join(['-'] * indent)
        )
        self.msg = '\n{header}\n{indent}{message}\n{footer}'.format(
            header=header,
            indent=''.join([' '] * (indent + 1)),
            message=message,
            footer=''.join(['-'] * len(header)),
        )
        super(BIDSError, self).__init__(self.msg)
        self.bids_root = bids_root


class BIDSWarning(RuntimeWarning):
    pass


def load_all_specs(all_specs, specs, node, **filters):
    if node.level == 'run':
        specs = node.run(group_by=node.group_by, force_dense=False)
    else:
        contrasts = list(chain(*[s.contrasts for s in specs]))
        specs = node.run(contrasts, group_by=node.group_by, **filters)

    all_specs[node.name] = specs
    for child in node.children:
        load_all_specs(all_specs, specs, child.destination, **child.filter)


def collect_participants(layout, participant_label=None, strict=False):
    """
    List the participants under the BIDS root and checks that participants
    designated with the participant_label argument exist in that folder.
    Returns the list of participants to be finally processed.
    Requesting all subjects in a BIDS directory root:
    TODO: ADD DOCTEST
    """
    all_participants = sorted(layout.get_subjects())

    # Error: bids_dir does not contain subjects
    if not all_participants:
        raise BIDSError(
            'Could not find participants. Please make sure the BIDS data '
            'structure is present and correct. Datasets can be validated online '
            'using the BIDS Validator (http://incf.github.io/bids-validator/).\n'
            'If you are using Docker for Mac or Docker for Windows, you '
            'may need to adjust your "File sharing" preferences.',
            layout.root,
        )

    # No --participant-label was set, return all
    if not participant_label:
        return all_participants

    # Drop sub- prefixes
    participant_label = [sub[4:] if sub.startswith('sub-') else sub for sub in participant_label]

    found_label = sorted(layout.get_subjects(subject=participant_label))

    if not found_label:
        raise BIDSError(
            'Could not find participants [{}]'.format(', '.join(participant_label)), layout.root
        )

    # Warn if some IDs were not found
    notfound_label = sorted(set(participant_label) - set(found_label))
    if notfound_label:
        exc = BIDSError(
            'Some participants were not found: {}'.format(', '.join(notfound_label)), layout.root
        )
        if strict:
            raise exc
        warnings.warn(exc.msg, BIDSWarning)

    return found_label


def write_derivative_description(bids_dir, deriv_dir, args):
    from .. import __version__
    from pathlib import Path

    def _clean_relative(item):
        """Turn absolute paths into relative paths"""
        try:
            p = Path(item)
            c = f"../{p.stem}"
        except:
            c = item
        return c

    # Clean up args
    out_args = {}
    for k, v in args.items():
        if k in ['bids_dir', 'output_dir', 'model', 'derivatives', 'work_dir']:
            if isinstance(v, list):
                v = [_clean_relative(i) for i in v]
            else:
                v = _clean_relative(v)
        out_args[k] = v

    desc = {
        'Name': 'Fitlins output',
        'BIDSVersion': '1.1.0',
        'PipelineDescription': {
            'Name': 'FitLins',
            'Version': __version__,
            'CodeURL': 'https://github.com/poldracklab/fitlins',
            'Parameters': out_args,
        },
        'CodeURL': 'https://github.com/poldracklab/fitlins',
        'HowToAcknowledge': 'https://github.com/poldracklab/fitlins',
    }

    # Keys that can only be set by environment
    if 'FITLINS_DOCKER_TAG' in os.environ:
        desc['DockerHubContainerTag'] = os.environ['FITLINS_DOCKER_TAG']
    if 'FITLINS_SINGULARITY_URL' in os.environ:
        singularity_url = os.environ['FITLINS_SINGULARITY_URL']
        desc['SingularityContainerURL'] = singularity_url
        try:
            desc['SingularityContainerMD5'] = _get_shub_version(singularity_url)
        except ValueError:
            pass

    # Keys deriving from source dataset
    fname = os.path.join(bids_dir, 'dataset_description.json')
    if os.path.exists(fname):
        with open(fname) as fobj:
            orig_desc = json.load(fobj)
    else:
        orig_desc = {}

    if 'DatasetDOI' in orig_desc:
        desc['SourceDatasetsURLs'] = ['https://doi.org/{}'.format(orig_desc['DatasetDOI'])]
    if 'License' in orig_desc:
        desc['License'] = orig_desc['License']

    with open(os.path.join(deriv_dir, 'dataset_description.json'), 'w') as fobj:
        json.dump(desc, fobj, indent=2)


def _get_shub_version(singularity_url):
    raise ValueError("Not yet implemented")