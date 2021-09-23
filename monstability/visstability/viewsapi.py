from rest_framework import viewsets, authentication

from .models import Nodes, Edges
from .serializers import NodesSerializer, EdgesSerializer
#from .permissions import ObjectPermissions

##### Nodes #####
class NodesViewSet(viewsets.ModelViewSet):
    """Nodes"""

    #permission_classes = [ObjectPermissions, ]
    serializer_class = NodesSerializer
    queryset = Nodes.objects.order_by('id')
    lookup_field = 'id_gr'


##### Edges #####
class EdgesViewSet(viewsets.ModelViewSet):
    """Edges"""

    #permission_classes = [ObjectPermissions, ]
    serializer_class = EdgesSerializer
    queryset = Edges.objects.order_by('id')
    lookup_field = 'id_gr'
