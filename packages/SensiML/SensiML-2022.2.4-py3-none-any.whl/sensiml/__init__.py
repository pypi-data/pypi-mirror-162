from sensiml.client import Client
from sensiml.client import Client as SensiML

__all__ = ["SensiML", "Client"]


try:
    from IPython.core.display import HTML

    display(HTML("<style>.container { width:90% !important; }</style>"))
except:
    pass

name = "sensiml"
__version__ = "2022.2.4"
