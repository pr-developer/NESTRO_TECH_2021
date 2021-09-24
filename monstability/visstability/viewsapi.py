from rest_framework import views, viewsets, authentication
from rest_framework.response import Response

from .models import Nodes, Edges
from .serializers import NodesSerializer, EdgesSerializer, NodesViewSerializer, EdgesViewSerializer

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

##### Nodes and Edges #####
class NodesListView(views.APIView):
    """Nodes and Edges"""

    def get(self, request, format=None, **kwargs):
        nodeslst = Nodes.objects.all()
        nodes_serializer = NodesViewSerializer(nodeslst, many=True)
        edgeslst = Edges.objects.all()
        edges_serializer = EdgesViewSerializer(edgeslst, many=True)

        return Response({
            "class": "GraphLinksModel",
            'nodeDataArray': nodes_serializer.data,
            'linkDataArray': edges_serializer.data,
        })
