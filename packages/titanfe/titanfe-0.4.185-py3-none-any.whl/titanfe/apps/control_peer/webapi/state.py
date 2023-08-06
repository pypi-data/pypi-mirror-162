# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Routes for Flow management"""

from functools import partial
from typing import List, Dict

from fastapi import APIRouter


def create_state_router(control_peer):
    """Create a router for state

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Returns:
        APIRouter: router/routes to manage the control peer's flows
    """

    router = APIRouter()
    router.add_api_route("/", partial(get_state, control_peer))
    return router


def get_state(control_peer) -> List[Dict]:
    """Create a router for state

    Arguments:
        control_peer (ControlPeer): an instance of the ControlPeer

    Returns:
        list of brick information
    """
    def brick_info(runner):
        brick = runner.brick
        return {
            "runner": runner.uid,
            "flow": brick.flow.uid,
            "uid": brick.uid,
            "name": brick.name,
        }

    return [brick_info(runner) for runner in control_peer.runners.values()]
