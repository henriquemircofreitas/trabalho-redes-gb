"""Digital transmission simulator: ASCII text -> line code -> modulation -> channel -> BER."""

from sim.link import LinkResult, run_link

__all__ = ["LinkResult", "run_link"]
__version__ = "1.0.0"
