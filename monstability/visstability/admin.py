from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin import helpers
from django.conf import settings
import os

from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import Nodes, Edges, TestCaseNodes
from .grstead import GStead

FILE_MODEL = 'monstability_model.xml'

class TestCaseNodesResource(resources.ModelResource):
    """Класс для импорта тест-кейса"""

    class Meta:
        model = TestCaseNodes
        fields = ('id', 'id_gr', 'access', 'stead', 'costdown', 'RTO', 'RPO',)

class NodesResource(resources.ModelResource):
    """Класс для импорта Nodes"""

    class Meta:
        model = Nodes
        fields = ('id', 'id_gr', 'type_gr', 'label_gr', 'layer', 'access', 'stead', 'costdown', 'coordX', 'coordY',
                  'RTO', 'RPO', 'color')

class EdgesResource(resources.ModelResource):
    """Класс для импорта Edges"""

    class Meta:
        model = Edges
        fields = ('id', 'id_gr', 'source', 'target', 'weight', 'color')


def grget_model(AG):
    ''' загрузка графа из базы данных '''
    qrND = Nodes.objects.all()
    for ND in qrND:
        AG.add_node(
            ND.id_gr,
            type=ND.type_gr,
            label=ND.label_gr,
            layer=ND.layer,
            access=ND.access,
            stead=ND.stead,
            costdown=ND.costdown,
            coordX=ND.coordX,
            coordY=ND.coordY,
            RTO=ND.RTO,
            RPO=ND.RPO,
            color=ND.color,
        )
    qrNE = Edges.objects.all()
    for NE in qrNE:
        AG.add_edge(
            NE.source,
            NE.target,
            weight=NE.weight,
            id=NE.id_gr,
            color=NE.color,
        )


def grput_model(AG):
    ''' выгрузка графа в базу данных '''
    if len(AG) > 0:
        Nodes.objects.all().delete()
        for node in AG.nodes.data():
            ND = Nodes.objects.create(
                id_gr=node[0],
                label_gr=node[1]['label'],
                type_gr=node[1]['type'],
                layer=node[1]['layer'],
                access=node[1]['access'],
                stead=node[1]['stead'],
                costdown=node[1]['costdown'],
                coordX=node[1]['coordX'],
                coordY=node[1]['coordY'],
                RTO=node[1]['RTO'],
                RPO=node[1]['RPO'],
                color=node[1]['color'],
            )
            ND.save()

        Edges.objects.all().delete()
        for edge in AG.edges.data():
            NE = Edges.objects.create(
                source=edge[0],
                target=edge[1],
                id_gr=edge[2]['id'],
                weight=edge[2]['weight'],
                color=edge[2]['color'],
            )
            NE.save()


@admin.register(Nodes)
class NodesAdmin(ImportExportModelAdmin):
    resource_class = NodesResource
    list_display = ('id', 'id_gr', 'label_gr', 'type_gr', 'layer', 'access', 'stead', 'costdown', 'color',)
    list_filter = ('type_gr', 'layer',)
    list_display_links = ('id_gr',)
    actions = ['grload_model', 'grsave_model', 'grcalc_model', 'grcalc_costdown']

    def changelist_view(self, request, extra_context=None):
        ''' эмуляция выбора всех элементов списка '''

        if 'action' in request.POST and request.POST['action'] in ('grload_model', 'grsave_model', ):
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Nodes.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(u.id)})
                request._set_post(post)
        return super(ImportExportModelAdmin, self).changelist_view(request, extra_context)

    def grload_model(self, request, queryset):
        ''' загрузка графа из файла GEXF '''
        gr = GStead()
        gr.read_gexf(os.path.join(settings.STATIC_DIR, FILE_MODEL))
        grput_model(gr.G)
    grload_model.short_description = 'Загрузить модель из GEXF файла'

    def grsave_model(self, request, queryset):
        ''' сохранение графа в файл GEXF '''
        gr = GStead()
        grget_model(gr.G)
        gr.write_gexf(os.path.join(settings.STATIC_DIR, FILE_MODEL))
    grsave_model.short_description = 'Сохранить модель в GEXF файл'

    def grcalc_model(self, request, queryset):
        ''' пересчет показателей устойчивости '''
        gr = GStead()
        grget_model(gr.G)
        for node in queryset:
            gr.calc_node_stead(node_id=node.id_gr)
        grput_model(gr.G)
    grcalc_model.short_description = 'Пересчитать показатели'

    def grcalc_costdown(self, request, queryset):
        ''' пересчет показателей доступности '''
        gr = GStead()
        grget_model(gr.G)
        for node in queryset:
            gr.calc_costdown(node_id=node.id_gr)
        grput_model(gr.G)
    grcalc_costdown.short_description = 'Пересчитать стоимость простоя'


@admin.register(Edges)
class EdgesAdmin(ImportExportModelAdmin):
    resource_class = EdgesResource
    list_display = ('id_gr', 'source', 'target', 'weight', 'color',)
    list_display_links = ('id_gr', 'source',)
#    list_filter = ('source', 'target',)


@admin.register(TestCaseNodes)
class TestCaseNodesAdmin(ImportExportModelAdmin):
    resource_class = TestCaseNodesResource
    list_display = ('id', 'id_gr', 'access', 'stead', 'costdown')
    list_display_links = ('id_gr',)
