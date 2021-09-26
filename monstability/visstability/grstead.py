"""
Модуль расчета устойчивости и формирования сигналов отклонений
Допущения:
    Граф устойчивости направленный.
    Обход графа начинается с узлов метрик.
    Ребра имеют веса.

Ограничения:
    Узлы графа содержат атрибуты:
        'type':string - тип узла
            'metric' - узел метрики
            'service' - узел сервиса
            'and' - узел логического И
            'or' - узел логического ИЛИ
            'true' - узел единичной функции (доступность всегда 1)
        'access':integer - текущая доступность
        'stead':float - текущая устойчивость
        'costdown':float - текущая стоимость простоя
    Ребра графа содержат свойство:
        'weight':float - вес ребра (коэффициент передачи сигнала)
    Узлы типа 'metric', 'service', 'true' могут иметь только одно входящее ребро
"""

import networkx as nx

TYPE_METRIC = 'metric'
TYPE_SERVICE = 'service'
TYPE_AND = 'and'
TYPE_OR = 'or'


class GStead:
    """ Класс графа устойчивости """

    G = None    # граф класса

    def __init__(self):
        self.G = nx.DiGraph()


    def read_gexf(self, path):
        """ загрузка графа из файла GEXF """
        self.G = nx.read_gexf(path)


    def write_gexf(self, path):
        """ выгрузка графа в файла GEXF """
        nx.write_gexf(self.G, path)


    def calc_node_stead(self, node_id):
        """ пересчет устойчивости узла """

        edge_list = list(nx.edge_bfs(self.G, node_id))  # обход в ширину для узла node
        for u, v in edge_list:  # перебор всех ребер текущего узла
            self._calc_stead(node_id=v)     # расчитываем устойчивость узла на конце ребра
            self._calc_access(node_id=v)    # расчитываем доступность узла на конце ребра


    def calc_RTORPO(self, node_id):
        """ функция расчета RTO, RPO в зависимых узлах"""
        lst_out_edges = list(self.G.out_edges(node_id)) # список исходящих ребер
        if len(lst_out_edges) > 0:    # обновление RTO, RPO текущего узла если у него есть входящие ребра
            minRTO = self.G.nodes[lst_out_edges[0][1]]['RTO']
            minRPO = self.G.nodes[lst_out_edges[0][1]]['RPO']
            for u, v in lst_out_edges:
                if self.G.nodes[v]['RTO'] < minRTO:
                    minRTO = self.G.nodes[v]['RTO']  # минимальное значение RTO исходящих узлов
                if self.G.nodes[v]['RPO'] < minRPO:
                    minRPO = self.G.nodes[v]['RPO']  # минимальное значение RPO исходящих узлов

            self.G.nodes[node_id]['RTO'] = minRTO
            self.G.nodes[node_id]['RPO'] = minRPO

        lst_in_edges = list(self.G.in_edges(node_id))  # список входящих ребер
        for u, v in lst_in_edges:   # рекурсивный вызов расчета для узлов входящих ребер
            self.calc_RTORPO(u)


    def calc_costdown(self, node_id):
        """ функция расчета стоимости простоя в зависимых узлах"""

        lst_out_edges = list(self.G.out_edges(node_id)) # список исходящих ребер
        if len(lst_out_edges) > 0:    # обновление стоимости простоя текущего узла если у него есть входящие ребра
            costdown = 0
            for u, v in lst_out_edges:
                if self.G.nodes[v]['type'] == TYPE_OR:
                    costdown += self.G.nodes[v]['costdown'] * self.G[u][v]['weight']  # ИЛИ сумма делится в соответствии с весами
                else:
                    costdown += self.G.nodes[v]['costdown'] # для остальных И сумма равна для всех узлов

            self.G.nodes[node_id]['costdown'] = costdown

        lst_in_edges = list(self.G.in_edges(node_id))  # список входящих ребер
        for u, v in lst_in_edges:   # рекурсивный вызов расчета для узлов входящих ребер
            self.calc_costdown(u)


    def calc_metrics_stead(self):
        """ пересчет устойчивости по всем нодам метрик"""

        nodesid_metric = []  # список узлов с метриками
        for node in self.G.nodes.data():    # обход по вершинам графа
            if node[1]['type'] == TYPE_METRIC:    # если тип ноды 'metric'
                nodesid_metric.append(node[0])   # добавляем id ноды в список узлов метрик

        for node_id in nodesid_metric:
            self.calc_node_stead(node_id)   # выполняем расчет с обходом в ширину по всем узлам метрик


    def _calc_stead(self, node_id):
        """ функция расчета устойчивости ноды """

        lst_in_edges = list(self.G.in_edges(node_id))   # список входящих ребер
        stead = 0;
        for u,v in lst_in_edges:
            stead += self.G.nodes[u]['stead'] * self.G[u][v]['weight']  # сумма устойчивости входящих узлов умноженный на вес ребра
        self.G.nodes[node_id]['stead'] = stead  # обновление устойчивости текущего узла

    def _calc_access(self, node_id):
        """ функция расчета доступности ноды """
        lst_in_edges = list(self.G.in_edges(node_id))   # список входящих ребер
        access = 1;
        for u,v in lst_in_edges:
            if self.G.nodes[v]['type'] == TYPE_OR:
                access = access or self.G.nodes[u]['access']    # ИЛИ доступностей входящих узлов
            else:
                access = access and self.G.nodes[u]['access']   # И доступностей входящих узлов для других узлов
        self.G.nodes[node_id]['access'] = access  # обновление доступности текущего узла


if __name__ == '__main__':
    pass
