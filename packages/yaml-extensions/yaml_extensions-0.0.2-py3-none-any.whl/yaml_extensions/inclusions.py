#  Copyright 2022- Carl Zeiss AG

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from io import IOBase
from pathlib import Path
from typing import Optional, Any

import yaml


class _InclusionBase:
    """
    Base class for inclusion loaders.

    This class helps track the directory with respect to which inclusions
    should be considered.

    Args:
        reference_directory: If set, a directory to prepend to inclusion paths
            (otherwise, current working directory is used or including file's
            location if determinable)

    """

    reference_directory: Optional[Path] = None

    def __init__(self, stream):
        super().__init__(stream)

        if isinstance(stream, IOBase):
            try:
                reference_directory = Path(stream.name).parent
                if reference_directory.exists():
                    self.reference_directory = reference_directory
            except AttributeError:
                pass

    @staticmethod
    def load_inclusion(ldr, node) -> Any:
        """
        Constructor for `!include` tags.

        These tags are not defined by the YAML specification, but can be added
        without violating the spec. They are assumed to follow the pattern:

        ```yaml
        fizz: !include "my_other.yaml"
        ```

        Args:
            ldr: Loader as passed by PyYAML.
            node: The node to replace with the loaded content.

        Returns:
            Anything that could be returned from the loader this extends.

        """
        reference_directory = ldr.reference_directory or Path.cwd()

        location = reference_directory / ldr.construct_scalar(node)

        with open(location, "r") as inclusion_fp:
            inner = yaml.load(inclusion_fp, Loader=type(ldr))
            return inner


class InclusionSafeLoader(_InclusionBase, yaml.SafeLoader):
    pass


class InclusionLoader(_InclusionBase, yaml.Loader):
    pass


InclusionLoader.add_constructor("!include", InclusionLoader.load_inclusion)

InclusionSafeLoader.add_constructor(
    "!include", InclusionSafeLoader.load_inclusion
)
