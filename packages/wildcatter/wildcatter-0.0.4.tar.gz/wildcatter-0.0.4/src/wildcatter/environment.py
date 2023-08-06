"""Driller environment module."""


from __future__ import annotations

import random
from typing import Any

import numpy as np
from gym import Env
from gym.spaces import Box
from gym.spaces import Discrete
from numpy.typing import NDArray


class SimpleDriller(Env):  # type: ignore
    """Simple driller environment."""

    def __init__(self, env_config: dict[str, Any]) -> None:
        """Initialize environment with config dictionary."""
        self.model = np.loadtxt(
            env_config["model_path"],
            delimiter=env_config["delim"],
        )

        self.nrow, self.ncol = self.model.shape
        self.available_pipe = env_config["available_pipe"]

        self.production = 0
        self.pipe_used = 0
        self.trajectory: list[list[int]] = []
        self.bit_location: list[int] = []

        self.action_space = Discrete(4)

        self.observation_space = Box(
            low=0, high=1, shape=(self.nrow, self.ncol), dtype="bool"
        )
        self.reset()

    def step(  # noqa: C901
        self, action: int
    ) -> tuple[NDArray[np.bool_], int, bool, dict[str, Any]]:
        """Take step based on action."""
        actions = {
            0: [1, 0],  # down
            1: [0, -1],  # left
            2: [0, 1],  # right
            3: [-1, 0],  # up
        }

        def take_action(loc: list[int], action: int) -> tuple[list[int], bool]:
            """Convenience function for taking action."""
            available_actions = list(actions.keys())
            stuck = False

            if loc[0] <= 1:
                available_actions.remove(3)

            if loc[0] == (self.nrow - 1):
                available_actions.remove(0)

            if loc[1] == 0:
                available_actions.remove(1)

            if loc[1] == (self.ncol - 1):
                available_actions.remove(2)

            if action not in available_actions:
                action = random.choice(available_actions)  # noqa: S311

            available_actions.remove(action)
            change = actions[action]
            new_location = [old + new for old, new in zip(loc, change)]

            if new_location in self.trajectory:
                collision = True
                while collision:
                    try:
                        new_action = random.choice(available_actions)  # noqa: S311
                    except IndexError:
                        stuck = True
                        break

                    try:
                        available_actions.remove(new_action)  # noqa: S311
                    except ValueError:
                        stuck = True
                        break

                    change = actions[new_action]
                    new_location = [old + new for old, new in zip(loc, change)]

                    if new_location not in self.trajectory:
                        collision = False

            return new_location, stuck

        new_location, stuck = take_action(self.bit_location, action)

        done = False
        if stuck:
            done = True
            reward = 0

        else:
            self.bit_location = new_location

            self.trajectory.append(new_location)
            newrow, newcol = new_location

            reward = self.model[newrow, newcol]

            self.update_state()

            self.pipe_used += 1

            if self.pipe_used == self.available_pipe:
                done = True

        info: dict[str, Any] = {}

        return self.state, reward, done, info

    def update_state(self) -> None:
        """Update state method."""
        traj_i, traj_j = np.asarray(self.trajectory).T
        self.state[traj_i, traj_j] = 1

    def render(self) -> None:
        """Gym environment rendering."""
        raise NotImplementedError("No renderer implemented yet.")

    def reset(self) -> NDArray[np.bool_]:
        """Reset the status of the environment."""
        self.surface_hole_location = [1, random.randint(0, self.ncol - 1)]  # noqa: S311
        self.state = np.zeros((self.nrow, self.ncol), dtype=bool)
        self.bit_location = self.surface_hole_location
        self.trajectory = [self.surface_hole_location]
        self.pipe_used = 0
        return self.state
