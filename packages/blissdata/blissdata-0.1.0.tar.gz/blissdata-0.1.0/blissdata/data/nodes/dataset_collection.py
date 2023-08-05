# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from blissdata.data.nodes.dataset import _DataPolicyNode


class DatasetCollectionNode(_DataPolicyNode):
    _NODE_TYPE = "dataset_collection"
