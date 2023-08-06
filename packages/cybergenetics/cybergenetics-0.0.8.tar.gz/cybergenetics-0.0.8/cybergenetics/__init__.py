__version__ = '0.0.5'

from gym.envs.registration import register

register(
    id='CRN-v0',
    entry_point='cybergenetics.envs.crn:CRNWrapper',
)
